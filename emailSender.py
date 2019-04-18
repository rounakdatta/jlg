import os

def sendReportMail(title, content):
    import smtplib
    from email.mime.text import MIMEText

    smtp_ssl_host = 'smtp.yandex.com'
    smtp_ssl_port = 465
    username = os.environ.get('Y_EMAIL')
    password = os.environ.get('Y_PWD')
    sender = os.environ.get('Y_EMAIL')
    targets = [os.environ.get('RECP_1'), os.environ.get('RECP_2')]

    msg = MIMEText(content)
    msg['Subject'] = title
    msg['From'] = sender
    msg['To'] = ', '.join(targets)

    server = smtplib.SMTP_SSL(smtp_ssl_host, smtp_ssl_port)
    server.login(username, password)
    server.sendmail(sender, targets, msg.as_string())
    server.quit()