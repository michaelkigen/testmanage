
from django.db import models
import uuid
from users.models import User
from django.conf import settings
from cloudinary.models import CloudinaryField
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

FOOD_CATEGORY =(
    ('Break_fast','break_fast'),
    ('Lunch','lunch'),
    ('Super','super')
)


       
class Menu_Object(models.Model):
    food_id = models.UUIDField(default=uuid.uuid4, primary_key= True , auto_created=True, editable=True)
    food_name = models.CharField(max_length=244)
    food_image = models.ImageField(upload_to='food_images',  null=True)
    price = models.FloatField(default= 100.00)
    description = models.TextField()
    is_avilable = models.BooleanField(default=True)
    
   
    def __str__(self):
        return self.food_name
    
    
class Categories(models.Model):
    cartegory_id = models.UUIDField(default=uuid.uuid4 ,primary_key=True,editable=False,auto_created=True)
    category = models.CharField(max_length=20, choices=FOOD_CATEGORY)
    food = models.ForeignKey(Menu_Object, verbose_name=("food"), on_delete=models.CASCADE) 
    
    def __str__(self):
        return self.category   
    
    
class Cart(models.Model):
    cart_id =models.UUIDField(default=uuid.uuid4, primary_key= True , auto_created=True, editable=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart')
    
    def __str__(self):
        return f"Cart ID: {self.cart_id}, User: {self.user.first_name}"
    
    @receiver(post_save, sender=User)
    def create_user_cart(sender, instance, created, **kwargs):
        if created:
            Cart.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_cart(sender, instance, **kwargs):
        instance.cart.save()
        
    def create_order(self):
       
        order = Order.objects.create(user=self.user , state=PENDING_ORDER )

        cart_items = self.cart_item.all()

        for cart_item in cart_items:
            Orderd_Food.objects.create(
                food=cart_item.food,
                order=order,
                quantity=cart_item.quantity
            )

        self.cart_item.all().delete()  # Empty the cart after creating the order

        return order
    
class Add_item_to_cart(models.Model):
    add_to_cart_id = models.UUIDField(default=uuid.uuid4 ,primary_key= True,auto_created= True, editable=False)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="cart_item", null=True, blank=True)
    food = models.ForeignKey(Menu_Object, on_delete=models.CASCADE, blank=True, null=True, related_name='cartitems')
    quantity = models.PositiveIntegerField(default=1)
    
    

PENDING_ORDER = 'p'
COMPLETE_ORDER = 'c'
CANCELED_ORDER = 'f'

STATUS = (
    (PENDING_ORDER , 'Pending'),
    (COMPLETE_ORDER, 'Complete'),
    (CANCELED_ORDER, 'Failed'),
)
MODE_OF_PAYMENTS = (
    ('MPESA','mpesa'),
    ('QCOINS','qcoins')
)

class  Order(models.Model):
    order_id = models.UUIDField(default=uuid.uuid4 ,primary_key= True,auto_created= True, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE , null= True)
    created_at = models.DateTimeField(auto_now_add=True)
    state = models.CharField(max_length=50, choices= STATUS , default= PENDING_ORDER)
    qrc_image = models.ImageField(upload_to='qr_code_images',  null=True)
    reciept = models.FileField(upload_to='reciepts', null= True)
    scaned_time = models.DateTimeField( auto_now=True, auto_now_add=False, null= True)
    payment_mode =models.CharField(max_length=50, choices= MODE_OF_PAYMENTS , default= 'mpesa')
    
    class Meta:
        unique_together = ('order_id',)
    
    def __str__(self):
        return f"Order ID: {self.order_id} User: {self.user}"
    
class Orderd_Food(models.Model):
    food  = models.ForeignKey(Menu_Object , on_delete= models.CASCADE, related_name='food')
    order = models.ForeignKey(Order, on_delete=models.CASCADE,related_name='ordered_food')
    quantity = models.PositiveIntegerField(default=1) 
    
    