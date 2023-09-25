from django.urls import path,include
from .views import RecieptAPIviewset

urlpatterns = [
    path("reciepts/",RecieptAPIviewset.as_view({'get': 'list'}), name="reciepts")
]
