import requests
import json
import os
from typing import List, Dict, Any, Generator, Optional

class OllamaClient:
    def __init__(self, base_url: str = None, model_name: str = None):
        raw_openrouter = os.getenv("OPENROUTER_API_KEY")
        raw_groq = os.getenv("GROQ_API_KEY")

        if raw_openrouter and raw_openrouter.strip() and raw_openrouter.strip().lower() not in ["none", "null", "false", "undefined"]:
            self.openrouter_api_key = raw_openrouter.strip().strip('"').strip("'")
        else:
            self.openrouter_api_key = None

        if raw_groq and raw_groq.strip() and raw_groq.strip().lower() not in ["none", "null", "false", "undefined"]:
            self.groq_api_key = raw_groq.strip().strip('"').strip("'")
        else:
            self.groq_api_key = None

        self.base_url = (base_url or os.getenv("OLLAMA_BASE_URL") or "http://127.0.0.1:11434").rstrip("/")
        self.cpu_threads = max(1, (os.cpu_count() or 4) - 1)
        self.explicit_model = model_name
        self.model_name = model_name or self._select_best_model("English")

    def is_server_online(self) -> bool:
        if self.openrouter_api_key or self.groq_api_key:
            return True
        try:
            res = requests.get(f"{self.base_url}/api/tags", timeout=3)
            return res.status_code == 200
        except Exception:
            return False

    def get_available_models(self) -> List[str]:
        try:
            res = requests.get(f"{self.base_url}/api/tags", timeout=3)
            if res.status_code == 200:
                data = res.json()
                return [m.get("name") for m in data.get("models", [])]
        except Exception:
            pass
        return ["qwen2.5:1.5b"]

    def _select_best_model(self, target_language: str = "English") -> str:
        if self.explicit_model:
            return self.explicit_model
            
        available = self.get_available_models()
        if not available:
            return "qwen2.5:1.5b"
            
        for cand in ["qwen2.5:1.5b", "qwen2.5:0.5b", "llama3.2:1b", "qwen2.5-coder:latest"]:
            if cand in available or any(m.startswith(cand) for m in available):
                return next(m for m in available if m == cand or m.startswith(cand))
                
        return available[0] if available else "qwen2.5:1.5b"

    def _chat_openrouter_stream(self, messages: List[Dict[str, str]], api_key: str, temperature: float, max_tokens: int) -> Generator[str, None, None]:
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "https://setux.com",
            "X-Title": "SetuX AI",
            "Content-Type": "application/json"
        }
        
        free_models = [
            "qwen/qwen-2.5-7b-instruct:free",
            "meta-llama/llama-3.2-11b-vision-instruct:free",
            "google/gemma-2-9b-it:free"
        ]
        
        for model in free_models:
            payload = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": True
            }
            try:
                res = requests.post(url, json=payload, headers=headers, stream=True, timeout=20)
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
            except Exception:
                pass
                
        yield from self._chat_ollama_stream(messages, "English", temperature, max_tokens)

    def _chat_groq_stream(self, messages: List[Dict[str, str]], api_key: str, temperature: float, max_tokens: int) -> Generator[str, None, None]:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        candidates = ["llama-3.1-8b-instant", "gemma2-9b-it"]
        for candidate in candidates:
            payload = {
                "model": candidate,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": True
            }
            try:
                res = requests.post(url, json=payload, headers=headers, stream=True, timeout=15)
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
                    return
            except Exception:
                pass
                
        yield from self._chat_ollama_stream(messages, "English", temperature, max_tokens)

    def _chat_ollama_stream(self, messages: List[Dict[str, str]], target_language: str, temperature: float, max_tokens: int) -> Generator[str, None, None]:
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
                yield f"\n[Error: Ollama server returned status code {res.status_code}]"
        except requests.exceptions.Timeout:
            yield "\n[Error: Local LLM request timed out.]"
        except requests.exceptions.ConnectionError:
            if os.getenv("VERCEL") or os.getenv("VERCEL_ENV"):
                yield "\n[Vercel Setup Notice: Please set your FREE GROQ_API_KEY or OPENROUTER_API_KEY in Vercel Settings -> Environment Variables, then click Redeploy!]"
            else:
                yield f"\n[Error: Cannot connect to Ollama at {self.base_url}. Ensure Ollama or server.py is running.]"
        except Exception as e:
            yield f"\n[Error communicating with LLM: {str(e)}]"

    def chat_completion_stream(self, messages: List[Dict[str, str]], temperature: float = 0.1, max_tokens: int = 250, target_language: str = "English") -> Generator[str, None, None]:
        if self.openrouter_api_key:
            yield from self._chat_openrouter_stream(messages, self.openrouter_api_key, temperature, max_tokens)
        elif self.groq_api_key:
            yield from self._chat_groq_stream(messages, self.groq_api_key, temperature, max_tokens)
        else:
            yield from self._chat_ollama_stream(messages, target_language, temperature, max_tokens)

    def chat_completion(self, messages: List[Dict[str, str]], temperature: float = 0.1, max_tokens: int = 250, target_language: str = "English") -> str:
        tokens = list(self.chat_completion_stream(messages, temperature=temperature, max_tokens=max_tokens, target_language=target_language))
        return "".join(tokens).strip()
