from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Run(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='runs')
    file_name = models.CharField(max_length=255)
    start_time = models.DateTimeField(null=True, blank=True)
    distance_km = models.FloatField()
    duration_mins = models.FloatField()
    avg_pace = models.CharField(max_length=50)
    shoe_name = models.CharField(max_length=100, default='Unassigned')
    notes = models.TextField(blank=True, default='')
    perceived_effort = models.IntegerField(default=5)

    def __str__(self):
        return f"{self.user.username} - {self.distance_km}km on {self.file_name}"