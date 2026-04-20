from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import json
import os
import logging
from dotenv import load_dotenv
from app.database import AsyncSessionLocal, engine, Base
from app.websocket_manager import manager
from app.crud import get_or_create_user, get_active_conversation, save_message, get_conversation_history, update_user_facts
from app.chatbot import get_zyra_response

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables ready")
    yield
    # Shutdown
    await engine.dispose()
    logger.info("Database engine disposed")

app = FastAPI(title="Zyra Backend", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Zyra backend is running! 💜"}

@app.get("/favicon.ico")
async def favicon():
    from fastapi.responses import Response
    return Response(status_code=204)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    user_id = None
    user_name = None
    conversation_id = None
    messages_history = []
    user_facts = []

    try:
        # First, try to get existing user from a stored session token (optional)
        # For simplicity, we'll wait for the first message to identify the user.
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)

            if message_data.get("type") == "message":
                user_text = message_data.get("content", "").strip()

                # If we don't have a user yet, treat this message as the user's name
                if user_name is None:
                    user_name = user_text
                    async with AsyncSessionLocal() as db:
                        user = await get_or_create_user(db, name=user_name, is_creator=False)
                        user_id = user.id
                        conversation = await get_active_conversation(db, user_id)
                        conversation_id = conversation.id
                        # Load history for this user
                        history = await get_conversation_history(db, conversation_id, limit=10)
                        messages_history = [{"role": msg.role, "content": msg.content} for msg in history]
                        user_facts = json.loads(user.facts) if user.facts else []
                    # Send welcome message
                    welcome = f"Nice to meet you, {user_name}! I'm Zyra, your AI friend. How can I help you today? 😊"
                    await manager.send_message(websocket, {"type": "message", "role": "assistant", "content": welcome})
                    # Save this welcome as an assistant message in DB? Optional.
                    continue

                # Normal message flow (user already identified)
                # Save user message
                async with AsyncSessionLocal() as db:
                    # Ensure user still exists (re‑fetch)
                    user = await get_or_create_user(db, name=user_name, is_creator=False)
                    conversation = await get_active_conversation(db, user.id)
                    await save_message(db, conversation.id, "user", user_text)
                    if "remember that" in user_text.lower():
                        fact = user_text.lower().split("remember that")[-1].strip()
                        await update_user_facts(db, user.id, fact)
                    # Refresh history if needed? Already have messages_history, but we'll append.
                messages_history.append({"role": "user", "content": user_text})

                # Tell frontend Zyra is thinking
                await manager.send_message(websocket, {"type": "typing", "value": True})

                # Get AI reply
                ai_reply = await get_zyra_response(messages_history, user_name, user_facts)

                # Save assistant message
                async with AsyncSessionLocal() as db:
                    user = await get_or_create_user(db, name=user_name, is_creator=False)
                    conversation = await get_active_conversation(db, user.id)
                    await save_message(db, conversation.id, "assistant", ai_reply)

                messages_history.append({"role": "assistant", "content": ai_reply})

                # Send the reply
                await manager.send_message(websocket, {"type": "message", "role": "assistant", "content": ai_reply})
                await manager.send_message(websocket, {"type": "typing", "value": False})

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for user: {user_name}")
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.close(code=1011, reason="Internal server error")
        except:
            pass
        manager.disconnect(websocket)