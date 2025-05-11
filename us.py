from telethon import TelegramClient, events
import re
import asyncio

# -------- إعداداتك الشخصية --------
api_id = 22707838  # ← حط الـ api_id تبعك
api_hash = '7822c50291a41745fa5e0d63f21bbfb6'  # ← حط الـ api_hash تبعك
session_name = 'us_session'
channel_username = '@Ichancy_Usd'  # ← اسم القناة يلي تراقبها
allowed_chat_ids = [7323006705]  # ← حط الuser_id تبعك هون (مو اسم المستخدم)

# -------- متغيرات التحكم --------
client = TelegramClient(session_name, api_id, api_hash)
is_active = True  # الحالة: شغال / موقف

# -------- regex --------
code_pattern = re.compile(r'الكود الثالث\s*:\s*([A-Za-z0-9]{5,})', re.IGNORECASE)
bot_link_pattern = re.compile(r'رابط البوت\s*:\s*(https?://t\.me/\S+)', re.IGNORECASE)

# -------- التحكم اليدوي --------
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

# -------- المراقبة التلقائية للقناة --------
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

# -------- تشغيل العميل --------
async def main():
    await client.start()
    print("✅ البوت شغال ومترقب...")
    await client.run_until_disconnected()

asyncio.run(main())