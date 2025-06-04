
[![maintainer](https://img.shields.io/badge/maintainer-Geert%20Meersman-green?style=for-the-badge&logo=github)](https://github.com/geertmeersman)
[![buyme_coffee](https://img.shields.io/badge/Buy%20me%20an%20Omer-donate-yellow?style=for-the-badge&logo=buymeacoffee)](https://www.buymeacoffee.com/geertmeersman)
[![MIT License](https://img.shields.io/github/license/geertmeersman/print-color-test?style=for-the-badge)](https://github.com/geertmeersman/print-color-test/blob/main/LICENSE)

[![GitHub issues](https://img.shields.io/github/issues/geertmeersman/print-color-test)](https://github.com/geertmeersman/print-color-test/issues)
[![Average time to resolve an issue](http://isitmaintained.com/badge/resolution/geertmeersman/print-color-test.svg)](http://isitmaintained.com/project/geertmeersman/print-color-test)
[![Percentage of issues still open](http://isitmaintained.com/badge/open/geertmeersman/print-color-test.svg)](http://isitmaintained.com/project/geertmeersman/print-color-test)
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-brightgreen.svg)](https://github.com/geertmeersman/print-color-test/pulls)

[![github release](https://img.shields.io/github/v/release/geertmeersman/print-color-test?logo=github)](https://github.com/geertmeersman/print-color-test/releases)
[![github release date](https://img.shields.io/github/release-date/geertmeersman/print-color-test)](https://github.com/geertmeersman/print-color-test/releases)
[![github last-commit](https://img.shields.io/github/last-commit/geertmeersman/print-color-test)](https://github.com/geertmeersman/print-color-test/commits)
[![github contributors](https://img.shields.io/github/contributors/geertmeersman/print-color-test)](https://github.com/geertmeersman/print-color-test/graphs/contributors)
[![github commit activity](https://img.shields.io/github/commit-activity/y/geertmeersman/print-color-test?logo=github)](https://github.com/geertmeersman/print-color-test/commits/main)


# 🖨️ Print Color Test Docker Container

This Docker container automatically generates a color test PDF and prints it to a networked Canon printer using CUPS and cron. It's designed to keep inkjet printers like the Canon Maxify GX7050 healthy by preventing ink from drying out or air from entering the tubes.

Ideal for inkjet printer owners who **don't print frequently** but want to **avoid clogged nozzles**.

---

## ✨ Features

- 🎨 Generates a PDF with Cyan, Magenta, Yellow, and Black blocks *(or blank for testing)*
- 🖨️ Prints via IPP using CUPS
- 🕒 Scheduled weekly print every **Friday at 11:00 AM CEST**
- ⚙️ Configurable via environment variables
- 📧 Sends email and/or Telegram notifications on print success/failure
- 🧪 Supports dry-run with blank PDF generation

---

## ⚙️ Environment Variables

| Variable            | Description                                                                 |
|---------------------|-----------------------------------------------------------------------------|
| `PRINTER_URI`        | IPP URI of the printer (e.g. `ipp://10.0.0.24:631/ipp/print`)               |
| `PRINTER_NAME`       | Optional printer name (used in notifications only, not in `lp`)             |
| `SMTP_SERVER`        | SMTP server (e.g. `smtp.gmail.com`) to enable email notifications           |
| `SMTP_PORT`          | SMTP server port (default: `587`)                                           |
| `SMTP_USER`          | SMTP username (usually same as `EMAIL_FROM`)                                |
| `SMTP_PWD`           | SMTP password or app password                                               |
| `EMAIL_FROM`         | Sender email address                                                        |
| `EMAIL_TO`           | Recipient email address                                                     |
| `TELEGRAM_BOT_ID`    | Telegram bot token (e.g. `123456:ABCDEF`)                                   |
| `TELEGRAM_CHAT_ID`   | Telegram chat ID to receive messages                                        |

> 📌 The actual printer used by `lp` is hardcoded as `MyPrinter`.

---

## 🏗️ Building the Image

```bash
docker build -t print-color-test .
```

## 🚀 One-Time Test Run

```bash
docker run --rm   -e PRINTER_URI=ipp://10.0.0.24:631/ipp/print   -e PRINTER_NAME="Canon GX7050"   print-color-test
```

## 🔁 Run Persistently with Docker Compose

```yaml
version: '3.8'

services:
  print-color-test:
    image: print-color-test
    environment:
      PRINTER_URI: ipp://10.0.0.24:631/ipp/print
      PRINTER_NAME: Canon GX7050
      EMAIL_FROM: printer@example.com
      EMAIL_TO: you@example.com
      SMTP_SERVER: smtp.gmail.com
      SMTP_PORT: 587
      SMTP_USER: printer@example.com
      SMTP_PWD: your_app_password
      TELEGRAM_BOT_ID: 123456:ABCDEF
      TELEGRAM_CHAT_ID: -12345678
    ports:
      - "631:631"  # Optional: expose CUPS web interface
    tty: true
```

```bash
docker-compose up -d
```

---

## 📆 Weekly Scheduled Print

Prints every **Friday at 11:00 AM CEST** via cron.

**Cron job:**

```cron
0 11 * * 5 /usr/local/bin/weekly_print.sh >> /var/log/cron.log 2>&1
```

**Script: `weekly_print.sh`**

```bash
#!/bin/bash

echo "[INFO] Running weekly print job at $(date)"

# Generate PDF
python3 /home/generate_pdf.py

# Print
if lp -d MyPrinter /home/color_test_page_dated.pdf; then
    echo "[INFO] Print job succeeded. Sending notifications..."
    python3 /home/send_notification.py "SUCCESS" "Color test page printed successfully at $(date)."
else
    echo "[ERROR] Print job failed. Sending notifications..."
    python3 /home/send_notification.py "FAILURE" "Color test page FAILED to print at $(date)."
fi
```

---

## 🛠️ Printer and notifications Debugging

```bash
docker exec -it <container_id> bash
```

Inside the container:

```bash
lpstat -p             # Printer status
lpstat -o             # Print queue
cancel -a             # Cancel all jobs
/usr/local/bin/weekly_print.sh # Launch the color test print job and push notifications if the environment variables are set
lp -d MyPrinter /home/color_test_page_dated.pdf  # Manual print test
/home/test_empty.sh   # Generate an empty PDF, send it to the printer and push notifications if the environment variables are set
```

---

## 💬 Community & Support

Questions, feedback, or want to chat?

📨 **Discord:** [discordapp.com/users/geertmeersman](https://discordapp.com/users/geertmeersman)

---

## 📄 License

MIT

---

## 📬 How to Set Up Telegram Notifications

To receive print job notifications via Telegram, you’ll need:

- A **Telegram Bot Token** (`TELEGRAM_BOT_ID`)
- Your **Chat ID** (`TELEGRAM_CHAT_ID`)

### 🛠️ Step 1: Create a Telegram Bot

1. Open Telegram and search for `@BotFather`
2. Start a chat and send:  
   ```
   /newbot
   ```
3. Follow the prompts to name your bot
4. You’ll get a token that looks like:  
   ```
   123456789:ABCDefGhIjKlMnOpQRStuvWxYz
   ```
   This is your **`TELEGRAM_BOT_ID`**

### 🧾 Step 2: Get Your Chat ID

1. Start a chat with your new bot (just send it any message)
2. Open your browser and visit:  
   ```
   https://api.telegram.org/bot<YOUR_BOT_ID>/getUpdates
   ```
   For example:  
   ```
   https://api.telegram.org/bot123456789:ABCDefGhIjKlMnOpQRStuvWxYz/getUpdates
   ```
3. Look for the `chat.id` in the response:
   ```json
   "chat": {
     "id": 123456789,
     ...
   }
   ```
   - If you’re using a **group**, add the bot to the group and look for a **negative number** like `-987654321`

This is your **`TELEGRAM_CHAT_ID`**

### ✅ Example `.env`

```env
TELEGRAM_BOT_ID=123456789:ABCDefGhIjKlMnOpQRStuvWxYz
TELEGRAM_CHAT_ID=123456789
```
