# Use official slim Python 3.11 base image
FROM python:3.11-slim

# Install required system packages:
# - cron: for scheduled jobs
# - tzdata: to set correct timezone
# - cups & cups-client: printing system and client tools
# - ghostscript: required for PDF processing
# Also install Python dependencies: reportlab (for PDF generation), requests (for notifications)
RUN apt-get update && \
    apt-get install -y cron tzdata cups cups-client ghostscript vim-tiny curl && \
    pip install reportlab requests cron-descriptor && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy Python scripts into container
COPY scripts/generate_pdf.py /home/generate_pdf.py
COPY scripts/generate_empty_pdf.py /home/generate_empty_pdf.py
COPY scripts/send_notification.py /home/send_notification.py
COPY scripts/describe_cron.py /home/describe_cron.py

# Copy entrypoint and make it executable
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Copy auxiliary test script and make it executable
COPY scripts/test_empty.sh /home/test_empty.sh
RUN chmod +x /home/test_empty.sh

# Set timezone (default: Europe/Brussels)
ENV TZ=Europe/Brussels
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Setup cron job:
# - Copy cron job config
# - Copy weekly print script
# - Set correct permissions
COPY cron/cronjob /etc/cron.d/color-printer
COPY scripts/weekly_print.sh /usr/local/bin/weekly_print.sh
RUN chmod +x /usr/local/bin/weekly_print.sh 
RUN chmod 0644 /etc/cron.d/color-printer
RUN crontab /etc/cron.d/color-printer  # Register cron job

# Copy custom CUPS configuration
COPY conf/cupsd.conf /etc/cups/cupsd.conf

# Copy VERSION
COPY VERSION /VERSION

# Healthcheck
COPY scripts/healthcheck.sh /healthcheck.sh
RUN chmod +x /healthcheck.sh

HEALTHCHECK CMD /healthcheck.sh

# Use custom entrypoint to start CUPS and cron
ENTRYPOINT ["/entrypoint.sh"]
