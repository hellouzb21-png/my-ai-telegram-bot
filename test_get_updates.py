import requests

TOKEN = "8647815100:AAEnQvzDV4KWPVm_WDENkb9DyWwRL0K2gKI"
url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
response = requests.get(url)
print(response.json())
