
import os
import sys
import requests
import smtplib

from email.message import EmailMessage

API_TOKEN = os.environ.get("CLICKUP_TOKEN")

# SMTP configuration
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USERNAME = os.environ.get("SMTP_USERNAME")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")
EMAIL_FROM = os.environ.get("EMAIL_FROM", SMTP_USERNAME)

# Project manager email
PROJECT_MANAGER_EMAIL = os.environ.get("PROJECT_MANAGER_EMAIL")


def get_task(task_id):
    url = f"https://api.clickup.com/api/v2/task/{task_id}"
    headers = {"Authorization": API_TOKEN}
    response = requests.get(url, headers=headers)

    if response.status_code == 404:
        return None

    response.raise_for_status()
    return response.json()


def update_status(task_id, new_status):
    url = f"https://api.clickup.com/api/v2/task/{task_id}"
    headers = {
        "Authorization": API_TOKEN,
        "Content-Type": "application/json"
    }
    body = {"status": new_status}

    response = requests.put(url, headers=headers, json=body)
    response.raise_for_status()

    print(f"Updated {task_id} to status: {new_status}")


def send_status_email(task, old_status, new_status):
    """Send a status update notification to the project manager."""

    if not PROJECT_MANAGER_EMAIL:
        print("WARNING: Project manager email is not configured.")
        return

    if not all([SMTP_USERNAME, SMTP_PASSWORD, EMAIL_FROM]):
        print("WARNING: SMTP configuration is incomplete.")
        return

    task_name = task.get("name", "Unnamed ClickUp task")
    task_url = task.get("url", "")

    message = EmailMessage()
    message["Subject"] = f"ClickUp status update: {task_name}"
    message["From"] = EMAIL_FROM
    message["To"] = PROJECT_MANAGER_EMAIL

    message.set_content(
        f"""Hello Project Manager,

The status of a ClickUp task has changed.

Task: {task_name}
Previous status: {old_status}
New status: {new_status}
Task ID: {task.get('id', 'Unknown')}
Task URL: {task_url or 'Not available'}

This notification was sent automatically by the GitLab CI/CD pipeline.
"""
    )

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(message)

        print(
            f"Email notification sent to project manager: "
            f"{PROJECT_MANAGER_EMAIL}"
        )

    except (smtplib.SMTPException, OSError) as error:
        # Email failure must not interrupt ClickUp synchronization.
        print(
            "WARNING: Status updated, but email notification failed: "
            f"{error}"
        )


if __name__ == "__main__":
    task_id = sys.argv[1]
    new_status = sys.argv[2]

    task = get_task(task_id)

    if not task:
        print(f"No task found with ID {task_id}")
        sys.exit(1)

    # Retrieve the previous status before updating
    old_status = task.get("status", {}).get("status", "Unknown")

    # Original ClickUp functionality
    update_status(task_id, new_status)

    # Additional email notification
    send_status_email(task, old_status, new_status)
