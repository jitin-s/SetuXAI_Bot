import json
import os
import re
from typing import List, Dict, Any, Tuple, Generator
from .guardrails import GuardrailChecker
from .ollama_client import OllamaClient
from .scanner import WebsiteScanner

class SetuXBotEngine:
    def __init__(self, model_name: str = None, kb_path: str = None, memory_path: str = None):
        if kb_path is None:
            kb_path = os.path.join(os.path.dirname(__file__), "knowledge_base.json")
        if memory_path is None:
            memory_path = os.path.join(os.path.dirname(__file__), "learned_memory.json")
            
        self.bot_maker = "jitin.io"
        self.kb_path = kb_path
        self.memory_path = memory_path
        self.kb_data = self._load_json(self.kb_path)
        self.learned_memory = self._load_json(self.memory_path, default={"scanned_websites": {}, "custom_facts": []})
        self.guardrails = GuardrailChecker()
        self.scanner = WebsiteScanner()
        self.ollama = OllamaClient(model_name=model_name)
        self.conversation_history: List[Dict[str, str]] = []

    def _load_json(self, path: str, default: Dict[str, Any] = None) -> Dict[str, Any]:
        if default is None:
            default = {}
        try:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"[Warning] Failed to load JSON {path}: {e}")
        return default

    def _save_learned_memory(self):
        try:
            with open(self.memory_path, 'w', encoding='utf-8') as f:
                json.dump(self.learned_memory, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[Warning] Failed to save learned memory: {e}")

    def learn_from_website_url(self, url: str) -> Dict[str, Any]:
        scan_result = self.scanner.scan_url(url)
        if scan_result.get("success"):
            cleaned_url = scan_result["url"]
            self.learned_memory["scanned_websites"][cleaned_url] = {
                "title": scan_result["title"],
                "content": scan_result["content"],
                "scanned_at": str(os.path.getmtime(self.memory_path) if os.path.exists(self.memory_path) else "")
            }
            self._save_learned_memory()
        return scan_result

    def learn_from_dom_payload(self, url: str, title: str, raw_text: str) -> Dict[str, Any]:
        scan_result = self.scanner.scan_page_payload(url, title, raw_text)
        if scan_result.get("success"):
            self.learned_memory["scanned_websites"][url] = {
                "title": title,
                "content": scan_result["content"],
                "source": "embedded_js_widget"
            }
            self._save_learned_memory()
        return scan_result

    def learn_custom_fact(self, fact: str, response: str) -> Dict[str, Any]:
        item = {"fact": fact, "response": response}
        self.learned_memory["custom_facts"].append(item)
        self._save_learned_memory()
        return {"success": True, "fact": item}

    def _check_developer_attribution(self, query: str, language: str) -> str:
        q_lower = query.lower()
        creator_keywords = [
            "who created you", "who created u", "who made you", "who built you",
            "who is your developer", "who designed you", "who developed you", "who programmed you",
            "किसने बनाया", "किसने डेवलप किया", "कोण बनवले", "बनावणार कोण", "का बनाए हैं", "बनाने वाले का नाम"
        ]
        
        if any(kw in q_lower for kw in creator_keywords):
            responses = {
                "Hindi": "मुझे jitin.io द्वारा बनाया गया है।",
                "Marathi": "मला jitin.io द्वारे तयार केले गेले आहे.",
                "Bengali": "আমাকে jitin.io দ্বারা তৈরি করা হয়েছে।",
                "Tamil": "நான் jitin.io ஆல் உருவாக்கப்பட்டேன்.",
                "Telugu": "నేను jitin.io ద్వారా తయారు చేయబడ్డాను.",
                "Gujarati": "મને jitin.io દ્વારા બનાવવામાં આવ્યો છે.",
                "English": "I was created by jitin.io."
            }
            return responses.get(language, "I was created by jitin.io.")
        return ""

    def _retrieve_relevant_kb_context(self, user_query: str) -> str:
        query_lower = user_query.lower()
        matched_context = []

        services = self.kb_data.get("services", {})

        general_keywords = ["services", "plans", "facility", "facilities", "offer", "options", "menu", "cost", "pricing", "fees", "list", "सेवा", "सुविधा", "प्लान"]
        is_general_query = any(gw in query_lower for gw in general_keywords) and not any(doc in query_lower for doc in ["driving", "license", "licence", "dl", "passport", "pan", "aadhaar", "aadhar", "ration", "voter", "ayushman"])

        if is_general_query and "setux_overview" in services:
            overview_categories = services["setux_overview"].get("categories", {})
            for cat_id, cat_info in overview_categories.items():
                title = cat_info.get("title", "")
                process = cat_info.get("process", "")
                fee = cat_info.get("fee", "")
                matched_context.append(f"• Service: {title}\n  Process: {process}\n  Fee: {fee}\n")
            return "SetuX Citizen Identification Document Services & Pricing Directory:\n\n" + "\n".join(matched_context)

        # 1. Search Core Knowledge Base
        for service_id, service_info in services.items():
            if service_id == "setux_overview":
                continue
                
            keywords = service_info.get("keywords", [])
            if any(kw.lower() in query_lower for kw in keywords):
                categories = service_info.get("categories", {})
                for cat_id, cat_info in categories.items():
                    if "address" in query_lower and "address" not in cat_id.lower() and "address" not in cat_info.get("title", "").lower():
                        continue
                    if ("mobile" in query_lower or "biometric" in query_lower or "phone" in query_lower) and "mobile" not in cat_id.lower() and "child" not in cat_id.lower():
                        continue
                    if ("name" in query_lower or "dob" in query_lower or "date of birth" in query_lower) and "name" not in cat_id.lower():
                        continue
                    if "new" in query_lower and "new" not in cat_id.lower():
                        continue

                    title = cat_info.get("title", "")
                    mode = cat_info.get("mode", "ONLINE")
                    offline_note = cat_info.get("offline_note", "")
                    flowchart = cat_info.get("flowchart", "")
                    process = cat_info.get("process", "")
                    docs = ", ".join(cat_info.get("required_documents", []))
                    fee = cat_info.get("fee", "N/A")
                    
                    category_text = f"### Service: {title}\n"
                    if mode == "ONLINE":
                        category_text += "✅ 100% Online Process\n\n"
                    else:
                        category_text += f"⚠️ Offline Visit Required ({offline_note})\n\n"
                        
                    category_text += f"Visual Flowchart Roadmap:\n{flowchart}\n\n"
                    category_text += f"SetuX Step-by-Step Procedure:\n{process}\n\n"
                    category_text += f"Required Proof Documents: {docs}\n"
                    category_text += f"SetuX Official Fee: {fee}\n"
                    matched_context.append(category_text)

        # 2. Search Learned Memory (Scanned Websites & Dynamic Facts)
        scanned_sites = self.learned_memory.get("scanned_websites", {})
        for site_url, site_data in scanned_sites.items():
            title = site_data.get("title", "")
            content = site_data.get("content", "")
            
            words = [w for w in query_lower.split() if len(w) > 3]
            if any(w in content.lower() or w in title.lower() for w in words):
                snippet = content[:1500]
                matched_context.append(f"Scanned Website Data ({site_url} - {title}):\n{snippet}\n")

        for item in self.learned_memory.get("custom_facts", []):
            if any(w in item.get("fact", "").lower() for w in query_lower.split() if len(w) > 3):
                matched_context.append(f"Learned Fact: {item['fact']} -> {item['response']}")

        if matched_context:
            return matched_context[0]
            
        return "SetuX Services: Apply New PAN Card (100% Online - ₹106), Apply New Driving License (Offline Test Visit - ₹250), Apply New Passport Assistance (Offline PSK Visit - ₹350), Apply New Voter ID (100% Online - ₹25), Aadhaar Address Update (100% Online - ₹50), Aadhaar Mobile Link (Offline Biometric Visit - ₹50)."

    def _sanitize_response(self, text: str) -> str:
        replacements = [
            (r"\b(official\s+govt\.?\s+website|official\s+government\s+website|government\s+portal|govt\s+portal|official\s+website|official\s+portal|national\s+highway\s+authority|nhai)\b", "SetuX Portal", re.IGNORECASE),
            (r"\b(uidai\s+website|uidai\s+portal|myaadhaar\s+portal)\b", "SetuX Aadhaar Services", re.IGNORECASE),
            (r"\b(nsdl\s+portal|protean\s+portal|utitsl\s+portal)\b", "SetuX PAN Services", re.IGNORECASE),
            (r"\b(parivahan\s+portal|rto\s+portal)\b", "SetuX Driving License Services", re.IGNORECASE),
            (r"\b(nvsp\s+portal|eci\s+portal|voter\s+helpline)\b", "SetuX Voter ID Services", re.IGNORECASE)
        ]
        sanitized = text
        for pattern, replacement, flags in replacements:
            sanitized = re.sub(pattern, replacement, sanitized, flags=flags)
        return sanitized

    def build_system_prompt(self, context_snippet: str, target_language: str = "English") -> str:
        language_instructions = {
            "Hindi": "MANDATORY SCRIPT & LANGUAGE: Write 100% in HINDI (हिन्दी) using Devanagari script. Do not use English script.",
            "Marathi": "MANDATORY SCRIPT & LANGUAGE: Write 100% in MARATHI (मराठी) using Devanagari script. Do not use English script.",
            "Bengali": "MANDATORY SCRIPT & LANGUAGE: Write 100% in BENGALI (বাংলা) using Bengali script. Do not use English script.",
            "Tamil": "MANDATORY SCRIPT & LANGUAGE: Write 100% in TAMIL (தமிழ்) using Tamil script. Do not use English script.",
            "Telugu": "MANDATORY SCRIPT & LANGUAGE: Write 100% in TELUGU (తెలుగు) using Telugu script. Do not use English script.",
            "Gujarati": "MANDATORY SCRIPT & LANGUAGE: Write 100% in GUJARATI (ગુજરાતી) using Gujarati script. Do not use English script.",
            "English": "MANDATORY SCRIPT & LANGUAGE: Write in English."
        }
        lang_rule = language_instructions.get(target_language, f"Write 100% in {target_language}.")

        return f"""You are SetuX AI Assistant.

PRIMARY GOAL:
ASSIST USERS WITH ACCURATE SETUX PLATFORM SERVICES AND INTEGRATED WEBSITE KNOWLEDGE.

{lang_rule}

STRICT RESPONSE RULES:
1. TRANSLATE ALL STEPS, PROOFS, AND FEES ENTIRELY IN THE REQUESTED SCRIPT ({target_language}).
2. FORMAT ROADMAPS AS VISUAL TEXT FLOWCHARTS ([Step 1] ➔ [Step 2] ➔ [Step 3] ➔ [Step 4]).
3. OFFLINE VISIT NOTICE:
   - If 100% Online, state: "✅ 100% Online Process".
   - If Offline Visit Required, state: "⚠️ Offline Visit Required" and explain SetuX Kendra Appointment / Doorstep Visit slot booking step!
4. DEVELOPER ATTRIBUTION RULE:
   - State "I was created by jitin.io" ONLY if explicitly asked who created/developed you. Do NOT mention jitin.io in standard document answers.

KNOWLEDGE BASE:
{context_snippet}
"""

    def process_query_stream(self, user_query: str, target_language: str = "English") -> Tuple[Generator[str, None, None], bool]:
        # 0. Check explicit developer attribution query
        dev_response = self._check_developer_attribution(user_query, target_language)
        if dev_response:
            def dev_yield():
                yield dev_response
            return dev_yield(), True

        # 1. Guardrail check
        is_allowed, reason = self.guardrails.is_query_allowed(user_query)
        if not is_allowed:
            refusal_msg = self.guardrails.get_polite_refusal(target_language)
            def single_yield():
                yield refusal_msg
            return single_yield(), False

        # 2. Retrieve KB Context
        kb_context = self._retrieve_relevant_kb_context(user_query)
        system_prompt = self.build_system_prompt(kb_context, target_language=target_language)
        
        messages = [{"role": "system", "content": system_prompt}]
        
        for msg in self.conversation_history[-2:]:
            messages.append(msg)
            
        messages.append({"role": "user", "content": user_query})

        # 3. Stream response with fallback to structured knowledge base if connection is pending
        def token_streamer():
            full_response = []
            has_tokens = False
            
            for token in self.ollama.chat_completion_stream(messages=messages, temperature=0.1, max_tokens=250, target_language=target_language):
                if token and not token.startswith("\n[Error"):
                    has_tokens = True
                full_response.append(token)
                yield token

            if not has_tokens:
                fallback_reply = f"\n\n{kb_context}"
                yield fallback_reply
                full_response.append(fallback_reply)

            raw_accumulated = "".join(full_response).strip()
            sanitized_accumulated = self._sanitize_response(raw_accumulated)
            
            if sanitized_accumulated:
                self.conversation_history.append({"role": "user", "content": user_query})
                self.conversation_history.append({"role": "assistant", "content": sanitized_accumulated})

        return token_streamer(), True

    def process_query(self, user_query: str, target_language: str = "English") -> Tuple[str, bool]:
        gen, is_allowed = self.process_query_stream(user_query, target_language=target_language)
        raw_text = "".join(list(gen))
        return self._sanitize_response(raw_text), is_allowed

    def clear_history(self):
        self.conversation_history.clear()
