from email.message import EmailMessage
from base64 import urlsafe_b64encode
from googleapiclient.errors import HttpError


def create_message():
    try:
        message = EmailMessage()
        message.set_content('content')
        message['To'] = 'lyleokothdev@gmail.com'
        message['From'] = 'lyceokoth@gmail.com'
        message['Subject'] = 'Automated draft'
        # encoded message
        encoded_message = urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {
            'raw': encoded_message
        }
    except HttpError as error:
        print(f'An error occurred: {error}')
        create_message = None
    return create_message

def send_message(gmail_client, message):
    try:
        send_message = (gmail_client.users().messages().send
                        (userId="me", body=message).execute())
        print(f'Message Id: {send_message["id"]}')
    except HttpError as error:
        print(f'An error occurred: {error}')
        send_message = None
    return send_message