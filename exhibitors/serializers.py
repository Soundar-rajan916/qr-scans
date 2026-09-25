from rest_framework import serializers
from .models import Exhibitor, ExhibitorDevice, ScanLog
from django.contrib.auth.models import User

class ExhibitorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exhibitor
        fields = ['exhibitor_id', 'exhibitor_name', 'type', 'max_devices']

class ExhibitorDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExhibitorDevice
        fields = ['device_id', 'device_name', 'is_active', 'last_login', 'created_at']

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    device_id = serializers.CharField()
    device_name = serializers.CharField(required=False, allow_blank=True)

class ExhibitorRegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)
    exhibitor_name = serializers.CharField(max_length=255)
    type = serializers.ChoiceField(choices=Exhibitor.TYPE_CHOICES, default='silver')

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists")
        return value
