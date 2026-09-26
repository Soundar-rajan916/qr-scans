from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login, logout
from django.core.signing import Signer, BadSignature
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import Exhibitor, ExhibitorDevice, ScanLog
from .serializers import ExhibitorSerializer, ExhibitorDeviceSerializer, LoginSerializer, ExhibitorRegistrationSerializer
from .device_manager import register_or_update_device, DeviceLimitReached
from users.models import EventUser
from users.serializers import EventUserSerializer
from django.db import transaction
from django.contrib.auth.models import User

signer = Signer()

class ExhibitorRegistrationView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    
    def post(self, request):
        serializer = ExhibitorRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                user = User.objects.create_user(
                    username=serializer.validated_data['username'],
                    password=serializer.validated_data['password']
                )
                exhibitor = Exhibitor.objects.create(
                    user=user,
                    exhibitor_name=serializer.validated_data['exhibitor_name'],
                    type=serializer.validated_data['type']
                )
            return Response({
                "message": "Exhibitor registered successfully",
                "exhibitor": ExhibitorSerializer(exhibitor).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ExhibitorLoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                username=serializer.validated_data['username'],
                password=serializer.validated_data['password']
            )
            if user is not None and hasattr(user, 'exhibitor'):
                try:
                    device = register_or_update_device(
                        exhibitor=user.exhibitor,
                        device_id=serializer.validated_data['device_id'],
                        device_name=serializer.validated_data.get('device_name', '')
                    )
                except DeviceLimitReached as e:
                    return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
                
                login(request, user)
                
                # Save device_id in session for future requests
                request.session['device_id'] = device.device_id
                
                return Response({
                    "message": "Login successful",
                    "exhibitor": ExhibitorSerializer(user.exhibitor).data
                })
            else:
                return Response({"error": "Invalid credentials or not an exhibitor"}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from django.utils import timezone
from .models import Exhibitor, ExhibitorDevice, ScanLog, ExhibitorDeviceSession

class ExhibitorLogoutView(APIView):
    def post(self, request):
        print("========== LOGOUT API CALLED ==========")
        print("USER:", request.user)
        print("AUTHENTICATED:", request.user.is_authenticated)
        print("=======================================")

        if request.user.is_authenticated and hasattr(request.user, 'exhibitor'):
            device_id = request.data.get('device_id') or request.session.get('device_id')
            if device_id:
                device = ExhibitorDevice.objects.filter(exhibitor=request.user.exhibitor, device_id=device_id).first()
                if device:
                    session = ExhibitorDeviceSession.objects.filter(device=device, logout_time__isnull=True).first()
                    if session:
                        session.logout_time = timezone.now()
                        session.save(update_fields=['logout_time'])
                        
                        session.refresh_from_db()
                        print(
                            "LOGOUT SESSION:",
                            session.id,
                            session.device.device_id,
                            session.logout_time
                        )
                    
        logout(request)
        return Response({"message": "Logout successful"})

class ExhibitorMeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not hasattr(request.user, 'exhibitor'):
            return Response({"error": "Not an exhibitor"}, status=status.HTTP_403_FORBIDDEN)
        return Response(ExhibitorSerializer(request.user.exhibitor).data)

class ExhibitorDevicesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not hasattr(request.user, 'exhibitor'):
            return Response({"error": "Not an exhibitor"}, status=status.HTTP_403_FORBIDDEN)
        devices = request.user.exhibitor.devices.all()
        return Response(ExhibitorDeviceSerializer(devices, many=True).data)

class ExhibitorDeviceDeactivateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, device_id):
        if not hasattr(request.user, 'exhibitor'):
            return Response({"error": "Not an exhibitor"}, status=status.HTTP_403_FORBIDDEN)
        
        device = get_object_or_404(ExhibitorDevice, exhibitor=request.user.exhibitor, device_id=device_id)
        session = ExhibitorDeviceSession.objects.filter(device=device, logout_time__isnull=True).first()
        if session:
            session.logout_time = timezone.now()
            session.save(update_fields=['logout_time'])
        
        return Response({"message": "Device deactivated successfully"})

class QRScanView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, token):
        if not hasattr(request.user, 'exhibitor'):
            return Response({"error": "Not an exhibitor"}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            user_id_str = signer.unsign(token)
        except BadSignature:
            return Response({"error": "Invalid or expired QR code"}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            event_user = EventUser.objects.get(user_id=user_id_str)
        except EventUser.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
            
        # Log the scan
        device_id = request.session.get('device_id')
        device = None
        if device_id:
            device = ExhibitorDevice.objects.filter(exhibitor=request.user.exhibitor, device_id=device_id).first()
            
        ScanLog.objects.create(
            exhibitor=request.user.exhibitor,
            user=event_user,
            device=device
        )
        
        return Response(EventUserSerializer(event_user).data)
