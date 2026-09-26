from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import Exhibitor, ExhibitorDevice, ScanLog, ExhibitorDeviceSession

class ScanLogInline(admin.TabularInline):
    model = ScanLog
    readonly_fields = ('user', 'device', 'scanned_at')
    can_delete = False
    extra = 0
    fields = ('user', 'device', 'scanned_at')
    
    def has_add_permission(self, request, obj=None):
        return False

@admin.register(Exhibitor)
class ExhibitorAdmin(admin.ModelAdmin):
    list_display = ('exhibitor_name', 'type', 'total_scans', 'logged_in_devices', 'view_scan_logs_link')
    search_fields = ('exhibitor_name', 'user__username')
    list_filter = ('type',)
    inlines = [ScanLogInline]

    def total_scans(self, obj):
        return ScanLog.objects.filter(exhibitor=obj).count()
    total_scans.short_description = 'Total Scans'

    def logged_in_devices(self, obj):
        return ExhibitorDeviceSession.objects.filter(
            device__exhibitor=obj,
            logout_time__isnull=True
        ).count()
    logged_in_devices.short_description = 'Currently Logged-in Devices'

    def view_scan_logs_link(self, obj):
        url = reverse('admin:exhibitors_scanlog_changelist') + f'?exhibitor__id__exact={obj.id}'
        return format_html('<a href="{}">View Scan Logs</a>', url)
    view_scan_logs_link.short_description = 'Action'

@admin.register(ExhibitorDevice)
class ExhibitorDeviceAdmin(admin.ModelAdmin):
    list_display = ('device_name', 'device_id', 'exhibitor', 'created_at')
    list_filter = ('exhibitor',)
    search_fields = ('device_name', 'device_id')

@admin.register(ExhibitorDeviceSession)
class ExhibitorDeviceSessionAdmin(admin.ModelAdmin):
    list_display = ('device', 'exhibitor_name', 'login_time', 'logout_time', 'status')
    list_filter = ('device__exhibitor', 'login_time')

    def exhibitor_name(self, obj):
        return obj.device.exhibitor.exhibitor_name
    
    def status(self, obj):
        return 'Active' if obj.logout_time is None else 'Logged Out'
    
@admin.register(ScanLog)
class ScanLogAdmin(admin.ModelAdmin):
    list_display = ('exhibitor', 'user', 'device', 'scanned_at')
    list_filter = ('exhibitor', 'scanned_at')
    search_fields = ('user__name', 'user__email', 'device__device_name', 'device__device_id')
