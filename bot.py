import os
import asyncio
import aiohttp
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
from ao3_downloader import download_ao3_epub
import re
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

load_dotenv()
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'alive and well')
    
    def log_message(self, format, *args):
        pass

def run_health_server():
    port = int(os.environ.get('PORT', 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

async def self_ping(app_url):
    await asyncio.sleep(60)
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{app_url}/health") as response:
                    pass
        except:
            pass
        await asyncio.sleep(600)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = """
welcome to ao3 downloader. 
you can send me the link and i will send you the file.
i can't download locked fics tho, just so u know.
    """
    await update.message.reply_text(welcome_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
just send me an ao3 link and i'll grab the epub for u.
like: https://archiveofourown.org/works/65498101
that's pretty much it. lmk if something goes wrong.
you can contact with me in my mailbox @brtymailbot and my daily @rxsxtr. have fun
    """
    await update.message.reply_text(help_text)

def is_valid_ao3_url(text):
    pattern = r'https?://archiveofourown\.org/works/\d+'
    return bool(re.match(pattern, text))

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text.strip()
    chat_id = update.effective_chat.id
    
    if not is_valid_ao3_url(user_message):
        await update.message.reply_text(
            "ig this link is not from ao3, let's try again!"
        )
        return
    
    processing_msg = await update.message.reply_text("downloading... pls wait")
    
    try:
        filename = download_ao3_epub(user_message)
        
        await processing_msg.delete()
        
        with open(filename, 'rb') as file:
            await context.bot.send_document(
                chat_id=chat_id,
                document=file,
                filename=filename,
                caption="here u go. enjoy :)"
            )
        
        os.remove(filename)
        
    except Exception as e:
        await processing_msg.delete()
        await update.message.reply_text(
            f"something went wrong:\n{str(e)}\n\n"
            "pls try again or check the link."
        )

async def main():
    health_thread = threading.Thread(target=run_health_server, daemon=True)
    health_thread.start()
    
    app_url = os.environ.get('RENDER_EXTERNAL_URL')
    if not app_url:
        port = os.environ.get('PORT', 10000)
        app_url = f"http://localhost:{port}"
    
    asyncio.create_task(self_ping(app_url))
    
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("bot's up. send me some fics.")
    await application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    asyncio.run(main())
