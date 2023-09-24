from smtplib import SMTPException
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Verifications
import string
import random
from django.core.mail import EmailMultiAlternatives


def generate_verification_code(length=4):
    characters = string.digits  # You can customize the characters used in the verification code
    verification_code = ''.join(random.choice(characters) for _ in range(length))
    return verification_code




def send_Verification_Email(request,email, name, code):
    verification_code = code
    

    # Set the verification code and its expiration time
    verifications = Verifications.objects.create(email = email ,verification_code=verification_code, verification_code_sent=datetime.now(timezone.utc))
    verifications.save()

    # Render the HTML email template with dynamic content
    html_message = render_to_string('email.html', {'recipient_name': name, 'verification_code': verification_code})
    plain_message = strip_tags(html_message)  # Strip HTML tags for the plain text version

    # Send email
    try:
        send_mail(
            'Verification Code - Your Website',
            plain_message,
            'michaelmaiyo44@gmail.com',  # Sender's email address
            [email],  # Recipient's email address
            html_message=html_message  # Attach the HTML message
        )
        # Email sent successfully
        return 'Email sent successfully.'
    except SMTPException as e:
        # Handle the exception
        print(f"Email sending failed: {e}")
        # Provide an error message to the user
        return 'Failed to send the email. Please try again later.'



def Orderdfood_emailer(request, email, fName, Lname, ordered_food):
    subject = 'Thank You for Your Food Order'
    from_email =  'michaelmaiyo44@gmail.com' 
    to_email = email

    # Render the HTML content from the template
    html_message = render_to_string('email_template.html', {'ordered_food': ordered_food, 'fName': fName, 'Lname': Lname})

    # Create the plain text version of the email
    plain_message = strip_tags(html_message)

    # Create the email message
    email_message = EmailMultiAlternatives(subject, plain_message, from_email, [to_email])
    email_message.attach_alternative(html_message, 'text/html')

    try:
        email_message.send()
        # Email sent successfully
        return 'Email sent successfully.'
    except Exception as e:
        # Handle the exception
        print(f"Email sending failed: {e}")
        # Provide an error message to the user
        return 'Failed to send the email. Please try again later.'
