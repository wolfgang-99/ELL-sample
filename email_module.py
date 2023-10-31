import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage


def send_email_with_image(sender_email, sender_password, receiver_email, subject, paragraphs, image_path):
    # Create a multipart message container
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    # Create the HTML content of the email
    html = f'''
       <html>
           <body>
               <p><img src="cid:image"></p>
               {''.join(f"<p>{p}</p>" for p in paragraphs)}
           </body>
       </html>
       '''

    # Attach the HTML content to the email
    msg.attach(MIMEText(html, 'html'))

    # Open the image file
    with open(image_path, 'rb') as image_file:
        # Create a MIME image object
        image = MIMEImage(image_file.read(), name='logo.png')

        # Define the image ID
        image.add_header('Content-ID', '<image>')
        image.add_header('Content-Disposition', 'inline', filename='logo.png')

        # Attach the image to the email
        msg.attach(image)
    try:
        # Establish a secure connection with the SMTP server
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.set_debuglevel(1)

        # Login to the sender's email account
        server.login(sender_email, sender_password)

        # Send the email
        server.send_message(msg)

        # Clean up the connection
        server.quit()

        return True
    except Exception as e:
        print(f"Email sending error: {str(e)}")
        return False


def read_message(file_path, register_name, register_email, **kwargs):
    # kwargs argument
    deposit_amount = kwargs.get('deposit_amount')
    wallet = kwargs.get('wallet')

    with open(file_path, 'r') as email_text:
        message = email_text.read()
        message = message.replace("[Name]", register_name)
        message = message.replace("[Company Name]", "Ellextra")
        message = message.replace("[email]", register_email)
        if deposit_amount and wallet:
            message = message.replace("[deposite amount]", deposit_amount)
            message = message.replace("[wallet]", wallet)

        paragraphs = message.split('\n\n')  # Assuming paragraphs are separated by two newline characters
    return paragraphs


def email_user(register_email, register_name, file_path):

    if register_email:
        sender_email = 'email.test.sample2023@gmail.com'
        sender_password = 'ritd jara flsf gjso'
        subject = 'test team'
        image_path = 'static/assets/images/logo.jpeg'
        file_path = file_path

        paragraphs = read_message(file_path, register_name, register_email)
        Email_sent = send_email_with_image(sender_email=sender_email, sender_password=sender_password,
                                           receiver_email=register_email, subject=subject, paragraphs=paragraphs,
                                           image_path=image_path)

        if Email_sent:
            print(f'email sent to user_email: {register_email}')
            return register_email


def email_admin(admin_email, register_email, register_name, file_path, deposit_amount, wallet):

    if admin_email:
        sender_email = 'kristaspace0@gmail.com'
        sender_password = 'pkhmlmmqhpcwjhob'
        subject = 'test team'
        image_path = 'static/assets/images/logo.png'
        file_path = file_path

        paragraphs = read_message(file_path, register_name, deposit_amount=deposit_amount,
                                  wallet=wallet, register_email=register_email)
        Email_sent = send_email_with_image(sender_email=sender_email, sender_password=sender_password,
                                           receiver_email=admin_email, subject=subject, paragraphs=paragraphs,
                                           image_path=image_path)

        if Email_sent:
            print('email sent to admin')


# email_admin(register_email='wolf@gmail.com', register_name= 'wolf', admin_email="blazealex348@gmail.com",
#             file_path="Email text/Admin_email_notification_deposite",
#             deposit_amount='500', wallet='btc')
# email_user(register_email="wolfworldtrade@gmail.com", register_name='wolf', file_path='Email text/Deposite_Email_text.txt')
