import re
from typing import Tuple, Dict, Any

class GuardrailChecker:
    """
    Ensures SetuX AI Assistant ONLY responds to SetuX services (New ID Applications, Document Updates, & Site Navigation).
    AI Bot Created by jitin.io.
    """
    
    ALLOWED_KEYWORDS = [
        # English terms for Update, New ID Application & Navigation
        "aadhaar", "aadhar", "uidai", "myaadhaar",
        "pan", "pancard", "nsdl", "protean", "utitsl", "epan", "new pan", "apply pan", "create pan",
        "ration", "rationcard", "epds", "nfsa", "bpl", "apl",
        "voter", "voterid", "epic", "nvsp", "election card", "new voter", "apply voter", "create voter",
        "driving license", "license", "licence", "parivahan", "rto", "dl",
        "passport", "ayushman", "document", "documents", "id", "card", "new id", "apply", "create", "register",
        "update", "correction", "correct", "change", "address", "name", "dob",
        "date of birth", "mobile", "phone", "link", "photo", "biometric",
        "member", "family", "proof", "fee", "cost", "charge", "kendra", "setux", "jitin.io", "jitin",
        "status", "process", "form", "certificate", "portal", "site", "how to use", "navigation", "flowchart", "roadmap",
        
        # Hindi & Marathi (Devanagari) terms
        "आधार", "पैन", "पॅन", "राशन", "रेशन", "वोटर", "मतदार", "लायसन्स", "ड्राइविंग", "ड्रायव्हिंग",
        "नया", "नवीन", "बनाएं", "बनावणे", "अपडेट", "सुधार", "दुरुस्ती", "बदल", "बदला", "बदलायचे", "बदलना", "बदलायचा", "जोडणे",
        "नाम", "नाव", "पता", "पत्ता", "मोबाइल", "फोन", "जन्म", "तारिख", "फोटो", "कागदपत्रे", "दस्तावेज़",
        "शुल्क", "फीस", "फी", "प्रोसेस", "स्टेप्स", "रोडमैप", "कसे", "कैसे", "काय", "क्या", "सेतुएक्स", "सेतूएक्स"
    ]
    
    EXPLICIT_OFFTOPIC_PATTERNS = [
        r"\b(python|java|javascript|html|css|c\+\+|coding|code|function|program|script)\b",
        r"\b(weather|temperature|forecast|rain|climate)\b",
        r"\b(capital of|who is president|who is prime minister|tell me a joke|write a poem|essay|math|calculator|recipe|cook|cricket|football|movie|song)\b",
        r"\b(bitcoin|crypto|stock market|share price|invest|trading)\b"
    ]

    def is_query_allowed(self, user_query: str) -> Tuple[bool, str]:
        query_lower = user_query.strip().lower()
        
        if not query_lower:
            return False, "empty query"

        for pattern in self.EXPLICIT_OFFTOPIC_PATTERNS:
            if re.search(pattern, query_lower):
                return False, "off_topic"

        has_allowed_keyword = any(kw in query_lower for kw in self.ALLOWED_KEYWORDS)
        
        conversational_greetings = ["hi", "hello", "namaste", "hey", "help", "menu", "services", "kaise", "kya", "kase", "kay", "हा", "नमस्कार", "मदत", "who made you", "creator", "maker"]
        is_greeting = any(g in query_lower for g in conversational_greetings) and len(query_lower.split()) <= 4
        
        if has_allowed_keyword or is_greeting or len(query_lower.split()) <= 4:
            return True, "allowed"

        return True, "allowed"

    def get_polite_refusal(self, user_language: str = "English") -> str:
        refusals = {
            "Hindi": "क्षमा करें! मैं सेतुएक्स (SetuX) एआई सहायक हूँ। मैं केवल सेतुएक्स पोर्टल पर नए आईडी आवेदन, दस्तावेज़ अपडेट और साइट सहायता में मदद कर सकता हूँ।",
            "Marathi": "क्षमस्व! मी सेतूएक्स (SetuX) एआय सहाय्यक आहे. मी फक्त नवीन आयडी अर्ज आणि दस्तऐवज अद्ययावत सेवांसाठी मदत करू शकतो.",
            "Bengali": "ক্ষমা করবেন! আমি সেতুএক্স (SetuX) এআই সহকারী। আমি নতুন আইডি আবেদন ও নথি আপডেট সংক্রান্ত পরিষেবাতে সাহায্য করতে পারি।",
            "Tamil": "மன்னிக்கவும்! நான் சேதுஎக்ஸ் (SetuX) AI உதவியாளர்.",
            "Telugu": "క్షమించండి! నేను సేతుఎక్స్ (SetuX) AI సహాయకుడిని.",
            "Gujarati": "માફ કરશો! હું સેતુએક્સ (SetuX) AI સહાયક છું.",
            "English": "I apologize! I am SetuX AI Helper, specialized strictly in New ID Applications, Document Updates, & Site Guidance on SetuX."
        }
        return refusals.get(user_language, refusals["English"])
