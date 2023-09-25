from django.urls import  path
from .views import SendMessageView , GetMessagesView
 
 
urlpatterns = [
    path('sendmasg/',SendMessageView.as_view(), name='send'),
    path('viewmsg/',GetMessagesView.as_view(), name='view')
    
    ]