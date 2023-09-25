from django.db import models
import uuid
# Create your models here.
class Reciepts(models.Model):
    reciept = models.ImageField(upload_to='department_reciepts',  null=True)
    created_time = models.DateField(auto_now= True)
    
    
