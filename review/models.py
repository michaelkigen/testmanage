from django.db import models
from menu.models import Menu_Object
import uuid
from users.models import User

# Create your models here.
class OveralReview(models.Model):
    product = models.ForeignKey(Menu_Object, on_delete=models.CASCADE, related_name='OveralReview')
    overal_rating = models.FloatField(default= 0.00)
    
    
class Review(models.Model):
   
    review_id = models.UUIDField(default=uuid.uuid4 ,primary_key= True,auto_created= True, editable=False)
    product = models.ForeignKey(Menu_Object, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(default= 1)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
class NotifY(models.Model):
    message = models.TextField()
    posted_time = models.DateTimeField(auto_now_add=True)
