from django.db import models
from users.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from mpesa.models import PaymentTransaction

# Create your models here.
class Profile(models.Model):
    profile_pic = models.ImageField( upload_to='profile_images', null = True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL , on_delete= models.CASCADE, related_name= 'profile')
    points = models.DecimalField(max_digits=6,decimal_places=1,default= 1)
    
    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()