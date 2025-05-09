
# Log Analyzer with Alerts and Dashboard

This project is a real-time log analyzer that monitors a log file for errors and sends email alerts when a predefined threshold of errors is reached within a specified time window. The log analyzer also provides a simple curses-based dashboard that displays recent log entries.

## Project Setup

### Prerequisites

- Docker (for containerization)
- Docker Compose (for multi-container orchestration)
- Python 3.12
- A valid SMTP configuration for sending email alerts (e.g., AWS SES, SMTP server)

### Steps to Set Up and Run

#### 1. Clone the Repository

```bash
git clone https://github.com/your-username/log-analyzer.git
cd log-analyzer
```

#### 2. Environment Setup

Create a `.env` file in the project directory with your email and SMTP credentials. The following keys are required:

```
SMTP_SERVER=<your-smtp-server>
SMTP_PORT=<your-smtp-port>
SMTP_USERNAME=<your-smtp-username>
SMTP_PASSWORD=<your-smtp-password>
EMAIL_SENDER=<sender-email>
EMAIL_RECEIVER=<receiver-email>
```

#### 3. Build and Run with Docker Compose

Once the `.env` file is created, you can use Docker Compose to build and run the project.

```bash
docker-compose up --build
```

This command will build the Docker images and start the application, which will monitor the log file `sample.log` for any errors and send email alerts when the threshold is exceeded.

#### 4. View the Application

Once the application is running, it will start monitoring the log file. The log analyzer's dashboard will be available in your terminal.

To exit the dashboard, press `CTRL+C`.

#### 5. Test Email Alerts

To simulate an error and trigger the email alert, you can modify `sample.log` to include an "ERROR" line, or configure your log-generating application to produce errors.

Example of triggering an error in `sample.log`:

```
2025-05-09 ERROR Something went wrong
```

The system will detect the error, log the error timestamp, and send an email alert if the error count exceeds the predefined threshold.

---

## Docker Setup

### Multi-stage Dockerfile

This project uses a multi-stage Dockerfile to optimize the build process:

1. **Builder Stage**: Installs necessary dependencies for building Python packages (e.g., `gcc`, `libncurses`).
2. **Runtime Stage**: Copies only the required dependencies and application code into a smaller, runtime-only image.

### Docker Compose

We use `docker-compose.yml` to orchestrate the service and ensure the application runs with all necessary configurations.

```yaml
version: "3.8"
services:
  log-analyzer:
    build: .
    environment:
      - SMTP_SERVER=${SMTP_SERVER}
      - SMTP_PORT=${SMTP_PORT}
      - SMTP_USERNAME=${SMTP_USERNAME}
      - SMTP_PASSWORD=${SMTP_PASSWORD}
      - EMAIL_SENDER=${EMAIL_SENDER}
      - EMAIL_RECEIVER=${EMAIL_RECEIVER}
    volumes:
      - .:/app
    ports:
      - "8080:8080"
    restart: unless-stopped
```

---

## Output Overview

When an error is detected in the log file, the application logs the error message in the terminal and sends an email alert to the designated receiver. The email will contain the error count and details of the error occurrences.

### Sample Email:

```
Subject: Log Analyzer Alert
Body: ALERT: 2 errors detected in the last 60 seconds!
```

The application also logs various messages in the terminal and updates the curses-based UI, providing real-time log monitoring.

---

## Troubleshooting

### 1. No email received
Ensure that your SMTP configuration is correct, and check the SMTP service's delivery logs for any errors. For services like AWS SES, ensure the sending email is verified.

### 2. Docker build issues
If you encounter issues during the Docker build process, check the Dockerfile to ensure the necessary dependencies are being installed correctly. You can debug by reviewing the build logs.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
