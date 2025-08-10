from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Event(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    date = models.DateField()
    time = models.TimeField(null=True, blank=True)
    location = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='events')
    image = models.ImageField(upload_to='event_images/', default='default_event.jpg')
    participants = models.ManyToManyField(User, blank=True, related_name='rsvped_events')

    class Meta:
        ordering = ['-date', 'time']

    def __str__(self):
        return f"{self.name} ({self.date})"
