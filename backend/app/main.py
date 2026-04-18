from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
import json
import ollama
from app.database import AsyncSessionLocal, engine, Base
from app.websocket_manager import manager
from app.crud import get_or_create_user, get_active_conversation, save_message, get_conversation_history, update_user_facts
from app.chatbot import get_zyra_response
import os
from dotenv import load_dotenv

load_dotenv()
MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

app = FastAPI(title="Zyra Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables on startup
@app.on_event("startup")
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
def root():
    return {"message": "Zyra backend with PostgreSQL is running! 💜"}

@app.get("/favicon.ico")
async def favicon():
    from fastapi.responses import Response
    return Response(status_code=204)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    
    user_name = "Zaku"
    async with AsyncSessionLocal() as db:
        user = await get_or_create_user(db, user_name, is_creator=True)
        conversation = await get_active_conversation(db, user.id)
        history = await get_conversation_history(db, conversation.id, limit=10)
        messages_history = [{"role": msg.role, "content": msg.content} for msg in history]
        user_facts = json.loads(user.facts) if user.facts else []
    
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            if message_data.get("type") == "message":
                user_text = message_data.get("content", "")
                
                # Save user message
                async with AsyncSessionLocal() as db:
                    user = await get_or_create_user(db, user_name, is_creator=True)
                    conversation = await get_active_conversation(db, user.id)
                    await save_message(db, conversation.id, "user", user_text)
                    if "remember that" in user_text.lower():
                        fact = user_text.lower().split("remember that")[-1].strip()
                        await update_user_facts(db, user.id, fact)
                
                messages_history.append({"role": "user", "content": user_text})
                
                await manager.send_message(websocket, {"type": "typing", "value": True})
                
                ai_reply = await get_zyra_response(messages_history, user_name, user_facts)
                
                # Save assistant message
                async with AsyncSessionLocal() as db:
                    user = await get_or_create_user(db, user_name, is_creator=True)
                    conversation = await get_active_conversation(db, user.id)
                    await save_message(db, conversation.id, "assistant", ai_reply)
                
                messages_history.append({"role": "assistant", "content": ai_reply})
                
                await manager.send_message(websocket, {"type": "stream_start"})
                await manager.send_message(websocket, {"type": "stream_chunk", "content": ai_reply})
                await manager.send_message(websocket, {"type": "stream_end"})
                await manager.send_message(websocket, {"type": "typing", "value": False})
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)