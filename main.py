from telethon import TelegramClient, events
import re
import asyncio
import threading
import os
from flask import Flask

# -------- إعداداتك الشخصية --------
api_id = 9844693
api_hash = 'b9f99569919502974aedefbda38393a5'
session_name = 'us_session'
channel_username = '@Ichancy_Usd'
allowed_chat_ids = [7323006705]

# -------- regex --------
code_pattern = re.compile(r'الكود الثالث\s*:\s*([A-Za-z0-9]{5,})', re.IGNORECASE)
bot_link_pattern = re.compile(r'رابط البوت\s*:\s*(https?://t\.me/\S+)', re.IGNORECASE)

# -------- الحالة --------
client = TelegramClient(session_name, api_id, api_hash)
is_active = True

# -------- Web Server لإرضاء Render --------
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ البوت شغال على Render بدون مشاكل"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

# -------- Telethon Handlers --------
@client.on(events.NewMessage)
async def command_handler(event):
    global is_active

    if event.chat_id not in allowed_chat_ids:
        return

    msg = event.raw_text.strip().lower()

    if msg == '/start_bot':
        is_active = True
        await event.reply("✅ تم تفعيل البوت ومراقبة القناة.")
    elif msg == '/stop_bot':
        is_active = False
        await event.reply("⛔ تم إيقاف مراقبة القناة.")
    elif msg == '/status':
        status = "شغال ✅" if is_active else "موقف ⛔"
        await event.reply(f"الحالة الحالية: {status}")

@client.on(events.NewMessage(chats=channel_username))
async def handler(event):
    if not is_active:
        return

    text = event.raw_text
    code_match = code_pattern.search(text)
    link_match = bot_link_pattern.search(text)

    if not code_match or not link_match:
        print("ما تم العثور على الكود أو رابط البوت.")
        return

    code = code_match.group(1).strip()
    bot_link = link_match.group(1).strip()
    bot_username = bot_link.split('/')[-1]

    print(f"إرسال الكود [{code}] للبوت @{bot_username}")

    try:
        await client.send_message(bot_username, '/start')
        await asyncio.sleep(2)

        msgs = await client.get_messages(bot_username, limit=1)
        if msgs and msgs[0].buttons:
            for row in msgs[0].buttons:
                for button in row:
                    if 'كود' in button.text:
                        await button.click()
                        await asyncio.sleep(1)
                        await client.send_message(bot_username, code)
                        print("✅ تم إرسال الكود بنجاح.")
                        return
        print("لم يتم العثور على زر فيه كلمة 'كود'")
    except Exception as e:
        print(f"❌ خطأ أثناء تنفيذ العملية: {e}")

# -------- التشغيل --------
def run_telethon():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(client.start())
    print("✅ البوت شغال ومترقب...")
    loop.run_until_complete(client.run_until_disconnected())

if __name__ == "__main__":
    # شغل البوت بخيط
    threading.Thread(target=run_telethon).start()
    # شغل السيرفر
    run_flask()
