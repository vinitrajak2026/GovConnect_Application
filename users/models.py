from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import random

class User(AbstractUser):
    """
    Custom user model for GovConnect supporting Citizens, Moderators, and Admins.
    """
    is_citizen = models.BooleanField(default=True)
    is_moderator = models.BooleanField(default=False)
    is_admin_user = models.BooleanField(default=False)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

class UserProfile(models.Model):
    """
    Citizens profile with state, qualifications, and demographic info for recommendation engine.
    """
    QUALIFICATION_CHOICES = [
        ('10th', '10th Pass'),
        ('12th', '12th Pass'),
        ('Graduate', 'Graduate'),
        ('PostGraduate', 'Post-Graduate'),
        ('Doctorate', 'Doctorate'),
    ]

    OCCUPATION_CHOICES = [
        ('Student', 'Student'),
        ('Farmer', 'Farmer'),
        ('Unemployed', 'Unemployed'),
        ('SelfEmployed', 'Self-Employed'),
        ('PrivateJob', 'Private Job'),
        ('SeniorCitizen', 'Senior Citizen'),
        ('Business', 'Business'),
    ]

    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_expiry = models.DateTimeField(blank=True, null=True)
    
    # Demographics for recommendations
    qualification = models.CharField(max_length=20, choices=QUALIFICATION_CHOICES, default='Graduate')
    state = models.ForeignKey('portal.State', on_delete=models.SET_NULL, null=True, blank=True, related_name='profiles')
    occupation = models.CharField(max_length=20, choices=OCCUPATION_CHOICES, default='Student')
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='Male')
    age = models.IntegerField(default=22)
    annual_income = models.DecimalField(max_digits=12, decimal_places=2, default=150000.00)

    # Preferences
    notification_email = models.BooleanField(default=True)
    notification_browser = models.BooleanField(default=True)
    notification_sms = models.BooleanField(default=False)

    def generate_otp(self):
        self.otp = f"{random.randint(100000, 999999)}"
        self.otp_expiry = timezone.now() + timezone.timedelta(minutes=10)
        self.save()
        return self.otp

    def verify_otp(self, entered_otp):
        if self.otp and self.otp == entered_otp and self.otp_expiry > timezone.now():
            self.otp = None
            self.otp_expiry = None
            self.save()
            return True
        return False

    def __str__(self):
        return f"{self.user.email}'s Profile"

class UserActivityLog(models.Model):
    """
    Log of citizen and moderator actions for security, auditing, and analytics.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_logs')
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    details = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.email} - {self.action} @ {self.timestamp}"
