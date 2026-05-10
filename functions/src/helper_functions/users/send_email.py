from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from src.shared import logger

def send_email(message: Mail):
    """
    Sends an email using SendGrid.

    Parameters:
    message (Mail): The email message to be sent.
    
    Raises:
    Exception: If there is an error sending the email.
    """
    try:
        # Retrieve the SendGrid API key from a file
        with open('./sendgrid_api_key.txt', 'r') as file:
            sendgrid_api_key = file.read().strip()

        if not sendgrid_api_key:
            raise ValueError("SendGrid API key is not found in the file.")

        # Initialize SendGrid API client
        sg = SendGridAPIClient(sendgrid_api_key)
        
        # Send the email
        response = sg.send(message)
        logger.info(f"Email sent successfully with status code: {response.status_code}")

    except Exception as e:
        # Provide detailed error information
        raise Exception(f"An error occurred while sending email: {str(e)}")