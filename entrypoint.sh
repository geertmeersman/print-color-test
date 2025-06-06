#!/bin/bash
set -e

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}


cat << "EOF"
 _____                _    ___  ___                                         
|  __ \              | |   |  \/  |                                         
| |  \/ ___  ___ _ __| |_  | .  . | ___  ___ _ __ ___ _ __ ___   __ _ _ __  
| | __ / _ \/ _ \ '__| __| | |\/| |/ _ \/ _ \ '__/ __| '_ ` _ \ / _` | '_ \ 
| |_\ \  __/  __/ |  | |_  | |  | |  __/  __/ |  \__ \ | | | | | (_| | | | |
 \____/\___|\___|_|   \__| \_|  |_/\___|\___|_|  |___/_| |_| |_|\__,_|_| |_|
                                                                            

Print Color Test Docker Container
by Geert Meersman
===========================================

This container generates a color test PDF and prints it to a networked Canon printer using CUPS and cron.
It helps maintain your Canon Maxify GX7050 (or similar) inkjet printer by keeping ink flowing regularly.
---------------------------------------------------------------------------------------------------------


EOF

# Dump selected environment variables with quoting
{
  printenv | grep -E '^(PRINTER_URI|PRINTER_NAME|SMTP_USER|SMTP_PWD|SMTP_SERVER|SMTP_PORT|EMAIL_FROM|EMAIL_TO|TELEGRAM_BOT_ID|TELEGRAM_CHAT_ID)=' | \
    while IFS='=' read -r key value; do
      echo "export ${key}=\"${value//\"/\\\"}\""
    done
} > /env.sh
chmod +x /env.sh


# Start CUPS daemon in the background
log "[INFO] Starting CUPS service..."
cupsd &

# Wait a bit for CUPS to start
sleep 3

# Start cron
log "[INFO] Starting cron..."
cron
log "[INFO] Crontab listing..."
crontab -l

# Add the printer (overwrite if exists)
log "[INFO] Adding printer $PRINTER_NAME ($PRINTER_URI)..."
lpadmin -p "MyPrinter" -v "$PRINTER_URI" -D "$PRINTER_NAME" -m everywhere -E

log "[INFO] Setting 'MyPrinter' as default printer..."
lpadmin -d "MyPrinter"

log "[INFO] CUPS and printer setup completed. Ready to receive print jobs."
lpstat -p MyPrinter

# Optional: keep container running to troubleshoot, or exit
tail -f /dev/null
