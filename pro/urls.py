from django.contrib import admin
from django.urls import path,include
import users
import Profile
import menu
import mpesa
import reciept
import chatbox
import records
import review
urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/',include('users.urls')),
    path('menu/',include('menu.urls')),
    path('mpesa/',include('mpesa.urls')),
    path('reciept/',include('reciept.urls')),
    path('profile/',include('Profile.urls')),
    path('chat/',include('chatbox.urls')),
    path('reviews/',include('review.urls')),
    path('records/',include('records.urls'))
]
