# python:3.13-alpine 3.13.17-alpine3.24
FROM python:3.13-alpine@sha256:bf12ecc0bea3f171d55145dd02c78b5eeb09f30ee2ac9cc2b4c9e4e8f5e30741

ENV TZ=Europe/Brussels
ENV DEBIAN_FRONTEND=noninteractive

RUN apk add --no-cache \
    tini \
    cups \
    cups-filters \
    ghostscript-fonts \
    curl \
    vim \
    tzdata \
    bash \
    gcc \
    musl-dev \
    libffi-dev \
    libc-dev \
    openssl-dev \
    linux-headers \
    busybox-suid \
    libc6-compat \
    python3-dev \
    py3-setuptools \
    py3-wheel \
    py3-pip \
    dcron

RUN pip3 install --upgrade pip

RUN pip install --no-cache-dir \
    flask \
    gunicorn \
    reportlab \
    requests \
    pysnmp>=7.1.30 \
    pyasn1>=0.6.4 \
    cron-descriptor

RUN cp /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

COPY scripts/python/*.py /home/
RUN chmod +x /home/describe_cron.py

COPY scripts/flask/web_interface.py /home/flask/web_interface.py
COPY scripts/flask/templates /home/flask/templates
COPY scripts/flask/static /home/flask/static

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY scripts/bash/test_empty.sh /home/
RUN chmod +x /home/test_empty.sh

COPY cron /home/cron
COPY scripts/bash/weekly_print.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/weekly_print.sh && \
    chmod 0644 /home/cron/cronjob && \
    crontab /home/cron/cronjob

COPY conf/cupsd.conf /etc/cups/cupsd.conf

COPY VERSION /VERSION

COPY scripts/bash/healthcheck.sh /healthcheck.sh
RUN chmod +x /healthcheck.sh
HEALTHCHECK CMD /healthcheck.sh

ENTRYPOINT ["/sbin/tini", "--", "/entrypoint.sh"]
