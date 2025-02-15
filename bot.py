import asyncio
import aiohttp
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatAction
from dalle import text2im  # DALL·E API के लिए इंपोर्ट

API_ID = "28795512"
API_HASH = "c17e4eb6d994c9892b8a8b6bfea4042a"
BOT_TOKEN = "7589052839:AAGPMVeZpb63GEG_xXzQEua1q9ewfNzTg50"

app = Client("ChatBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

async def fetch_response(query):
    url = f"https://codesearchdevapi.vercel.app/chat?query={query}"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=5) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("data")
        except (aiohttp.ClientError, asyncio.TimeoutError):
            return None

async def text_filter(_, __, m: Message):
    return (
        bool(m.text)
        and len(m.text) <= 69
        and not m.text.startswith(("!", "/"))
        and (not m.reply_to_message or m.reply_to_message.reply_to_message_id == m._client.me.id)
    )

chatbot_filter = filters.create(text_filter)

@app.on_message(chatbot_filter)
async def chatbot(client, message: Message):
    chat_id = message.chat.id
    await client.send_chat_action(chat_id, ChatAction.TYPING) 
    user_message = message.text.lower()

    if "pic" in user_message or "image" in user_message:
        await client.send_chat_action(chat_id, ChatAction.UPLOAD_PHOTO)
        image = await text2im({"prompt": user_message, "size": "1024x1024"})
        await message.reply_photo(photo=image["url"], caption="Here is your image!")
    else:
        reply = await fetch_response(user_message)
        await message.reply_text(reply or "ChatBot Error, Something went wrong. Contact @Sanatanu_support")

print("🤖 Chatbot with Image Generation is running...")
app.run()
