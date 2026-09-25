from django.contrib import admin
from .models import Exhibitor, ExhibitorDevice, ScanLog

@admin.register(Exhibitor)
class ExhibitorAdmin(admin.ModelAdmin):
    list_display = ('exhibitor_name', 'user', 'type', 'max_devices')
    search_fields = ('exhibitor_name', 'user__username')
    list_filter = ('type',)

@admin.register(ExhibitorDevice)
class ExhibitorDeviceAdmin(admin.ModelAdmin):
    list_display = ('device_name', 'device_id', 'exhibitor', 'is_active', 'last_login')
    list_filter = ('is_active', 'exhibitor')
    search_fields = ('device_name', 'device_id')
    
@admin.register(ScanLog)
class ScanLogAdmin(admin.ModelAdmin):
    list_display = ('exhibitor', 'user', 'device', 'scanned_at')
    list_filter = ('exhibitor', 'scanned_at')
    search_fields = ('user__name', 'user__email', 'exhibitor__exhibitor_name')
