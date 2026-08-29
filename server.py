import os
import sys
import json
import asyncio
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from setux_bot.engine import SetuXBotEngine

app = FastAPI(
    title="SetuX AI Assistant API",
    description="REST & Self-Learning API Server for SetuX Document Portal AI Chatbot (Created by jitin.io)",
    version="2.0.0"
)

# Enable CORS for React Frontend and Host Websites
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

bot_engine = SetuXBotEngine()

class ChatRequest(BaseModel):
    message: str
    language: Optional[str] = "English"
    stream: Optional[bool] = True

class ScanWebsiteRequest(BaseModel):
    url: Optional[str] = None
    title: Optional[str] = None
    html: Optional[str] = None

class LearnFactRequest(BaseModel):
    fact: str
    response: str

@app.get("/")
def read_root():
    return {
        "status": "online",
        "app": "SetuX Self-Learning AI Assistant API",
        "active_model": bot_engine.ollama.model_name,
        "scanned_websites_count": len(bot_engine.learned_memory.get("scanned_websites", {}))
    }

@app.get("/api/status")
def get_status():
    return {
        "ollama_online": bot_engine.ollama.is_server_online(),
        "active_model": bot_engine.ollama.model_name,
        "available_models": bot_engine.ollama.get_available_models(),
        "bot_maker": "jitin.io",
        "scanned_websites_count": len(bot_engine.learned_memory.get("scanned_websites", {})),
        "history_count": len(bot_engine.conversation_history) // 2
    }

@app.get("/api/learned-knowledge")
def get_learned_knowledge():
    return {
        "scanned_websites": list(bot_engine.learned_memory.get("scanned_websites", {}).keys()),
        "custom_facts_count": len(bot_engine.learned_memory.get("custom_facts", []))
    }

@app.post("/api/scan-website")
def scan_website_endpoint(req: ScanWebsiteRequest):
    if req.html and req.url:
        result = bot_engine.learn_from_dom_payload(req.url, req.title or req.url, req.html)
        return {"message": f"Successfully learned live website content from {req.url}", "result": result}
    elif req.url:
        result = bot_engine.learn_from_website_url(req.url)
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to scan website URL"))
        return {"message": f"Successfully crawled and learned website from {req.url}", "result": result}
    else:
        raise HTTPException(status_code=400, detail="Must provide either 'url' or 'url' + 'html'.")

@app.post("/api/learn")
def learn_fact_endpoint(req: LearnFactRequest):
    result = bot_engine.learn_custom_fact(req.fact, req.response)
    return {"message": "Fact successfully learned and saved to memory.", "result": result}

@app.post("/api/clear")
def clear_chat():
    bot_engine.clear_history()
    return {"message": "Conversation history cleared successfully."}

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    if req.stream:
        token_gen, is_allowed = bot_engine.process_query_stream(req.message, target_language=req.language)
        
        async def event_generator():
            try:
                for token in token_gen:
                    yield f"data: {json.dumps({'token': token})}\n\n"
                    await asyncio.sleep(0.01)
                yield f"data: {json.dumps({'done': True, 'is_allowed': is_allowed})}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"

        return StreamingResponse(event_generator(), media_type="text/event-stream")
    else:
        response_text, is_allowed = bot_engine.process_query(req.message, target_language=req.language)
        return {
            "response": response_text,
            "is_allowed": is_allowed
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
