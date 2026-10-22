# 🖨️ Print Color Test

A Docker container that automatically generates a CMYK color test PDF and prints it weekly to a networked printer via CUPS — keeping inkjet nozzles healthy.

## Features

- 🎨 Generates a PDF with Cyan, Magenta, Yellow and Black color blocks
- 🖨️ Prints via IPP using CUPS
- 🕒 Scheduled weekly print every Friday at 11:00 AM via cron
- 🌐 Flask web interface for status, logs and cron schedule
- 📧 Email and/or Telegram notifications on success/failure
- 🧪 Blank PDF dry-run support

## Tags

| Tag | Description |
|-----|-------------|
| `latest` | Latest stable release |
| `v1.2.3` | Specific release version |

## Quick start

```yaml
services:
  print-color-test:
    image: geertmeersman/print-color-test:latest
    container_name: print-color-test
    restart: unless-stopped
    environment:
      PRINTER_URI: ipp://10.0.0.24:631/ipp/print
      PRINTER_NAME: Canon GX7050
      PRINTER_IP: 10.0.0.24
      WEB_PORT: 80
    ports:
      - "80:80"
```

## Environment variables

| Variable | Description |
|----------|-------------|
| `PRINTER_URI` | IPP URI of the printer |
| `PRINTER_NAME` | Printer name (used in notifications) |
| `PRINTER_IP` | IP address for SNMP ink level queries |
| `WEB_PORT` | Flask web interface port (default: 80) |
| `SMTP_SERVER` | SMTP server for email notifications |
| `SMTP_PORT` | SMTP port (default: 587) |
| `SMTP_USER` | SMTP username |
| `SMTP_PWD` | SMTP password |
| `EMAIL_FROM` | Sender email |
| `EMAIL_TO` | Recipient email |
| `TELEGRAM_BOT_ID` | Telegram bot token |
| `TELEGRAM_CHAT_ID` | Telegram chat ID |

## Base image

`python:3.13-alpine` — currently pinned to `3.13.17-alpine3.24`

## Links

- 📖 [Full documentation & source code](https://github.com/geertmeersman/print-color-test)
- 🐛 [Report an issue](https://github.com/geertmeersman/print-color-test/issues)
- 📋 [Changelog](https://github.com/geertmeersman/print-color-test/releases)
- 📜 [License — MIT](https://github.com/geertmeersman/print-color-test/blob/main/LICENSE)
