const TelegramBot = require('node-telegram-bot-api');
const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');

// Thay thế BOT_TOKEN với token của bạn
const token = '7588647057:AAFp-akD0f4VK84zOxxJPLuQQzyswC6tzXg';
const adminChatIds = ['7371969470']; // ID chat admin

// Tạo bot
const bot = new TelegramBot(token, { polling: true });

// Lắng nghe lỗi polling
bot.on('polling_error', (error) => {
    console.error('Polling Error:', error.code, error.response ? error.response.body : error.message);
});

// Gửi thông báo kết nối thành công
adminChatIds.forEach(chatId => {
    bot.sendMessage(chatId, 'Bot đã kết nối thành công với Telegram!');
});

// Hướng dẫn sử dụng bot
const helpMessage = `
*Hướng dẫn sử dụng bot:*

╔════════════════════════════════════════════╗
║                  Lệnh Bot                 ║
╠════════════════════════════════════════════╣
║ /help                                   - Hiển thị hướng dẫn sử dụng bot.        ║
║ /download <tên_file>                    - Tải file từ server về nhóm chat.        ║
║ /delete <tên_file>                      - Xóa file trong thư mục bot.            ║
║ /deleteall <tiền_tố_file>               - Xóa tất cả các file có tiền tố tương   ║
║                                           ứng.                                   ║
║ /rename <tên_file_cũ> <tên_file_mới>     - Đổi tên file từ tên cũ sang tên mới.  ║
║ /upload                                 - Tải file lên server qua Telegram.      ║
╚════════════════════════════════════════════╝

*Lưu ý:* 
- Bot sẽ tự động nhận và xử lý các file gửi đến trong nhóm chat.
- Các lệnh phải được thực hiện bởi admin của bot.
`;

bot.on('message', async (msg) => {
    const chatId = msg.chat.id;

    // Kiểm tra quyền admin
    if (!adminChatIds.includes(chatId.toString())) {
        return bot.sendMessage(chatId, 'Bạn không có quyền thực hiện lệnh này.');
    }

    if (msg.text) {
        const command = msg.text.trim();

        // Hiển thị hướng dẫn sử dụng
        if (command === '/help') return bot.sendMessage(chatId, helpMessage, { parse_mode: 'Markdown' });

        // Xử lý các lệnh
        const args = command.split(' ').slice(1);
        switch (true) {
            case command.startsWith('/download '):
                handleDownload(chatId, args[0]);
                break;
            case command.startsWith('/delete '):
                handleDelete(chatId, args[0]);
                break;
            case command.startsWith('/deleteall '):
                handleDeleteAll(chatId, args[0]);
                break;
            case command.startsWith('/rename '):
                handleRename(chatId, args);
                break;
            default:
                handleTerminalCommand(chatId, command);
        }
    } else if (msg.document) {
        handleFileUpload(chatId, msg.document);
    }
});

// Xử lý tải file lên
function handleFileUpload(chatId, document) {
    const fileName = document.file_name;
    bot.downloadFile(document.file_id, __dirname)
        .then(() => bot.sendMessage(chatId, `✅ File đã được tải lên thành công: ${fileName}`))
        .catch(err => bot.sendMessage(chatId, `❌ Đã xảy ra lỗi khi tải file. Lỗi: ${err.message}`));
}

// Hàm xử lý lệnh terminal
function handleTerminalCommand(chatId, terminalCommand) {
    if (!terminalCommand) {
        return bot.sendMessage(chatId, 'Vui lòng cung cấp lệnh để thực thi.');
    }

    exec(terminalCommand, (error, stdout, stderr) => {
        if (error) {
            // Nếu lỗi liên quan đến mô-đun thiếu
            if (stderr && stderr.includes('MODULE_NOT_FOUND')) {
                const missingModule = stderr.match(/Cannot find module '(.*?)'/);
                if (missingModule) {
                    const errorMessage = `❌ Thiếu mô-đun: ${missingModule[1]}`;
                    bot.sendMessage(chatId, errorMessage, { parse_mode: 'Markdown' });
                    console.error(errorMessage);  // In lỗi ra terminal
                    return;
                }
            }

            // Nếu có lỗi khác
            const errorMessage = `❌ Lỗi khi thực thi lệnh:\n\`${error.message}\``;
            bot.sendMessage(chatId, errorMessage, { parse_mode: 'Markdown' });
            console.error(errorMessage);  // In lỗi ra terminal
            return;
        }

        if (stderr) {
            const stderrMessage = `⚠️ Kết quả lỗi:\n\`${stderr}\``;
            bot.sendMessage(chatId, stderrMessage, { parse_mode: 'Markdown' });
            console.error(stderrMessage);  // In lỗi ra terminal
            return;
        }

        const successMessage = `✅ Kết quả:\n\`${stdout}\``;
        bot.sendMessage(chatId, successMessage, { parse_mode: 'Markdown' });
        console.log(successMessage);  // In kết quả ra terminal
    });
}


// Hàm xử lý tải file
function handleDownload(chatId, fileName) {
    if (!fileName) return bot.sendMessage(chatId, '❌ Vui lòng cung cấp tên file để tải xuống.');

    const filePath = path.join(__dirname, fileName);
    fs.access(filePath, fs.constants.F_OK, (err) => {
        if (err) return bot.sendMessage(chatId, `❌ Không tìm thấy file: ${fileName}.`);

        bot.sendDocument(chatId, filePath)
            .then(() => bot.sendMessage(chatId, `✅ Đã gửi file: ${fileName}`))
            .catch(err => bot.sendMessage(chatId, `❌ Đã xảy ra lỗi khi gửi file. Lỗi: ${err.message}`));
    });
}

// Hàm xử lý xóa file
function handleDelete(chatId, fileName) {
    if (!fileName) return bot.sendMessage(chatId, '❌ Vui lòng cung cấp tên file để xóa.');

    const filePath = path.join(__dirname, fileName);
    fs.unlink(filePath, (err) => {
        if (err) return bot.sendMessage(chatId, `❌ Không thể xóa file: ${fileName}. Lỗi: ${err.message}`);
        bot.sendMessage(chatId, `✅ File đã được xóa thành công: ${fileName}`);
    });
}

// Hàm xử lý xóa tất cả file
function handleDeleteAll(chatId, filePrefix) {
    if (!filePrefix) return bot.sendMessage(chatId, '❌ Vui lòng cung cấp tiền tố file để xóa.');

    fs.readdir(__dirname, (err, files) => {
        if (err) return bot.sendMessage(chatId, `❌ Không thể đọc thư mục. Lỗi: ${err.message}`);

        const filesToDelete = files.filter(file => file.startsWith(filePrefix));
        if (filesToDelete.length === 0) return bot.sendMessage(chatId, `❌ Không tìm thấy file nào có tiền tố "${filePrefix}".`);

        filesToDelete.forEach(file => {
            const filePath = path.join(__dirname, file);
            fs.unlink(filePath, (err) => {
                if (err) console.error(`Không thể xóa file: ${file}. Lỗi: ${err.message}`);
            });
        });
        bot.sendMessage(chatId, `✅ Đã xóa ${filesToDelete.length} file có tiền tố "${filePrefix}".`);
    });
}

// Hàm xử lý đổi tên file
function handleRename(chatId, [oldName, newName]) {
    if (!oldName || !newName) return bot.sendMessage(chatId, '❌ Vui lòng cung cấp tên file cũ và tên file mới để đổi tên.');

    const oldFilePath = path.join(__dirname, oldName);
    const newFilePath = path.join(__dirname, newName);

    fs.rename(oldFilePath, newFilePath, (err) => {
        if (err) return bot.sendMessage(chatId, `❌ Không thể đổi tên file: ${oldName}. Lỗi: ${err.message}`);
        bot.sendMessage(chatId, `✅ Đã đổi tên file từ "${oldName}" sang "${newName}" thành công.`);
    });
}

console.log('Bot đang chạy...');
