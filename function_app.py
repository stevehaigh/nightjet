import logging
import azure.functions as func
import requests
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content

app = func.FunctionApp()

@app.timer_trigger(schedule="0 0 */6 * * *", arg_name="myTimer", run_on_startup=False,
                   use_monitor=False) 
def timer_trigger(myTimer: func.TimerRequest) -> None:
    if myTimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function executed.')

    url = "https://www.nightjet.com/nj-booking-ocp/connection/8400058/8100108/2025-08-02"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if "connections" in data and len(data["connections"]) > 0:
            send_email(True)
        else:
            send_email(False)
    else:
        logging.error(f"Failed to fetch data from the URL, status code: {response.status_code}")

def send_email(is_bookable: bool):

    subject = "nightjet tickets not yet available"
    content = Content("text/plain", "Tickets not available yet")


    if is_bookable:
        subject='NIGHTJET Tickets Available',
        content = Content("text/plain", "Tickets are available. Check the details at https://www.nightjet.com/en/ticket-buchen#/home")


    message = Mail(
        from_email='steve_a_haigh@hotmail.com',
        to_emails='steve_a_haigh@hotmail.com',
        subject=subject,
        plain_text_content=content        
    )

    mail_json = message.get()

    try:
        sendgrid_api_key = os.environ.get('SENDGRID_API_KEY')
        
        if not sendgrid_api_key:
            logging.error("SendGrid API key not found.")
            return
        
        sg = SendGridAPIClient(sendgrid_api_key)
        response = sg.client.mail.send.post(request_body=mail_json)
        logging.info(f"Email sent successfully with status code {response.status_code}")
    except Exception as e:
        logging.error(f"An error occurred with Sendmail: {e}")
        logging.error(response.body) 