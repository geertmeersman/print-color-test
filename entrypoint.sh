#!/bin/bash
set -euo pipefail

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

# Display banner
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

# Validate required environment variables
: "${PRINTER_URI:?Environment variable PRINTER_URI is not set}"
: "${PRINTER_NAME:?Environment variable PRINTER_NAME is not set}"

# Dump selected environment variables to /env.sh
{
  printenv | grep -E '^(PRINTER_URI|PRINTER_NAME|SMTP_USER|SMTP_PWD|SMTP_SERVER|SMTP_PORT|EMAIL_FROM|EMAIL_TO|TELEGRAM_BOT_ID|TELEGRAM_CHAT_ID)=' | \
    while IFS='=' read -r key value; do
      echo "export ${key}=\"${value//\"/\\\"}\""
    done
} > /env.sh
chmod +x /env.sh

# Start CUPS
log "[INFO] Starting CUPS service..."
cupsd &
sleep 3

if ! pgrep cupsd > /dev/null; then
  log "[ERROR] CUPS failed to start!"
  exit 1
fi

# Start cron
log "[INFO] Starting cron service..."
cron &

# Describe cron jobs
log "[INFO] Describing cron jobs..."
python3 /home/describe_cron.py || log "[WARN] Failed to describe cron jobs."

# Configure printer
CUPS_PRINTER_NAME="MyPrinter"

log "[INFO] Adding printer '$PRINTER_NAME' at $PRINTER_URI..."
if ! lpadmin -p "$CUPS_PRINTER_NAME" -v "$PRINTER_URI" -D "$PRINTER_NAME" -m everywhere -E; then
  log "[ERROR] Failed to add printer!"
  exit 1
fi

log "[INFO] Setting '$CUPS_PRINTER_NAME' as default printer..."
lpadmin -d "$CUPS_PRINTER_NAME"

log "[INFO] Printer setup complete. Current printer status:"
lpstat -p "$CUPS_PRINTER_NAME" || log "[WARN] Could not retrieve printer status."

WEB_PORT="${WEB_PORT:-80}"
log "[INFO] Launching Flask web app on port $WEB_PORT..."
exec gunicorn --chdir /home/flask --bind 0.0.0.0:$WEB_PORT --worker-class eventlet --timeout 120 web_interface:app
