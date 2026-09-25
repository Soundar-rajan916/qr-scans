from .models import ExhibitorDevice

class DeviceLimitReached(Exception):
    pass

def register_or_update_device(exhibitor, device_id, device_name=""):
    device, created = ExhibitorDevice.objects.get_or_create(
        exhibitor=exhibitor,
        device_id=device_id,
        defaults={'device_name': device_name, 'is_active': True}
    )
    
    if not created and not device.is_active:
        # Trying to reactivate a device
        active_count = ExhibitorDevice.objects.filter(exhibitor=exhibitor, is_active=True).count()
        if active_count >= exhibitor.max_devices:
            raise DeviceLimitReached("Maximum active devices reached for your plan.")
        device.is_active = True
        device.save()
    elif created:
        # New device created, check limit. Since it was just created with is_active=True, 
        # count includes this device.
        active_count = ExhibitorDevice.objects.filter(exhibitor=exhibitor, is_active=True).count()
        if active_count > exhibitor.max_devices:
            device.delete() # rollback
            raise DeviceLimitReached("Maximum active devices reached for your plan.")
            
    # Update last login
    device.save() # Triggers auto_now=True
    return device
