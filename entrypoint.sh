#!/bin/bash
set -e

# Start CUPS daemon in the background
cupsd &

# Wait a bit for CUPS to start
sleep 3

# Start cron
cron

# Add the printer (overwrite if exists)
lpadmin -p "MyPrinter" -v "$PRINTER_URI" -m everywhere -E
lpadmin -d "MyPrinter"

# Optional: keep container running to troubleshoot, or exit
tail -f /dev/null
