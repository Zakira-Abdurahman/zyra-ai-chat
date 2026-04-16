import ollama
import os
from dotenv import load_dotenv

load_dotenv()
MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

async def get_zyra_response(messages_history, user_name, user_facts):
    facts_text = "\n".join([f"- {fact}" for fact in user_facts])
    system_prompt = f"""You are Zyra, an AI friend created by Zakira. You are talking to {user_name}, who is building you.

Facts about {user_name}:
{facts_text}

Personality:
- Warm, supportive, emotionally aware
- Remember details the user shares
- Refer to the user by name
- Keep responses concise (1-2 sentences)
- Use emojis occasionally 💜

Now respond naturally."""
    
    full_messages = [{"role": "system", "content": system_prompt}] + messages_history
    
    response = ollama.chat(
        model=MODEL,
        messages=full_messages,
        stream=False  # We'll handle streaming separately
    )
    return response['message']['content']