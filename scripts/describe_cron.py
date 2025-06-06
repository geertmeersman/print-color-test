"""
╔══════════════════════════════════════════════════════════════╗
║         CRONTAB HUMANIZER – Docker Startup Utility           ║
╠══════════════════════════════════════════════════════════════╣
║ Reads cron expressions from /etc/cron.d/color-printer and    ║
║ uses cron-descriptor to generate human-readable schedules.   ║
║                                                              ║
║ Example:                                                     ║
║   0 11 * * 5   →   At 11:00 AM, only on Friday               ║
║                                                              ║
║ Useful for debugging and logging inside Docker containers.   ║
║                                                              ║
║ Author: Geert Meersman 🚀                                    ║
╚══════════════════════════════════════════════════════════════╝
"""

from cron_descriptor import get_description
import re

print("📆 Scheduled Cron Jobs:")

with open("/etc/cron.d/color-printer", "r") as file:
    for line in file:
        # Skip empty/comment lines
        if line.strip().startswith("#") or not line.strip():
            continue

        # Extract cron timing (first 5 fields)
        match = re.match(r"^(\S+\s+\S+\s+\S+\s+\S+\s+\S+)", line)
        if match:
            cron_expr = match.group(1)
            try:
                human = get_description(cron_expr)
                print(f"🕒 {cron_expr} → {human}")
            except Exception as e:
                print(f"⚠️ Failed to parse: {cron_expr} ({e})")
