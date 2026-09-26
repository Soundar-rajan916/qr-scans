from .models import ExhibitorDevice, ExhibitorDeviceSession

class DeviceLimitReached(Exception):
    pass

def register_or_update_device(exhibitor, device_id, device_name=""):
    device, created = ExhibitorDevice.objects.get_or_create(
        exhibitor=exhibitor,
        device_id=device_id,
        defaults={'device_name': device_name}
    )
    
    # Check open sessions for this exhibitor
    active_count = ExhibitorDeviceSession.objects.filter(
        device__exhibitor=exhibitor,
        logout_time__isnull=True
    ).count()

    # Check if this exact device already has an open session
    has_open_session = ExhibitorDeviceSession.objects.filter(
        device=device,
        logout_time__isnull=True
    ).exists()

    if not has_open_session:
        # Before creating a new session, ensure we haven't reached the limit
        if active_count >= exhibitor.max_devices:
            # If the device was just created but we can't open a session, rollback the device creation
            if created:
                device.delete()
            raise DeviceLimitReached("Maximum active devices reached for your plan.")
            
        # Create a new session
        ExhibitorDeviceSession.objects.create(device=device)

    return device
