import asyncio
from google import genai

GEMINI_API_KEY = "AIzaSyDyXBTxC-8X5DVgIfQ2M88AT2JMrRnMM2Q"
client = genai.Client(api_key=GEMINI_API_KEY)

try:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Hello"
    )
    print("Response:", response.text)
except Exception as e:
    print(f"Error 2.5: {e}")

try:
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents="Hello"
    )
    print("Response 1.5:", response.text)
except Exception as e:
    print(f"Error 1.5: {e}")
