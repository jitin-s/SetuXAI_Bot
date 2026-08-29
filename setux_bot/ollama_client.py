import requests
import json
import os
from typing import List, Dict, Any, Generator, Optional

class OllamaClient:
    def __init__(self, base_url: str = None, model_name: str = None):
        raw_groq = os.getenv("GROQ_API_KEY")
        self.groq_api_key = raw_groq.strip().strip('"').strip("'") if raw_groq else None
        self.base_url = (base_url or os.getenv("OLLAMA_BASE_URL") or "http://127.0.0.1:11434").rstrip("/")
        self.cpu_threads = max(1, (os.cpu_count() or 4) - 1)
        self.explicit_model = model_name
        self.model_name = model_name or self._select_best_model("English")

    def is_server_online(self) -> bool:
        if self.groq_api_key:
            return True
        try:
            res = requests.get(f"{self.base_url}/api/tags", timeout=3)
            return res.status_code == 200
        except Exception:
            return False

    def get_available_models(self) -> List[str]:
        if self.groq_api_key:
            return ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768", "gemma2-9b-it"]
        try:
            res = requests.get(f"{self.base_url}/api/tags", timeout=3)
            if res.status_code == 200:
                data = res.json()
                return [m.get("name") for m in data.get("models", [])]
        except Exception:
            pass
        return []

    def _select_best_model(self, target_language: str = "English") -> str:
        if self.groq_api_key:
            return "llama-3.3-70b-versatile"

        if self.explicit_model:
            return self.explicit_model
            
        available = self.get_available_models()
        if not available:
            return "qwen2.5-coder:latest"
            
        if target_language != "English":
            for m in available:
                if "coder" in m or "7b" in m or "8b" in m:
                    return m
                    
        for cand in ["qwen2.5:1.5b", "qwen2.5:0.5b", "llama3.2:1b", "qwen2.5-coder:latest"]:
            if cand in available or any(m.startswith(cand) for m in available):
                return next(m for m in available if m == cand or m.startswith(cand))
                
        return available[0] if available else "qwen2.5:1.5b"

    def _chat_groq_stream(self, messages: List[Dict[str, str]], model: str, temperature: float, max_tokens: int) -> Generator[str, None, None]:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json"
        }
        
        # Models to try in order of fallback
        models_to_try = [model, "llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"]
        
        for candidate_model in models_to_try:
            payload = {
                "model": candidate_model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": True
            }
            try:
                res = requests.post(url, json=payload, headers=headers, stream=True, timeout=30)
                if res.status_code == 200:
                    for line in res.iter_lines():
                        if line:
                            line_str = line.decode("utf-8")
                            if line_str.startswith("data: ") and line_str != "data: [DONE]":
                                try:
                                    chunk = json.loads(line_str.replace("data: ", ""))
                                    content = chunk.get("choices", [{}])[0].get("delta", {}).get("content", "")
                                    if content:
                                        yield content
                                except Exception:
                                    pass
                    return # Successfully streamed!
                else:
                    err_body = res.text[:200]
                    if candidate_model != models_to_try[-1]:
                        continue # Try next fallback model
                    yield f"\n[Error Groq API: Status {res.status_code} - {err_body}]"
                    return
            except Exception as e:
                yield f"\n[Error Groq Cloud Inference: {str(e)}]"
                return

    def chat_completion_stream(self, messages: List[Dict[str, str]], temperature: float = 0.1, max_tokens: int = 250, target_language: str = "English") -> Generator[str, None, None]:
        if self.groq_api_key:
            model = "llama-3.3-70b-versatile"
            yield from self._chat_groq_stream(messages, model, temperature, max_tokens)
            return

        url = f"{self.base_url}/api/chat"
        active_model = self._select_best_model(target_language)
        
        payload = {
            "model": active_model,
            "messages": messages,
            "stream": True,
            "options": {
                "temperature": temperature,
                "top_p": 0.8,
                "num_predict": max_tokens,
                "num_ctx": 1024 if active_model != "qwen2.5:1.5b" else 512,
                "num_thread": self.cpu_threads
            }
        }
        
        try:
            res = requests.post(url, json=payload, stream=True, timeout=120)
            if res.status_code == 200:
                for line in res.iter_lines():
                    if line:
                        chunk = json.loads(line.decode("utf-8"))
                        content = chunk.get("message", {}).get("content", "")
                        if content:
                            yield content
            else:
                yield f"\n[Error: Ollama returned status code {res.status_code}]"
        except requests.exceptions.Timeout:
            yield "\n[Error: Local LLM request timed out.]"
        except requests.exceptions.ConnectionError:
            yield "\n[Error: Cannot connect to Ollama server. Check OLLAMA_BASE_URL or GROQ_API_KEY env variables.]"
        except Exception as e:
            yield f"\n[Error communicating with LLM: {str(e)}]"

    def chat_completion(self, messages: List[Dict[str, str]], temperature: float = 0.1, max_tokens: int = 250, target_language: str = "English") -> str:
        tokens = list(self.chat_completion_stream(messages, temperature=temperature, max_tokens=max_tokens, target_language=target_language))
        return "".join(tokens).strip()
