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
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException


def generate_verification_code(length=4):
    characters = string.digits  # You can customize the characters used in the verification code
    verification_code = ''.join(random.choice(characters) for _ in range(length))
    return verification_code




def send_center_sms(data, user):
    try:
        print('step 1')
        account_sid = "AC94d634c48c7f12dfb8f6af8f0b1614c2"
        auth_token = "50917f3e65a520aeb570f376e9b1a5e5"
        client = Client(account_sid, auth_token)

        # Format the data and user details for better readability
        formatted_data = '\n'.join([f"{item['food_name']}: {item['quantity']} x {item['sub_total']}" for item in data])
        formatted_user = f"User ID: {user['user_id']}\nPhone: {user['user_phone_number']}\nName: {user['user_first_name']} {user['user_last_name']}"

        # Construct the final message
        message_body = f"New order:\n{formatted_data}\n\n{formatted_user}"

        message = client.messages.create(
            body=message_body,
            from_='+13343842451',
            to='+254797759614'
        )
        print('step 3')
    except TwilioRestException as e:
        print(f"Twilio error: {e}")
        # Handle the exception or return an error response
        return f'Failed {e}'




