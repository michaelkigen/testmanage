from django.contrib import admin
from django.urls import path,include
import users
import Profile
import menu
import mpesa
urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/',include('users.urls')),
    path('menu/',include('menu.urls')),
    path('mpesa/',include('mpesa.urls')),
    path('profile/',include('Profile.urls'))
]
