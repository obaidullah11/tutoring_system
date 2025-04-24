from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
import uuid
from rest_framework_simplejwt.tokens import RefreshToken  # Importing RefreshToken

# Custom field for generating a unique user ID
class CustomUserIDField(models.CharField):
    def pre_save(self, model_instance, add):
        # Generate a 24-character hexadecimal ID if it's a new instance
        if add:
            return uuid.uuid4().hex[:6]  # Slicing to get the first 6 characters for a custom ID length
        else:
            return super().pre_save(model_instance, add)

class MyUserManager(BaseUserManager):
    def create_user(self, email, username=None, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')

        email = self.normalize_email(email)
        username = username or email  # Use email as username if not provided

        if self.model.objects.filter(email=email).exists():
            raise ValueError(f"The email '{email}' is already in use.")

        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username=None, password=None, **extra_fields):
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_superuser', True)

        if not username:
            username = email
        return self.create_user(email, username, password, **extra_fields)

def user_profile_pic_upload_path(instance, filename):
    # This will save files to MEDIA_ROOT/profile_pics/<user_id>/<filename>
    return f'profile_pics/{instance.id}/{filename}'
class User(AbstractUser):
    profile_pic = models.ImageField(
        upload_to=user_profile_pic_upload_path,
        blank=True,
        null=True
    )
    USER_TYPE_CHOICES = [
        ('admin', 'Admin'),
        ('student', 'Student'),
        ('teacher', 'Teacher'),
    ]

    id = CustomUserIDField(primary_key=True, max_length=6, editable=False)
    username = models.CharField(max_length=150, unique=True, blank=True, null=True)
    
    email = models.EmailField(unique=True, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='student')
    otp = models.CharField(max_length=6, blank=True, null=True)

    is_admin = models.BooleanField(default=False, null=True)
    is_email_verified = models.BooleanField(default=False, null=True)
    is_approved = models.BooleanField(default=False, null=True)
    is_deleted = models.BooleanField(default=False, null=True)
    is_mute = models.BooleanField(default=False, null=True)

    device_token = models.CharField(max_length=255, blank=True, null=True)
    profile_pic_url = models.URLField(max_length=500, blank=True, null=True)

    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin

    def get_jwt_token(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"



