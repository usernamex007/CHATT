import os
import aiohttp
import asyncio
from pyrogram import Client, filters
from pyrogram.enums import ChatAction
from gtts import gTTS
from datetime import datetime

API_ID = "28795512"
API_HASH = "c17e4eb6d994c9892b8a8b6bfea4042a"
BOT_TOKEN = "7589052839:AAGPMVeZpb63GEG_xXzQEua1q9ewfNzTg50"
UNSPLASH_API_KEY = "NeYveZLZuKE1a3HJcGUmmdWG24B1UzAIgqMV53VPaPM"

app = Client("ChatBotWithFeatures", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

if not os.path.exists("chat_history"):
    os.makedirs("chat_history")

async def save_history(user_id, user_message, bot_reply):
    now = datetime.now().strftime("%Y-%m-%d")
    with open(f"chat_history/{user_id}_{now}.txt", "a") as file:
        file.write(f"User: {user_message}\nBot: {bot_reply}\n\n")

async def fetch_image(query):
    url = f"https://api.unsplash.com/photos/random?query={query}&client_id={UNSPLASH_API_KEY}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("urls", {}).get("regular")
            return None

async def send_voice_reply(message, text):
    tts = gTTS(text=text, lang="hi")
    tts.save("voice.mp3")
    await message.reply_voice("voice.mp3")
    os.remove("voice.mp3")

async def chatbot_reply(message_text):
    url = f"https://codesearchdevapi.vercel.app/chat?query={message_text}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("data")
            return "मुझे जवाब नहीं मिला!"

@app.on_message(filters.text & ~filters.command(["start", "help"]))
async def chatbot(client, message):
    chat_id = message.chat.id
    user_message = message.text.lower()
    await client.send_chat_action(chat_id, ChatAction.TYPING)

    if any(word in user_message for word in ["photo", "image", "pic", "तस्वीर"]):
        image_url = await fetch_image(user_message)
        if image_url:
            await message.reply_photo(photo=image_url)
            await save_history(chat_id, user_message, "[Image Sent]")
        else:
            await message.reply_text("मुझे कोई इमेज नहीं मिली!")
    else:
        reply = await chatbot_reply(user_message)
        await message.reply_text(reply)
        await send_voice_reply(message, reply)
        await save_history(chat_id, user_message, reply)

print("Bot Started with History, Images & Voice!")
app.run()
