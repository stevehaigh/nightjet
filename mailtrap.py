import requests
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

subject = "nightjet test"
body_text = "blah"

# Build the mail payload
mail_payload = {
        "from": {
            "email": "hello@demomailtrap.com"
        },
        "to": [
            {
                "email": "steve_a_haigh@hotmail.com" 
            }
    ],
    "subject": subject,
    "text": body_text,
    "category": "transactional"
}



try:
    # Send the email via Mailtrap's API
    headers = {
        "Authorization": f"Bearer xxxxxxxxxxxxxxxxxxxxxxxx",
        "Content-Type": "application/json"
    }

    response = requests.post(
        "https://send.api.mailtrap.io/api/send",
        json=mail_payload,
        headers=headers
    )

    if response.status_code == 200:
        print("Email sent successfully via Mailtrap API")
    else:
        print(f"Failed to send email via Mailtrap API, status code: {response.status_code}, response: {response.text}")

except Exception as e:
    print(e)
