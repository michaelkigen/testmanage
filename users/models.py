from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager
from django.utils import timezone

class BaseUser(BaseUserManager):
    def create_user(self,phone_number,email ,first_name,last_name,password):
        if not phone_number:
            raise ValueError('please enter your phone_number')
        user = self.model(
            email = self.normalize_email(email),
            phone_number=phone_number,
            first_name=first_name,
            last_name=last_name,
            
        )
        user.set_password(password)
        user.save(using = self.db)
        return user
    
    def create_superuser(self,phone_number,email,first_name,last_name,password):
        
        super_user =self.create_user(
            phone_number,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            
        )
        super_user.is_admin =True
        super_user.save(using = self.db)
        return super_user
    
class User(AbstractBaseUser):
    phone_number =models.CharField(unique= True ,max_length=20)
    email = models.EmailField(verbose_name='email', max_length=202)
    first_name = models.CharField(max_length= 30)
    last_name = models.CharField(max_length= 30)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default= False)
    is_staff = models.BooleanField(default= False)
    is_ccare = models.BooleanField(default= False)
    is_verified = models.BooleanField(default=False)
    
    
    objects =  BaseUser()
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS=['email','first_name','last_name']
    
    def __str__(self) -> str:
        return self.phone_number
    
    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin


class Verifications(models.Model):
    email = models.EmailField(verbose_name='email', max_length=202,null= True)
    verification_code = models.CharField(max_length=6, blank=True, null=True)
    verification_code_sent = models.DateTimeField(blank=True, null=True)
    
    

    '''@classmethod
    def create_verification(cls, user, code):
        verification = user.verifications.create(verification_code=code)
        return verification
'''


class TokenBlacklist(models.Model):
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.token
