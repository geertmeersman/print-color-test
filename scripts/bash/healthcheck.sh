#!/bin/bash

# Check if CUPS web interface is up
if ! curl -sf http://localhost:631 >/dev/null; then
  echo "CUPS not responding on port 631"
  exit 1
fi

# Check if printer is recognized
if ! lpstat -p MyPrinter | grep -q "printer"; then
  echo "Printer 'MyPrinter' not found"
  exit 1
fi

exit 0
