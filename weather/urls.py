from django.urls import path
from weather.views import (
    WeatherFetchView,
    WeatherRecordDetailView,
    WeatherRecordListView,
)


urlpatterns = [
    path('weather/', WeatherRecordListView.as_view(), name='weather-list'),
    path(
        'weather/fetch/',
        WeatherFetchView.as_view(),
        name='weather-fetch',
    ),
    path(
        'weather/<int:pk>/',
        WeatherRecordDetailView.as_view(),
        name='weather-detail',
    ),
]