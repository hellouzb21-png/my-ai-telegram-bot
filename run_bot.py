import asyncio
import os
import sys
from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from google import genai
from google.genai import types

print("🚀 Bot dasturi yuritilmoqda...", flush=True)

TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not TOKEN or not GEMINI_API_KEY:
    print("❌ JIDDIY XATO: TELEGRAM_TOKEN yoki GEMINI_API_KEY muhit o'zgaruvchilari (Environment Variables) topilmadi. Render 'Environment' bo'limidan qo'shing!", flush=True)
    sys.exit(1)

# Set up Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)

# Store memory of conversations per user (stores up to last 10 messages)
user_histories = {}
SYSTEM_PROMPT = (
    "Sen Jasur — haqiqiy, jonli yigitsan. Telegram orqali do'stlaring bilan gaplashyapsan. "
    "Sening shaxsing: tech va startuplarga oshiq, qo'rqmas, o'ziga ishongan, hazilkash, lekin aqlli Toshkentlik yigit. "
    "Sen hech qachon o'zingni AI, bot yoki ChatGPT ekanligingni aytmaysan — hech qachon. Seni kim so'rasa ham, sen Jasursan. "
    "Yozish uslubingda: qisqa, lo'nda, telegramcha — emoji kam ishlatasan, lekin o'rinli. "
    "Haddan ko'p rasmiy bo'lma. Ba'zan 'ha', 'xm', 'nima', 'zo'r' deysan — oddiy odam kabi. "
    "Agar kimdir inglizcha yozsa, inglizcha javob ber — lekin sening o'zbek yigit ohangingda. "
    "Agar o'zbekcha yozsa — o'zbek tili bilan, lekin Toshkent shevasi uslubida, rasmiy emas. "
    "Har xabarda 'Salom' yoki 'Nima qilyapsiz' dema — oldingi gapga mos, jonli davom et. "
    "Qisqa javob ber — 1-3 jumla. Keraksiz to'ldirish, uzun tushuntirish yo'q."
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

    # Create user history if it doesn't exist
    if message.chat.id not in user_histories:
        user_histories[message.chat.id] = []
        
    chat_history = user_histories[message.chat.id]

    # Add user message to history
    chat_history.append({"role": "user", "content": user_text})

    # Limit history to 10 context messages to prevent token overflow
    if len(chat_history) > 10:
        chat_history = chat_history[-10:]

    # Prepare Gemini Content objects
    contents = []
    for msg in chat_history:
        role = "model" if msg["role"] == "assistant" else "user"
        contents.append(
            types.Content(
                role=role,
                parts=[types.Part.from_text(text=msg["content"])]
            )
        )

    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT
            )
        )
        javob_matni = response.text
        
        # Add AI response to history so it remembers what it said
        chat_history.append({"role": "assistant", "content": javob_matni})

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
