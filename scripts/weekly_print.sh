#!/bin/bash

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

log "[INFO] Running weekly print job at $(date)"

# Source env vars for cron
[ -f /env.sh ] && source /env.sh

# Generate PDF
python3 /home/generate_pdf.py

# Print
if lp -d MyPrinter /home/color_test_page_dated.pdf; then
    log "[INFO] Print job succeeded. Sending notifications..."
    python3 /home/send_notification.py "SUCCESS" "Color test page printed successfully at $(date)."
else
    log "[ERROR] Print job failed. Sending notifications..."
    python3 /home/send_notification.py "FAILURE" "Color test page FAILED to print at $(date)."
fi
