import logging
import os
import requests
import azure.functions as func
from azure.communication.email import EmailClient

app = func.FunctionApp()
schedule_chron_expression = os.environ.get("SCHEDULE_CHRON_EXPRESSION")

@app.timer_trigger(
    schedule=schedule_chron_expression,
    arg_name="myTimer",
    run_on_startup=False,
    use_monitor=False,
)
def timer_trigger(myTimer: func.TimerRequest) -> None:
    """
    Timer trigger function that gets executed based on a schedule.
    Args:
        myTimer (func.TimerRequest): The timer request object that contains the schedule information.
    Returns:
        None
    """
    if myTimer.past_due:
        logging.info("The timer is past due!")
    logging.info("Python timer trigger function executed.")
    main()

def main():
    """
    Main function that checks if tickets are available and triggers an email if they are.
    """
    date_to_check = os.environ.get("DATE_TO_CHECK")
    url_to_check = f"https://www.nightjet.com/nj-booking-ocp/connection/8400058/8100108/{date_to_check}"

    if tickets_are_available(url_to_check):
        send_tickets_available_email()

    send_heartbeat()
        

def tickets_are_available(url: str) -> bool:
    """
    Checks the specified URL for available ticket connections.

    Returns:
        bool: True if connections are found, otherwise False.
    """
    try:
        logging.info(f"Checking the site: {url}")
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            return "connections" in data and len(data["connections"]) > 0
        
        return False

    except Exception as e:
        logging.error(f"An error occurred while checking the site: {e}")
        return False

def compose_tickets_available_message(date_to_check: str) -> dict:
    """
    Composes the email message dictionary for tickets availability.
    """
    subject = "🚂 NIGHTJET Tickets Now Available"
    body_text = f'Tickets are available for {date_to_check}. This is a reminder to check dates and reset this app :)'
    return {
        "subject": subject,
        "body_text": body_text,
        "html": f"""
            <html>
                <body>
                    <h1>{body_text}</h1>
                </body>
            </html>
        """
    }

def send_email_message(email_message: dict):
    """
    Sends the email message using Azure Communication Services.
    """
    connection_string = os.environ.get("COMMUNICATION_SERVICES_CONNECTION_STRING")
    if not connection_string:
        logging.error("Connection string is not set.")
        return
    
    client = EmailClient.from_connection_string(connection_string)
    sender_address = os.environ.get("SENDER_EMAIL_ADDRESS")
    recipient_address = os.environ.get("RECIPIENT_EMAIL_ADDRESS")
    if not sender_address or not recipient_address:
        logging.error("Sender or recipient email address is not set.")
        return
    
    message = {
        "senderAddress": sender_address,
        "recipients": {"to": [{"address": recipient_address}]},
        "content": {
            "subject": email_message["subject"],
            "plainText": email_message["body_text"],
            "html": email_message["html"],
        },
    }

    poller = client.begin_send(message)
    poller.result()
    logging.info("Message sent")

def send_tickets_available_email():
    """
    Sends an email using Azure Communication Services if tickets are available.
    """
    try:
        date_to_check = os.environ.get("DATE_TO_CHECK")
        email_message = compose_tickets_available_message(date_to_check)
        send_email_message(email_message)
    except Exception as e:
        logging.error(f"An error occurred while sending the email: {e}")


def send_heartbeat():
    """
    Sends a heartbeat email to indicate the function is running.
    This function only sends the email on Sundays if the current time is within 90 minutes of HEARTBEATTIME.
    HEARTBEATTIEM is in the format HH:MM.
    """
    from datetime import datetime

    try:
        heartbeat_time_str = os.environ.get("HEARTBEATTIME")
        if not heartbeat_time_str:
            logging.info("HEARTBEATTIME not set; skipping heartbeat email.")
            return

        # Parse the heartbeat time
        heartbeat_time = datetime.strptime(heartbeat_time_str, "%H:%M").replace(
            year=datetime.now().year,
            month=datetime.now().month,
            day=datetime.now().day
        )
        now = datetime.now()
        difference = now - heartbeat_time

        # Only send email on specified day if within 60 minutes of HEARTBEATTIME
        # Get weekday from environment variable (default to 6/Sunday if not set)
        heartbeat_weekday = int(os.environ.get("HEARTBEAT_WEEKDAY", "6"))
        
        # Check if it's the right weekday, the time is within 60 minutes after heartbeat_time
        if now.weekday() == heartbeat_weekday and 0 <= difference.total_seconds() < 60 * 60:
            date_to_check = os.environ.get("DATE_TO_CHECK", "Unknown date")
            email_message = {
            "subject": "Nightjet Heartbeat",
            "body_text": f"The function is still running and checking for tickets on {date_to_check}.",
            "html": f"<html><body><p>The function is still running and checking for tickets on {date_to_check}.</p></body></html>",
            }
            send_email_message(email_message)

    except Exception as e:
        logging.error(f"An error occurred in send_heartbeat: {e}")
