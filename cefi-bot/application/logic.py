import sendgrid
from sendgrid.helpers.mail import *

def send_email_update(message,email_api_key):
    sg = sendgrid.SendGridAPIClient(api_key=email_api_key)
    from_email = Email("johannes.esbjornsson@gmail.com")
    to_email = To("johannes.esbjornsson@gmail.com")
    subject = "Crypto Update"
    content = Content("text/plain", message)
    mail = Mail(from_email, to_email, subject, content)
    response = sg.client.mail.send.post(request_body=mail.get())      
