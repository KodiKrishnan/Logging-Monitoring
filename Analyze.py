import time
import re
import os
import smtplib
import argparse
import curses
import traceback
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from collections import deque
from datetime import datetime, timedelta

# Constants
LOG_FILE_PATH = "./sample.log"
ERROR_PATTERN = re.compile(r"ERROR")
ALERT_THRESHOLD = 1
ALERT_WINDOW = timedelta(seconds=60)

# Email configuration from environment variables
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")

# Runtime storage
error_timestamps = deque()
log_messages = deque(maxlen=10)
recent_errors = deque(maxlen=20)

def parse_log_line(line):
    try:
        parts = line.strip().split()
        timestamp_str = parts[0]
        level = parts[1]
        message = " ".join(parts[2:])
        timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d")
        return timestamp, level, message
    except (ValueError, IndexError):
        return None, None, None

def send_email_alert(count):
    subject = 'Log Analyzer Alert'
    body = f"ALERT: {count} errors detected in the last {ALERT_WINDOW.seconds} seconds!"
    
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER

    # Attach the main text
    msg.attach(MIMEText(body, 'plain'))

    # Attach error log as file
    error_log_content = "\n".join(recent_errors)
    attachment = MIMEApplication(error_log_content, Name="error_log.txt")
    attachment['Content-Disposition'] = 'attachment; filename="error_log.txt"'
    msg.attach(attachment)

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.connect(SMTP_SERVER, SMTP_PORT)
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
    except Exception as e:
        log_messages.appendleft(f"[EMAIL ERROR] {e}")
        log_messages.appendleft(traceback.format_exc())

def check_alert():
    now = datetime.now()
    while error_timestamps and error_timestamps[0] < now - ALERT_WINDOW:
        error_timestamps.popleft()

    if len(error_timestamps) >= ALERT_THRESHOLD:
        alert_msg = f"[ALERT] {len(error_timestamps)} errors in last {ALERT_WINDOW.seconds} seconds!"
        log_messages.appendleft(alert_msg)
        send_email_alert(len(error_timestamps))

def follow_log(log_file, level_filter, keyword_filter, screen):
    with open(log_file, "r") as f:
        f.seek(0, 2)
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.5)
                continue

            timestamp, level, message = parse_log_line(line)
            if not timestamp:
                continue

            if level_filter and level != level_filter:
                continue
            if keyword_filter and keyword_filter not in message:
                continue

            now = datetime.now()
            if ERROR_PATTERN.search(line):
                error_timestamps.append(now)
                error_msg = f"[ERROR] {line.strip()}"
                recent_errors.append(error_msg)
                log_messages.appendleft(error_msg)
                check_alert()
            else:
                log_messages.appendleft(f"[LOG] {line.strip()}")

            draw_ui(screen)

def draw_ui(screen):
    screen.clear()
    screen.addstr(0, 0, "📊 Real-time Log Monitor")
    for idx, msg in enumerate(log_messages):
        if idx >= curses.LINES - 2:
            break
        screen.addstr(idx + 2, 0, msg[:curses.COLS - 1])
    screen.refresh()

def main():
    parser = argparse.ArgumentParser(description="Real-time log analyzer with alerts and dashboard.")
    parser.add_argument("--file", default=LOG_FILE_PATH, help="Log file path")
    parser.add_argument("--level", help="Log level filter (e.g., ERROR, INFO)")
    parser.add_argument("--keyword", help="Filter logs containing this keyword")
    args = parser.parse_args()

    def wrapped(stdscr):
        follow_log(args.file, args.level, args.keyword, stdscr)

    curses.wrapper(wrapped)

if __name__ == "__main__":
    main()
