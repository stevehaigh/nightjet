from azure.communication.email import EmailClient

def main():
    try:
        connection_string = "**************"
        client = EmailClient.from_connection_string(connection_string)

        message = {
            "senderAddress": "*********",
            "recipients": {
                "to": [{"address": "*************"}]
            },
            "content": {
                "subject": "Test Email from test application",
                "plainText": "Hello world via email.",
                "html": """
				<html>
					<body>
						<h1>Hello world via email.</h1>
					</body>
				</html>"""
            },            
        }

        poller = client.begin_send(message)
        result = poller.result()
        print("Message sent: ", result.message_id)

    except Exception as ex:
        print(ex)

main()
