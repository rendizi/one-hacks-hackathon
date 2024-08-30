import os 

def send_summarize(to: str, summarizes: dict):
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    smtp_server = 'smtp.google.com'  
    smtp_port = 587 
    smtp_user = os.getenv("EMAIL_ADDRESS")
    smtp_password = os.getenv("EMAIL_PASSWORD")

    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = to
    msg['Subject'] = 'Daily Instagram Stories Summary'

    body = "Here is the summarized stories:\n\n"
    for username, description in summarizes.items():
        body += f"Username: {username}\nDescription: {description}\n\n"
    
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")
