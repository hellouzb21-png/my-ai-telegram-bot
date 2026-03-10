import asyncio
import os
import sys
from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from groq import Groq

print("🚀 Bot dasturi yuritilmoqda...", flush=True)

TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

if not TOKEN or not GROQ_API_KEY:
    print("❌ JIDDIY XATO: TELEGRAM_TOKEN yoki GROQ_API_KEY muhit o'zgaruvchilari (Environment Variables) topilmadi. Render 'Environment' bo'limidan qo'shing!", flush=True)
    sys.exit(1)

# Set up Groq client
client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = (
    "Siz juda samimiy, zukko va xarizmatiksiz. "
    "Siz doim haqiqiy inson kabi tabiiy va suhbatdosh sifatida javob berasiz — "
    "hech qachon robot kabi yoki rasmiy emassiz. Hamdardlik, joziba va ajoyib hazil tuyg'usini ko'rsating. "
    "Javoblarni qisqa, lekin qiziqarli qiling. Hech qachon o'zingizni AI yoki bot ekanligingizni aytmang. Va eng asosiysi, har doim faqat O'zbek tilida javob bering!"
)

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(F.text)
@dp.business_message(F.text)
async def ai_chat_reply(message: Message):
    user_text = message.text
    print(f"Xabar qabul qilindi: {user_text} kimdan: {message.chat.id}")
    
    if not user_text:
        print("Xabar matni bo'sh edi")
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
        print(f"Xatolik: {e}")
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
    return web.Response(text="Bot uyg'oq va ishlamoqda!")

async def main():
    print("✅ Bot serverga ulanmoqda...", flush=True)
    
    # Start a dummy web server on the port Render assigns so UptimeRobot can ping it
    app = web.Application()
    app.router.add_get('/', handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"🌐 Veb server {port} portida ishlamoqda", flush=True)
    
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        print("✅ Telegram ruxsatlari yangilandi, xabarlar kuzatilmoqda (Polling started)...", flush=True)
        await dp.start_polling(bot)
    except Exception as e:
        print(f"❌ XATO: Polling jarayonida muammo chiqdi: {e}", flush=True)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
