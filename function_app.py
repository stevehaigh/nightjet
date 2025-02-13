import datetime
import logging
import os
import requests
import azure.functions as func
from azure.communication.email import EmailClient

app = func.FunctionApp()

date_to_check = os.environ.get("DATE_TO_CHECK")
url_to_check = f"https://www.nightjet.com/nj-booking-ocp/connection/8400058/8100108/{date_to_check}"

@app.timer_trigger(
    schedule="0 0 */1 * * *",
    arg_name="myTimer",
    run_on_startup=True,
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
    if tickets_are_available(url_to_check):
        send_email()

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

def send_email():
    """
    Sends an email using Azure Communication Services.

    Retrieves configuration from environment variables and constructs a message object.
    """
    try:
        subject = "🚂 NIGHTJET Tickets Now Available"
        body_text = f'Tickets are available for {date_to_check}. Check the details at <a href="https://www.nightjet.com/en/ticket-buchen#/home">Nightjet Booking</a>'

        connection_string = os.environ.get("COMMUNICATION_SERVICES_CONNECTION_STRING")
        if not connection_string:
            logging.error("Connection string is not set in environment variables.")
            return
        
        client = EmailClient.from_connection_string(connection_string)
        
        sender_address = os.environ.get("SENDER_EMAIL_ADDRESS")
        recipient_address = os.environ.get("RECIPIENT_EMAIL_ADDRESS")
        if not sender_address or not recipient_address:
            logging.error("Sender or recipient email address is not set in environment variables.")
            return
        
        message = { 
            "senderAddress": sender_address,
            "recipients": {"to": [{"address": recipient_address}]},
            "content": {
                "subject": f"{subject}",
                "plainText": f"{body_text}",
                "html": f"""
                <html>
                    <body>
                        <h1>{body_text}</h1>
                    </body>
                </html>""",
            },
        }

        poller = client.begin_send(message)
        result = poller.result()
        logging.info("Message sent")

    except Exception as e:
        logging.error(f"An error occurred while sending the email: {e}")
