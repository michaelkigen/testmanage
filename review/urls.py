from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReviewViewSet,NotificationViewSet,OveralReviewViewSet

router = DefaultRouter()
router.register('review', ReviewViewSet)
router.register('notification', NotificationViewSet)
router.register('overalreview', OveralReviewViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('reviews/<int:pk>/', ReviewViewSet.as_view({'put': 'update'}))
]
