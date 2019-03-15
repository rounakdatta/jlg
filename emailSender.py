def sendReportMail(title, content):
    import smtplib
    from email.mime.text import MIMEText

    smtp_ssl_host = 'smtp.yandex.com'
    smtp_ssl_port = 465
    username = 'asslpl@yandex.com'
    password = 'tempPassword'
    sender = 'asslpl@yandex.com'
    targets = ['rounakdatta12@gmail.com',]

    msg = MIMEText(content)
    msg['Subject'] = title
    msg['From'] = sender
    msg['To'] = ', '.join(targets)

    server = smtplib.SMTP_SSL(smtp_ssl_host, smtp_ssl_port)
    server.login(username, password)
    server.sendmail(sender, targets, msg.as_string())
    server.quit()