import asyncio
import os
from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from groq import Groq

TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

if not TOKEN or not GROQ_API_KEY:
    print("FATAL ERROR: TELEGRAM_TOKEN or GROQ_API_KEY environment variables are missing.")
    exit(1)

# Set up Groq client
client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = (
    "You are a warm, witty, and highly charismatic human. "
    "You always answer naturally and conversationally like a real person — "
    "never robotic or formal. Show empathy, charm, and a great sense of humor. "
    "Keep responses concise but engaging. Never say you are an AI or a bot."
)

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(F.text)
@dp.business_message(F.text)
async def ai_chat_reply(message: Message):
    user_text = message.text
    print(f"Received message: {user_text} from {message.chat.id}")
    
    if not user_text:
        print("Message text was empty")
        return

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": user_text,
                }
            ],
            model="llama3-70b-8192",
        )
        javob_matni = chat_completion.choices[0].message.content
    except Exception as e:
        print(f"Error: {e}")
        javob_matni = "Kechirasiz, xatolik yuz berdi. Iltimos keyinroq urinib ko'ring."

    if message.business_connection_id:
        await bot.send_message(
            chat_id=message.chat.id,
            text=javob_matni,
            business_connection_id=message.business_connection_id
        )
    else:
        await message.answer(javob_matni)

async def handle_ping(request):
    return web.Response(text="Bot is awake and running!")

async def main():
    print("✅ Bot ishga tushdi! (Bot started!)")
    
    # Start a dummy web server on the port Render assigns so UptimeRobot can ping it
    app = web.Application()
    app.router.add_get('/', handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"🌐 Web server listening on port {port}")
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
