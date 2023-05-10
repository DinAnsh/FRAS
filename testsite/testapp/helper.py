from django.core.mail import send_mail
from django.conf import settings

def send_forget_password_mail(email, meta):
    subject = "Reset your FRAS password"
    message = f'''Hello,
We received a request to reset the password for your account for this email address. To initiate the password reset process for your account, click the link below. 

{meta["scheme"]}://{meta["host"]}/change_password/{meta["token"]}/

Note: the link will be validated only for 2 minutes.

This link can only be used once. If you need to reset your password again, please visit http://127.0.0.1:8000/ and request another reset.

If you did not make this request, you can simply ignore this email.

Sincerely,
The FRAS Team
'''
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)
    return True