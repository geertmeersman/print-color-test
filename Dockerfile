# Use Alpine Python base
FROM python:3.11-alpine

# Set environment variables
ENV TZ=Europe/Brussels
ENV DEBIAN_FRONTEND=noninteractive

# Install tini and system dependencies
RUN apk add --no-cache \
        tini \
        cups \
        curl \
        vim \
        tzdata \
        bash \
        busybox-suid \
        libc6-compat \
        python3-dev \
        py3-setuptools \
        py3-wheel \
        dcron
RUN pip install --no-cache-dir \
        flask \
        gunicorn \
        eventlet \
        reportlab \
        requests \
        cron-descriptor

# Set timezone
RUN cp /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Copy Python scripts
COPY scripts/python/*.py /home/

# Copy Flask config
COPY scripts/flask/web_interface.py /home/flask/web_interface.py
COPY scripts/flask/templates /home/flask/templates


# Copy and set permissions for entrypoint and auxiliary scripts
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY scripts/bash/test_empty.sh /home/
RUN chmod +x /home/test_empty.sh

# Cron job setup
COPY cron/cronjob /etc/cron.d/color-printer
COPY scripts/bash/weekly_print.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/weekly_print.sh && \
    chmod 0644 /etc/cron.d/color-printer && \
    crontab /etc/cron.d/color-printer

# CUPS configuration
COPY conf/cupsd.conf /etc/cups/cupsd.conf

# Version file
COPY VERSION /VERSION

# Healthcheck
COPY scripts/bash/healthcheck.sh /healthcheck.sh
RUN chmod +x /healthcheck.sh
HEALTHCHECK CMD /healthcheck.sh

# Use tini as init system
ENTRYPOINT ["/sbin/tini", "--", "/entrypoint.sh"]
