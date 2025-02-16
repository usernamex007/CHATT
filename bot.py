import os
import aiohttp
import re
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
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

# स्टार्ट बटन और मैसेज
@app.on_message(filters.command("start"))
async def start(client, message):
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("❓ मदद", callback_data="help"),
         InlineKeyboardButton("👨‍💻 Owner", url="https://t.me/its_nexio")],
        [InlineKeyboardButton("📢 सपोर्ट चैनल", url="https://t.me/sanatani_tech"),
         InlineKeyboardButton("💬 सपोर्ट ग्रुप", url="https://t.me/sanatani_support")]
    ])
    caption = "🙋‍♂️ **नमस्ते! मैं आपका चैटबॉट हूँ।**\nमुझसे बात करें, इमेज मंगवाएं और बहुत कुछ।"
    await message.reply_photo(photo="https://files.catbox.moe/8dtq6s.jpg", caption=caption, reply_markup=buttons)

# मदद बटन और उसका जवाब
@app.on_callback_query(filters.regex("help"))
async def help_callback(client, callback_query):
    help_text = "**बॉट के कमांड्स:**\n- *बोल के बताओ* — वॉइस में जवाब\n- *तस्वीर* — इमेज भेजे\n- *गणना* — सीधे गणित के सवाल का जवाब\n- *जानकारी* — यूजर की जानकारी दे।"
    await callback_query.message.edit_text(help_text)

# टेक्स्ट इनपुट पर प्रतिक्रिया देना
@app.on_message(filters.text)
async def handle_text_message(client, message):
    chat_id = message.chat.id
    user_message = message.text.lower()
    
    # यूजर की जानकारी निकालने पर प्रतिक्रिया
    if "इस यूजर की जानकारी निकालो" in user_message or "user info" in user_message:
        target_user = message.reply_to_message.from_user if message.reply_to_message else message.from_user
        info = f"**यूजर जानकारी:**\n\n- नाम: {target_user.first_name}\n- यूजर आईडी: {target_user.id}\n"
        if target_user.username:
            info += f"- यूजरनेम: @{target_user.username}\n"
        await message.reply_text(info)

    # मैथेमेटिकल सवाल का जवाब देना
    elif re.search(r"(\d+)\s*[\+\-\*\/]\s*(\d+)", user_message):
        try:
            expression = re.sub(r"[^0-9+\-*/(). ]", "", user_message)
            result = eval(expression)
            await message.reply_text(f"सॉल्यूशन: `{expression}` = `{result}`")
        except Exception as e:
            await message.reply_text(f"कैलकुलेशन में त्रुटि: {str(e)}")
    
    # इमेज या सामान्य चैट प्रतिक्रिया
    elif any(word in user_message for word in ["photo", "image", "pic", "तस्वीर"]):
        image_url = await fetch_image(user_message)
        if image_url:
            await message.reply_photo(photo=image_url)
            await save_history(chat_id, user_message, "[Image Sent]")
        else:
            await message.reply_text("मुझे कोई इमेज नहीं मिली!")
    else:
        reply = await chatbot_reply(user_message)
        await message.reply_text(reply)
        await save_history(chat_id, user_message, reply)

print("Bot Started with Start Buttons, Help, User Info, and Math Calculation!")
app.run()
