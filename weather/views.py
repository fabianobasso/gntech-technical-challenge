import requests
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from weather.models import WeatherRecord
from weather.serializers import (
    ErrorSerializer,
    WeatherFetchSerializer,
    WeatherRecordSerializer,
)
from weather.services.weather_service import WeatherService


class WeatherRecordListView(ListAPIView):
    queryset = WeatherRecord.objects.all()
    serializer_class = WeatherRecordSerializer


class WeatherRecordDetailView(RetrieveAPIView):
    queryset = WeatherRecord.objects.all()
    serializer_class = WeatherRecordSerializer


class WeatherFetchView(APIView):
    @extend_schema(
        request=WeatherFetchSerializer,
        responses={
            201: WeatherRecordSerializer,
            400: ErrorSerializer,
            404: ErrorSerializer,
            502: ErrorSerializer,
            503: ErrorSerializer,
        },
        description=(
            'Consulta os dados meteorológicos atuais de uma cidade '
            'na OpenWeather e armazena o resultado no banco de dados.'
        ),
    )
    def post(self, request):
        serializer = WeatherFetchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        city = serializer.validated_data['city']

        try:
            record = WeatherService().save_current_weather(city)
        except requests.HTTPError as exception:
            response = exception.response

            if response is not None and response.status_code == 404:
                return Response(
                    {'detail': 'Cidade não encontrada.'},
                    status=status.HTTP_404_NOT_FOUND,
                )

            return Response(
                {'detail': 'Erro ao consultar o serviço de clima.'},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        except requests.RequestException:
            return Response(
                {'detail': 'Serviço de clima indisponível.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return Response(
            WeatherRecordSerializer(record).data,
            status=status.HTTP_201_CREATED,
        )