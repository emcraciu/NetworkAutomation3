import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

EMAIL_SENDER = "ionelaamatei2004@gmail.com"
EMAIL_PASS = "uuvl lall csea qgqe"
EMAIL_RECEIVER = "ionelaamatei2004@gmail.com"

def send_email(subject, message):
    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL_SENDER
        msg["To"] = EMAIL_RECEIVER
        msg["Subject"] = subject

        msg.attach(MIMEText(message, "plain"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASS)
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())

        print(" Email trimis cu succes!")
    except Exception as e:
        print(f" Eroare la trimiterea emailului: {e}")
