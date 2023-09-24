from typing import Optional
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.base_user import AbstractBaseUser
from .models import User

class CustomUserBackend(BaseBackend):
    def authenticate(self , phone_number = None , password = None, **kwargs):
        try:
            user = User.objects.get(phone_number = phone_number)
        except user.DoesNotExist:
            return None
        
        if user.check_password(password):
            return user
        return None
    def get_user(self, user_id):
        try:
            return User.objects.get(pk = user_id)
        except User.DoesNotExist:
            return None
        
        