#!/bin/bash

echo "[INFO] Sendig empty pdf print job at $(date)"

# Generate PDF
python3 /home/generate_empty_pdf.py

# Print
if lp -d MyPrinter /home/empty.pdf; then
    echo "[INFO] Print job succeeded. Sending notifications..."
    python3 /home/send_notification.py "SUCCESS" "Color test page printed successfully at $(date)."
else
    echo "[ERROR] Print job failed. Sending notifications..."
    python3 /home/send_notification.py "FAILURE" "Color test page FAILED to print at $(date)."
fi