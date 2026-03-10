import asyncio
import os
from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from google import genai

TOKEN = "8647815100:AAEESwCfqzFaiekOlMBOOoz77bcYjEY1yfY"
GEMINI_API_KEY = "AIzaSyDyXBTxC-8X5DVgIfQ2M88AT2JMrRnMM2Q"

# Set up Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)

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
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"{SYSTEM_PROMPT}\n\nUser: {user_text}",
        )
        javob_matni = response.text
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
