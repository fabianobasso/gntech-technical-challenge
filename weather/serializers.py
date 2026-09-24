from rest_framework import serializers
from weather.models import WeatherRecord


class WeatherRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeatherRecord
        fields = [
            'id',
            'city',
            'country',
            'temperature',
            'feels_like',
            'humidity',
            'pressure',
            'weather',
            'collected_at',
            'created_at',
        ]
        read_only_fields = fields

class WeatherFetchSerializer(serializers.Serializer):
    city = serializers.CharField(
        max_length=100,
        required=True,
        allow_blank=False,
    )

class ErrorSerializer(serializers.Serializer):
    detail = serializers.CharField()