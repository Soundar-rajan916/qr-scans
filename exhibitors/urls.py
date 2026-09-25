from django.urls import path
from .views import (
    ExhibitorRegistrationView,
    ExhibitorLoginView, 
    ExhibitorLogoutView, 
    ExhibitorMeView,
    ExhibitorDevicesView,
    ExhibitorDeviceDeactivateView,
    QRScanView
)

urlpatterns = [
    path('register/', ExhibitorRegistrationView.as_view(), name='exhibitor-register'),
    path('login/', ExhibitorLoginView.as_view(), name='exhibitor-login'),
    path('logout/', ExhibitorLogoutView.as_view(), name='exhibitor-logout'),
    path('me/', ExhibitorMeView.as_view(), name='exhibitor-me'),
    path('devices/', ExhibitorDevicesView.as_view(), name='exhibitor-devices'),
    path('devices/<str:device_id>/deactivate/', ExhibitorDeviceDeactivateView.as_view(), name='exhibitor-device-deactivate'),
    path('scan/<str:token>/', QRScanView.as_view(), name='exhibitor-scan'),
]
