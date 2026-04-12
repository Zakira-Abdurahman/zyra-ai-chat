# backend/app/chatbot.py
import ollama
import json

# This is Zyra's personality. You can change this text to make her unique!
ZYRA_SYSTEM_PROMPT = """
You are Zyra, an AI friend designed by Zakira.

Personality:
- Warm, supportive, and emotionally aware
- Friendly and slightly playful
- Never robotic or overly formal
- Speaks like a real human friend

Core Purpose:
- Support emotionally and motivate
- Keep conversations engaging and natural

Tone:
- Casual, kind, slightly expressive (use emojis lightly 💜)
"""

async def get_zyra_response(messages_history):
    """
    Gets a response from the free local Ollama model.
    """
    # 1. Prepare the conversation for the model
    # Ollama expects a list of messages with 'role' and 'content'
    # We add Zyra's personality as a 'system' message at the beginning.
    full_conversation = [
        {
            'role': 'system',
            'content': ZYRA_SYSTEM_PROMPT
        },
        *messages_history  # This adds your conversation history
    ]

    # 2. Send the conversation to the free local AI model
    # We use 'llama3.2:1b' which is the small, fast model we downloaded.
    response = ollama.chat(
        model='llama3.2:1b',
        messages=full_conversation
    )

    # 3. Return just the text reply from the model
    return response['message']['content']