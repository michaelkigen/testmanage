from django.urls import  path
from .views import (User_registration,Login_View,LogoutView,PhoneNumberCheckerView,
                    Send_verification_code,Delete_code_db,TokenRefreshView,Change_password_View,
                    RestetPassword_View,PasswordChecker,CheckTokenView
)
urlpatterns = [
    path('check_phone_number/',PhoneNumberCheckerView.as_view(), name='register'),
    path('registration/',User_registration.as_view(), name='register'),
    path('login/',Login_View.as_view(), name='login'),
    path('logout/',LogoutView.as_view(), name='logout'),
    path('send_code/',Send_verification_code.as_view(), name='send_code'),
    path('delete_db/',Delete_code_db.as_view(), name = 'delete_code_db'),
    path('refresh-token/', TokenRefreshView.as_view(), name='token-refresh'),
    path('check-token/', CheckTokenView.as_view(), name='check-token'),
    path('change_password/', Change_password_View.as_view(), name='change_password'),
    path('reset_password/', RestetPassword_View.as_view(), name='reset_password'),
    path('password_checker/', PasswordChecker.as_view(), name='Password_Checker'),
]