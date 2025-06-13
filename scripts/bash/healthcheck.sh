#!/bin/bash

WEB_PORT="${WEB_PORT:-80}"

# Check if CUPS web interface is up on port 631
if ! curl -sf http://localhost:631 >/dev/null; then
  echo "Healthcheck failed: CUPS web interface not responding on port 631"
  exit 1
fi

# Check if the printer named 'MyPrinter' is recognized
if ! lpstat -p MyPrinter | grep -q "printer"; then
  echo "Healthcheck failed: Printer 'MyPrinter' not found"
  exit 1
fi

# Check if your webserver is up on the configured port (default 80)
if ! curl -sf http://localhost:"$WEB_PORT" >/dev/null; then
  echo "Healthcheck failed: Webserver not responding on port $WEB_PORT"
  exit 1
fi

# All checks passed
exit 0
