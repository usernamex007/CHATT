import os
import re
import cloudscraper
from pyrogram import Client, filters

API_ID = "28795512"
API_HASH = "c17e4eb6d994c9892b8a8b6bfea4042a"
BOT_TOKEN = "7589052839:AAGPMVeZpb63GEG_xXzQEua1q9ewfNzTg50"

app = Client("ChatGPTesBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

class ChatGptEs:
    def __init__(self):
        self.url = "https://chatgpt.es"
        self.api_endpoint = "https://chatgpt.es/wp-admin/admin-ajax.php"
        self.scraper = cloudscraper.create_scraper()

    def ask_question(self, message: str) -> str:
        page_text = self.scraper.get(self.url).text
        nonce_match = re.search(r'data-nonce="(.+?)"', page_text)
        post_id_match = re.search(r'data-post-id="(.+?)"', page_text)

        if not nonce_match or not post_id_match:
            return "[ERROR] Failed to fetch tokens."

        payload = {
            'check_51710191': '1',
            '_wpnonce': nonce_match.group(1),
            'post_id': post_id_match.group(1),
            'url': self.url,
            'action': 'wpaicg_chat_shortcode_message',
            'message': message,
            'bot_id': '0',
            'chatbot_identity': 'shortcode',
            'wpaicg_chat_client_id': os.urandom(5).hex(),
            'wpaicg_chat_history': None
        }

        response = self.scraper.post(self.api_endpoint, data=payload).json()
        return response.get('data', '[ERROR] No response.')

chatbot = ChatGptEs()

@app.on_message(filters.private & filters.text)
def chat_with_ai(client, message):
    user_message = message.text
    reply = chatbot.ask_question(user_message)
    message.reply_text(reply)

print("Bot Started!")
app.run()
