
from rest_framework import viewsets,status
from rest_framework.response import Response
from .models import Review,NotifY,OveralReview
from .serializers import ReviewSerializer,NotificationSerializer,OveralratingSerializer


class OveralReviewViewSet(viewsets.ModelViewSet):
    queryset = OveralReview.objects.all()
    serializer_class = OveralratingSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def perform_create(self, serializer):
        product = serializer.validated_data['product']
        user = self.request.user

        # Create the review
        review = serializer.save(user=user)

        # Update the overall rating for the product
        self.update_overall_rating(product)

    def perform_update(self, serializer):
        # Retrieve the review to be updated
        review = self.get_object()

        # Update the review
        serializer.save()

        # Update the overall rating for the product
        self.update_overall_rating(review.product)
    def destroy(self, request, *args, **kwargs):
        # Retrieve the review to be deleted
        review = self.get_object()

        # Ensure the user attempting to delete the review is the owner of the review
        if review.user != self.request.user:
            return Response({'detail': 'You do not have permission to delete this review.'}, status=status.HTTP_403_FORBIDDEN)

        # Get the product associated with the review before deleting it
        product = review.product

        # Delete the review
        review.delete()

        # Update the overall rating for the product after the review is deleted
        self.update_overall_rating(product)

        return Response({'detail': 'Review deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)

    def update_overall_rating(self, product):
        ratings = Review.objects.filter(product=product).values_list('rating', flat=True)
        overal_rate, created = OveralReview.objects.get_or_create(product=product)

        if ratings:
            mean_rating = sum(ratings) / len(ratings)
            mean_rating = round(mean_rating, 2)
        else:
            mean_rating = 0

        overal_rate.overal_rating = mean_rating
        overal_rate.save()

        
    
class NotificationViewSet(viewsets.ModelViewSet):
    queryset = NotifY.objects.all()
    serializer_class = NotificationSerializer