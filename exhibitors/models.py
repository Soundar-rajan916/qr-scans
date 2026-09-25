import uuid
from django.db import models
from django.contrib.auth.models import User
from users.models import EventUser

class Exhibitor(models.Model):
    TYPE_CHOICES = [
        ('silver', 'Silver'),
        ('gold', 'Gold'),
        ('platinum', 'Platinum'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    exhibitor_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    exhibitor_name = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='silver')

    @property
    def max_devices(self):
        limits = {'silver': 1, 'gold': 2, 'platinum': 3}
        return limits.get(self.type, 1)

    def __str__(self):
        return f"{self.exhibitor_name} ({self.get_type_display()})"

class ExhibitorDevice(models.Model):
    exhibitor = models.ForeignKey(Exhibitor, related_name='devices', on_delete=models.CASCADE)
    device_id = models.CharField(max_length=255) # Client provided unique identifier
    device_name = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('exhibitor', 'device_id')

    def __str__(self):
        return f"{self.device_name or self.device_id} ({self.exhibitor.exhibitor_name})"

class ScanLog(models.Model):
    exhibitor = models.ForeignKey(Exhibitor, on_delete=models.CASCADE)
    user = models.ForeignKey(EventUser, on_delete=models.CASCADE)
    device = models.ForeignKey(ExhibitorDevice, on_delete=models.SET_NULL, null=True)
    scanned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.exhibitor.exhibitor_name} scanned {self.user.name} at {self.scanned_at}"
