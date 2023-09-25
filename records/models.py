from django.db import models

# Create your models here.
class Records(models.Model):
    food = models.CharField( max_length=50)
    tquantity = models.IntegerField(default=0)
    tamount  = models.IntegerField(default=0)
    
    
class DailyRecord(models.Model):
    measuredFood = models.CharField( max_length=100,null = True)
    expectedQuantity = models.CharField(max_length=100,null= True)
    food = models.CharField( max_length=100)
    quantity = models.IntegerField()
    amount  = models.IntegerField()
    date = models.DateTimeField( auto_now_add=True)