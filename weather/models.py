from django.db import models

# Create your models here.
class WeatherRecord(models.Model):
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=2)
    temperature = models.DecimalField(max_digits=5, decimal_places=2)
    feels_like = models.DecimalField(max_digits=5, decimal_places=2)
    humidity = models.PositiveSmallIntegerField()
    pressure = models.PositiveIntegerField()
    weather = models.CharField(max_length=100)
    collected_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-collected_at']

    def __str__(self):
        return f'{self.city}, {self.country} - {self.temperature}°C'