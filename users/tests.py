from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import UserProfile, UserActivityLog
from portal.models import State

User = get_user_model()

class UserAuthTestCase(TestCase):
    def setUp(self):
        self.state = State.objects.create(name="Karnataka", code="KA")
        self.user = User.objects.create_user(
            username="testcitizen",
            email="citizen@gmail.com",
            password="securepass123",
            is_citizen=True
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            phone="1234567890",
            qualification="Graduate",
            state=self.state,
            occupation="Student",
            gender="Male",
            age=23,
            annual_income=180000.00
        )

    def test_user_roles(self):
        self.assertTrue(self.user.is_citizen)
        self.assertFalse(self.user.is_moderator)
        self.assertEqual(str(self.user), "citizen@gmail.com")

    def test_profile_fields(self):
        self.assertEqual(self.profile.user.username, "testcitizen")
        self.assertEqual(self.profile.state.code, "KA")
        self.assertEqual(self.profile.qualification, "Graduate")

    def test_otp_verification_flow(self):
        otp = self.profile.generate_otp()
        self.assertEqual(len(otp), 6)
        self.assertTrue(self.profile.verify_otp(otp))
        # Verify second attempt fails as it resets
        self.assertFalse(self.profile.verify_otp(otp))

    def test_activity_logging(self):
        log = UserActivityLog.objects.create(
            user=self.user,
            action="Test Login Action",
            details="Logged in citizen successfully"
        )
        self.assertEqual(log.user.email, "citizen@gmail.com")
        self.assertEqual(log.action, "Test Login Action")
