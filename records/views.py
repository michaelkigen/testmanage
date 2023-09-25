from django.shortcuts import render
from rest_framework import views,status
from rest_framework.response import Response
from .models import Records,DailyRecord
from .serializers import RecordSerializer , DailyRecordSerializer
from Profile.models import Profile
from users.models import User
from datetime import datetime, timedelta

# ...
# Create your views here.

def convert_to_points(unavilable_food,user):
    phone_number = user["phone_number"]
    print("User ",phone_number)
    try:
        user = User.objects.get(phone_number=phone_number)
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        return Response({'error': 'profile not found.'}, status=status.HTTP_404_NOT_FOUND)
    pnts = int(unavilable_food) * 5
    print("Pointd ",pnts)
    profile.points +=pnts
    profile.save()


def recorder(food, user):
        for item in food:
            if item['food']['is_avilable'] == True:
                
                
                food_name = item['food']['food_name']
                quantity = item['quantity']
                sub_total = item['sub_total']
                try:
                    record = Records.objects.get(food = food_name)
                    
                except Records.DoesNotExist:
                    return Response({'detail': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)
                record.tquantity += quantity
                record.tamount += sub_total
                
                record.save()
            if item['food']['is_avilable'] == False:
                unavilable_food = item['sub_total']
                convert_to_points(unavilable_food,user)
        


class RecordsAPIview(views.APIView):
    def get(self,request):
        serializer = RecordSerializer
        return Response(serializer.data, status=status.HTTP_200_OK)
            
class ConvertTodailyRecord(views.APIView):
    def post(self,request):
        records = Records.objects.all()

        # Create DailyRecord objects from the Records data
        daily_records = []
        for record in records:
            daily_record = DailyRecord(
                food=record.food,
                quantity=record.tquantity,
                amount=record.tamount
            )
            daily_records.append(daily_record)

        # Bulk insert the DailyRecord objects into the DailyRecord table 
        DailyRecord.objects.bulk_create(daily_records)

        # Optionally, you can delete the original records from the Records table
        # records.delete()

        return Response({'success': 'Data conversion completed.'}, status=status.HTTP_200_OK)
    
    
class Dailyrecordviews(views.APIView):
    def get(self,request):
        serializer = DailyRecordSerializer
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    

class AggregatedDailyRecordView(views.APIView):
    def get(self, request):
        # Calculate the date range for the past week and month
        today = datetime.now().date()
        one_week_ago = today - timedelta(days=7)
        one_month_ago = today - timedelta(days=30)

        # Filter daily records for the past week and month
        weekly_records = DailyRecord.objects.filter(date__gte=one_week_ago, date__lte=today)
        monthly_records = DailyRecord.objects.filter(date__gte=one_month_ago, date__lte=today)

        # Serialize the data
        weekly_serializer = DailyRecordSerializer(weekly_records, many=True)
        monthly_serializer = DailyRecordSerializer(monthly_records, many=True)

        # Calculate weekly and monthly totals
        weekly_total_quantity = sum(record.quantity for record in weekly_records)
        weekly_total_amount = sum(record.amount for record in weekly_records)
        monthly_total_quantity = sum(record.quantity for record in monthly_records)
        monthly_total_amount = sum(record.amount for record in monthly_records)

        response_data = {
            'weekly_records': weekly_serializer.data,
            'monthly_records': monthly_serializer.data,
            'weekly_total_quantity': weekly_total_quantity,
            'weekly_total_amount': weekly_total_amount,
            'monthly_total_quantity': monthly_total_quantity,
            'monthly_total_amount': monthly_total_amount,
        }

        return Response(response_data, status=status.HTTP_200_OK)
