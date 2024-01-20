from oauth import get_gmail_client
from helpers import create_message, send_message

secrets_path = '/home/lyle/tutorial/titanic_analysis/secrets.json'
gmail_client = get_gmail_client(secrets_path)
message = create_message()
message = send_message(gmail_client, message)
print(message)