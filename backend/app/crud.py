from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import User, Conversation, Message
import json

async def get_or_create_user(db: AsyncSession, name: str, is_creator: bool = False) -> User:
    result = await db.execute(select(User).where(User.name == name))
    user = result.scalar_one_or_none()
    if not user:
        user = User(name=name, is_creator=is_creator, facts=json.dumps([]))
        db.add(user)
        await db.commit()
        await db.refresh(user)
    return user

async def get_active_conversation(db: AsyncSession, user_id: int) -> Conversation:
    # For simplicity, get the most recent conversation for this user
    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.started_at.desc())
        .limit(1)
    )
    conv = result.scalar_one_or_none()
    if not conv:
        conv = Conversation(user_id=user_id)
        db.add(conv)
        await db.commit()
        await db.refresh(conv)
    return conv

async def save_message(db: AsyncSession, conversation_id: int, role: str, content: str):
    msg = Message(conversation_id=conversation_id, role=role, content=content)
    db.add(msg)
    await db.commit()
    return msg

async def get_conversation_history(db: AsyncSession, conversation_id: int, limit: int = 10):
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.timestamp)
        .limit(limit)
    )
    return result.scalars().all()

async def update_user_facts(db: AsyncSession, user_id: int, new_fact: str):
    user = await db.get(User, user_id)
    if user:
        facts = json.loads(user.facts) if user.facts else []
        facts.append(new_fact)
        user.facts = json.dumps(facts)
        await db.commit()