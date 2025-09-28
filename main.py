from pyrogram import Client

BOT_TOKEN = "7738267751:AAGQ-3Me9Q-_ftiS2hnpCtFJLS1NaqzNocQ"
CHAT_ID = "@Dark_TeraBoxBot"   # jaise @yourbotusername ya bot ka numeric ID

app = Client("check_revenue", bot_token=BOT_TOKEN)

with app:
    chat = app.get_chat(CHAT_ID)
    print(chat)
