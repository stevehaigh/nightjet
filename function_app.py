import logging
import azure.functions as func
import requests
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

app = func.FunctionApp()


@app.timer_trigger(
    schedule="0 0 */6 * * *",
    arg_name="myTimer",
    run_on_startup=True,
    use_monitor=False,
)
def timer_trigger(myTimer: func.TimerRequest) -> None:
    if myTimer.past_due:
        logging.info("The timer is past due!")

    logging.info("Python timer trigger function executed.")

    url = (
        "https://www.nightjet.com/nj-booking-ocp/connection/8400058/8100108/2025-08-31"
    )
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if "connections" in data and len(data["connections"]) > 0:
            send_email(True)
        else:
            send_email(False)
    else:
        logging.error(
            f"Failed to fetch data from the URL, status code: {response.status_code}"
        )


def send_email(is_bookable: bool):
    subject = "nightjet tickets not yet available"
    body_text = "Tickets not available yet"

    if is_bookable:
        subject = "NIGHTJET Tickets Available"
        body_text = "Tickets are available. Check the details at https://www.nightjet.com/en/ticket-buchen#/home"

    # Build the email
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = "hello@demomailtrap.com"  # Adjust if needed
    message["To"] = "steve_a_haigh@hotmail.com"

    # Attach the plain text body
    message.attach(MIMEText(body_text, "plain"))

    # Retrieve Mailtrap SMTP credentials from environment variables
    mailtrap_username = os.environ.get("MAILTRAP_USERNAME")
    mailtrap_password = os.environ.get("MAILTRAP_PASSWORD")
    if not mailtrap_username or not mailtrap_password:
        logging.error("Mailtrap SMTP credentials not set in environment variables.")
        return

    try:
        # Connect to Mailtrap SMTP and send the email
        with smtplib.SMTP("smtp.mailtrap.io", 587) as server:
            server.login(mailtrap_username, mailtrap_password)
            server.sendmail(
                message["From"],
                [message["To"]],
                message.as_string()
            )
        logging.info("Email sent successfully via SMTP (Mailtrap Sandbox)")

    except Exception as e:
        logging.error(f"An error occurred while sending email via SMTP: {e}")
