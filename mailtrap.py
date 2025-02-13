import smtplib

sender = "Private Person <hello@demomailtrap.com>"
receiver = "A Test User <steve_a_haigh@hotmail.com>"

message = f"""\
Subject: Hi Mailtrap
To: {receiver}
From: {sender}

This is a test e-mail message."""

with smtplib.SMTP("bulk.smtp.mailtrap.io", 587) as server:
    server.starttls()
    server.login("api", "011a55dad77ccac901ee548f69036344")
    server.sendmail(sender, receiver, message)