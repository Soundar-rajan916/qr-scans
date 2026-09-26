from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from users.models import EventUser
from .models import Exhibitor, ExhibitorDevice, ScanLog, ExhibitorDeviceSession
from django.core.signing import Signer
from django.utils import timezone

class ExhibitorTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="exhib1", password="password123")
        self.exhibitor = Exhibitor.objects.create(user=self.user, exhibitor_name="Company X", type="silver") # 1 device limit
        self.user2 = User.objects.create_user(username="exhib2", password="password123")
        self.gold_exhibitor = Exhibitor.objects.create(user=self.user2, exhibitor_name="Company Gold", type="gold") # 2 device limit
        self.event_user = EventUser.objects.create(name="Jane", email="jane@test.com", score=10)
        self.signer = Signer()

    def test_login_and_logout_flow(self):
        # 1. Login sets creates an open session
        res1 = self.client.post(reverse('exhibitor-login'), {
            "username": "exhib1",
            "password": "password123",
            "device_id": "device_1"
        }, content_type="application/json")
        self.assertEqual(res1.status_code, 200)
        
        device1 = ExhibitorDevice.objects.get(device_id="device_1")
        session1 = ExhibitorDeviceSession.objects.filter(device=device1, logout_time__isnull=True).first()
        self.assertIsNotNone(session1)
        self.assertIsNone(session1.logout_time)
        initial_login = session1.login_time

        # 3. Logout sets logout_time
        res2 = self.client.post(reverse('exhibitor-logout'), {
            "device_id": "device_1"
        }, content_type="application/json")
        self.assertEqual(res2.status_code, 200)

        session1.refresh_from_db()
        self.assertIsNotNone(session1.logout_time)
        self.assertEqual(session1.login_time, initial_login) # Last login should be unchanged

        # 6. Login again creates a NEW session for the same device
        res3 = self.client.post(reverse('exhibitor-login'), {
            "username": "exhib1",
            "password": "password123",
            "device_id": "device_1"
        }, content_type="application/json")
        self.assertEqual(res3.status_code, 200)

        # 8. Same device does not create duplicate records
        self.assertEqual(ExhibitorDevice.objects.filter(device_id="device_1").count(), 1)
        self.assertEqual(ExhibitorDeviceSession.objects.filter(device=device1).count(), 2)
        
        new_session = ExhibitorDeviceSession.objects.filter(device=device1, logout_time__isnull=True).first()
        self.assertIsNotNone(new_session)
        self.assertNotEqual(new_session.id, session1.id) 

    def test_multi_device_logout_isolation(self):
        # 10. Gold plan allows 2 devices
        self.client.post(reverse('exhibitor-login'), {
            "username": "exhib2",
            "password": "password123",
            "device_id": "dev_A"
        }, content_type="application/json")
        
        self.client.post(reverse('exhibitor-login'), {
            "username": "exhib2",
            "password": "password123",
            "device_id": "dev_B"
        }, content_type="application/json")

        self.assertEqual(ExhibitorDevice.objects.count(), 2)
        dev_a = ExhibitorDevice.objects.get(device_id="dev_A")
        dev_b = ExhibitorDevice.objects.get(device_id="dev_B")
        
        self.assertEqual(ExhibitorDeviceSession.objects.filter(device=dev_a, logout_time__isnull=True).count(), 1)
        self.assertEqual(ExhibitorDeviceSession.objects.filter(device=dev_b, logout_time__isnull=True).count(), 1)

        # Logout dev_A
        self.client.post(reverse('exhibitor-logout'), {
            "device_id": "dev_A"
        }, content_type="application/json")

        # 4. Logout affects only current device
        self.assertEqual(ExhibitorDeviceSession.objects.filter(device=dev_a, logout_time__isnull=True).count(), 0)
        # 5. Other devices remain active
        self.assertEqual(ExhibitorDeviceSession.objects.filter(device=dev_b, logout_time__isnull=True).count(), 1)
        
        # 9. Inactive devices don't count toward limit (Limit is 2, dev_B is active, we can add dev_C)
        res = self.client.post(reverse('exhibitor-login'), {
            "username": "exhib2",
            "password": "password123",
            "device_id": "dev_C"
        }, content_type="application/json")
        self.assertEqual(res.status_code, 200)

    def test_device_limit_enforced(self):
        # Silver allows 1 device
        self.client.post(reverse('exhibitor-login'), {
            "username": "exhib1",
            "password": "password123",
            "device_id": "dev_1"
        }, content_type="application/json")
        
        res = self.client.post(reverse('exhibitor-login'), {
            "username": "exhib1",
            "password": "password123",
            "device_id": "dev_2"
        }, content_type="application/json")
        self.assertEqual(res.status_code, 403)

    def test_qr_scan(self):
        # Login
        self.client.post(reverse('exhibitor-login'), {
            "username": "exhib1",
            "password": "password123",
            "device_id": "device_1"
        }, content_type="application/json")
        
        token = self.signer.sign(str(self.event_user.user_id))
        res = self.client.get(reverse('exhibitor-scan', args=[token]))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['name'], "Jane")
        
        # Check scan log
        self.assertEqual(ScanLog.objects.count(), 1)
