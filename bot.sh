#!/bin/bash

# Cấp quyền thực thi cho tất cả các file bot và proxy
chmod +x bot1.py bot2.py bot3.py bot4.py bot5.py proxy.py

# Hiển thị lựa chọn bot cho người dùng
PS3='Chọn bot bạn muốn chạy (1-5): '
options=("Bot 1" "Bot 2" "Bot 3" "Bot 4" "Bot 5" "Thoát")
select opt in "${options[@]}"
do
    case $opt in
        "Bot 1")
            echo "Chạy Bot 1..."
            python3 bot1.py & python3 proxy.py
            break
            ;;
        "Bot 2")
            echo "Chạy Bot 2..."
            python3 bot2.py & python3 proxy.py
            break
            ;;
        "Bot 3")
            echo "Chạy Bot 3..."
            python3 bot3.py & python3 proxy.py
            break
            ;;
        "Bot 4")
            echo "Chạy Bot 4..."
            python3 bot4.py & python3 proxy.py
            break
            ;;
        "Bot 5")
            echo "Chạy Bot 5..."
            python3 bot5.py & python3 proxy.py
            break
            ;;
        "Thoát")
            echo "Thoát khỏi chương trình."
            break
            ;;
        *)
            echo "Lựa chọn không hợp lệ. Vui lòng chọn lại."
            ;;
    esac
done
