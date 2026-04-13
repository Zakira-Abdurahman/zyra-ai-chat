# backend/app/main.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import json
import ollama # Import the ollama library
from app.websocket_manager import manager

app = FastAPI(title="Zyra Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Zyra backend is running with a FREE AI model! 💜"}

# This is our new, more powerful WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    conversation_history = []
    # Zyra's personality for Ollama
    system_prompt_content = "You are Zyra, a warm, friendly AI friend. Keep responses short and conversational."

    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)

            if message_data.get("type") == "message":
                user_text = message_data.get("content", "")
                conversation_history.append({"role": "user", "content": user_text})

                # Tell frontend Zyra is thinking
                await manager.send_message(websocket, {"type": "typing", "value": True})

                # Prepare messages for Ollama
                ollama_messages = [
                    {'role': 'system', 'content': system_prompt_content},
                    *conversation_history
                ]

                # --- This is the streaming part ---
                # We'll collect the streamed response
                full_response = ""
                stream = ollama.chat(
                    model='llama3.2:3b',
                    messages=ollama_messages,
                    stream=True,  # <-- THIS ENABLES STREAMING
                )

                for chunk in stream:
                    # chunk['message']['content'] is the next word or piece of text
                    content_piece = chunk['message']['content']
                    full_response += content_piece
                    # Send the partial message to the frontend in real-time!
                    await manager.send_message(websocket, {
                        "type": "stream",
                        "content": content_piece,
                    })

                # Once the stream is finished, send the final, complete message
                await manager.send_message(websocket, {
                    "type": "message",
                    "role": "assistant",
                    "content": full_response,
                })
                # Tell frontend Zyra has finished thinking
                await manager.send_message(websocket, {"type": "typing", "value": False})

                conversation_history.append({"role": "assistant", "content": full_response})

    except WebSocketDisconnect:
        manager.disconnect(websocket)