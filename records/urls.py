from django.urls import path
from .views import ConvertTodailyRecord,AggregatedDailyRecordView,Dailyrecordviews,RecordsAPIview

urlpatterns = [
    path("convert_to_dailyrecord/",ConvertTodailyRecord.as_view(), name="convert"),
    path("w_m_record/",AggregatedDailyRecordView.as_view(), name="weeklymonthly"),
    path("trecord/",RecordsAPIview.as_view(), name="record"),
    path("dailyrecord/",Dailyrecordviews.as_view(), name="daily")
]
