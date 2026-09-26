from rest_framework import serializers
from .models import Exhibitor, ExhibitorDevice, ScanLog
from django.contrib.auth.models import User

class ExhibitorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exhibitor
        fields = ['exhibitor_id', 'exhibitor_name', 'type', 'max_devices']

class ExhibitorDeviceSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()

    class Meta:
        model = ExhibitorDevice
        fields = ['device_id', 'device_name', 'created_at', 'status']

    def get_status(self, obj):
        has_open_session = obj.sessions.filter(logout_time__isnull=True).exists()
        return 'Active' if has_open_session else 'Logged Out'

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
