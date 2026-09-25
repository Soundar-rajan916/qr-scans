from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from users.models import EventUser
from .models import Exhibitor, ExhibitorDevice, ScanLog
from django.core.signing import Signer

class ExhibitorTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="exhib1", password="password123")
        self.exhibitor = Exhibitor.objects.create(user=self.user, exhibitor_name="Company X", type="silver") # 1 device limit
        self.event_user = EventUser.objects.create(name="Jane", email="jane@test.com", score=10)
        self.signer = Signer()

    def test_login_and_device_limit(self):
        # First device login
        res1 = self.client.post(reverse('exhibitor-login'), {
            "username": "exhib1",
            "password": "password123",
            "device_id": "device_1"
        }, content_type="application/json")
        self.assertEqual(res1.status_code, 200)

        # Second device login should fail because of limit (silver=1)
        res2 = self.client.post(reverse('exhibitor-login'), {
            "username": "exhib1",
            "password": "password123",
            "device_id": "device_2"
        }, content_type="application/json")
        self.assertEqual(res2.status_code, 403)

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
