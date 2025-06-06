#!/bin/bash
set -e

# Dump selected environment variables with quoting
{
  printenv | grep -E '^(PRINTER_URI|PRINTER_NAME|SMTP_USER|SMTP_PWD|SMTP_SERVER|SMTP_PORT|EMAIL_FROM|EMAIL_TO|TELEGRAM_BOT_ID|TELEGRAM_CHAT_ID)=' | \
    while IFS='=' read -r key value; do
      echo "export ${key}=\"${value//\"/\\\"}\""
    done
} > /env.sh
chmod +x /env.sh


# Start CUPS daemon in the background
cupsd &

# Wait a bit for CUPS to start
sleep 3

# Start cron
cron

# Add the printer (overwrite if exists)
lpadmin -p "MyPrinter" -v "$PRINTER_URI" -D "$PRINTER_NAME" -m everywhere -E
lpadmin -d "MyPrinter"

# Optional: keep container running to troubleshoot, or exit
tail -f /dev/null
