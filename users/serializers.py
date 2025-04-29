# from rest_framework import serializers
from django.contrib.auth import authenticate
# from users.models import User,DocumentVerification
# from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError
# from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
# from django.contrib.auth.tokens import PasswordResetTokenGenerator
# from users.utils import Util
# from rest_framework_simplejwt.tokens import RefreshToken
# from rest_framework import serializers
# from rest_framework import serializers
# from .models import User, DocumentVerification
# from .models import User
# from rest_framework_simplejwt.tokens import RefreshToken
# from rest_framework import serializers
# from rest_framework import serializers
# from .models import User
# from rest_framework_simplejwt.tokens import RefreshToken




from rest_framework import serializers
from users.models import User

class UserProfileSerializernew(serializers.ModelSerializer):
    # Return both refresh and access JWT tokens
    # tokens = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            # Primary key
            'id',

            # Identity
            'email',
            'username',
            'first_name',
            'last_name',

            # Contact
            'phone_number',

            # Avatar
            'profile_pic',
            'profile_pic_url',

            # Roles & flags
            'user_type',
            'is_admin',
            'is_email_verified',
            'is_approved',
            'is_deleted',
            'is_mute',

            # Device
            'device_token',

            # Tokens

        ]

# class UserProfileSerializerv2(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = (
#             'id', 'username', 'first_name', 'last_name', 'phone_number',  'email','device_type', 'device_token',  'city', 'state',
#             'address', 'bio',  'profile_pic_url', 'email_id','created_at', 'updated_at','is_identity_verified','language',
#         )

#     def update(self, instance, validated_data):
#         for attr, value in validated_data.items():
#             setattr(instance, attr, value)
#         instance.save()
#         return instance



from rest_framework import serializers
from users.models import User

class UserProfileSerializer(serializers.ModelSerializer):
    # Return both refresh and access JWT tokens
    tokens = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            # Primary key
            'id',

            # Identity
            'email',
            'username',
            'first_name',
            'last_name',

            # Contact
            'phone_number',

            # Avatar
            'profile_pic',
            'profile_pic_url',

            # Roles & flags
            'user_type',
            'is_admin',
            'is_email_verified',
            'is_approved',
            'is_deleted',
            'is_mute',

            # Device
            'device_token',

            # Tokens
            'tokens',
        ]
        read_only_fields = ('id', 'tokens')

    def get_tokens(self, obj):
        """
        Delegates to your model’s `get_jwt_token()`,
        which returns {'refresh': ..., 'access': ...}.
        """
        return obj.get_jwt_token()

    def update(self, instance, validated_data):
        """
        Apply any writable fields and save.
        """
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

# class DocumentVerificationSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = DocumentVerification
#         fields = ('id', 'user', 'document_file', 'verification_status', 'verification_date')




# class EmailExistenceCheckSerializer(serializers.Serializer):
#     email = serializers.EmailField()

# # Serializer for the response
# class EmailExistenceCheckResponseSerializer(serializers.Serializer):
#     success = serializers.BooleanField()
#     message = serializers.CharField()
#     data = serializers.DictField()
# class EmailSerializer(serializers.Serializer):
#     subject = serializers.CharField(max_length=255)
#     body = serializers.CharField()
#     to_email = serializers.EmailField()


# class SendOTPSerializer(serializers.Serializer):
#     phone_number = serializers.CharField(max_length=15)
# class phoneloginSerializer(serializers.Serializer):
#     phone_number = serializers.CharField(max_length=15)

#     def validate_phone_number(self, value):
#         if not User.objects.filter(phone_number=value).exists():
#             raise serializers.ValidationError("User with this phone number does not exist.")
#         return value
# class VerifyOTPSerializer(serializers.Serializer):
#     phone_number = serializers.CharField(max_length=15)
#     otp = serializers.CharField(max_length=6)




# class ResetPasswordSerializer(serializers.Serializer):
#     phone_number = serializers.CharField(max_length=15)
#     new_password = serializers.CharField(min_length=6)



#import logging
from django.db import transaction
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
import logging
User = get_user_model()
logger = logging.getLogger(__name__)
import random
from django.core.mail import send_mail
from django.conf import settings

class RegisterUserSerializer(serializers.ModelSerializer):
    profile_pic = serializers.ImageField(required=False, allow_null=True)
    profile_pic_url = serializers.URLField(required=False, allow_null=True)
    user_type = serializers.ChoiceField(choices=User.USER_TYPE_CHOICES, default='student')
    password = serializers.CharField(write_only=True, required=True, min_length=8)
    tokens = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'password', 'first_name', 'last_name',
            'phone_number', 'profile_pic', 'profile_pic_url', 'user_type',
            'device_token', 'is_email_verified', 'is_approved', 'is_deleted',
            'is_mute', 'tokens', 'otp',
        ]
        extra_kwargs = {
            'email': {'required': True},
            'id': {'read_only': True},
            'username': {'required': False},
            'password': {'write_only': True, 'required': True},
            'otp': {'read_only': True},
        }

    def validate_email(self, value):
        email = value.strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError("This email is already taken.")
        return email

    def validate_phone_number(self, value):
        phone = value.strip()
        if User.objects.filter(phone_number=phone).exists():
            raise serializers.ValidationError("This phone number is already taken.")
        return phone

    def validate(self, attrs):
        first = attrs.get('first_name', '').strip()
        last = attrs.get('last_name', '').strip()
        if not attrs.get('username'):
            attrs['username'] = f"{first} {last}" if first and last else attrs.get('email')
        return attrs

    def generate_otp(self):
        """Generate a 4-digit random OTP"""
        return str(random.randint(1000, 9999))

    def send_otp_email(self, user):
        subject = "Your OTP Code"
        message = f"Hello {user.first_name},\n\nYour OTP code is: {user.otp}\n\nThanks!"
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

    @transaction.atomic
    def create(self, validated_data):
        logger.debug("Creating user with data: %s", {k: v for k, v in validated_data.items() if k != 'password'})
        password = validated_data.pop('password')

        otp = self.generate_otp()
        validated_data['otp'] = otp

        user = User.objects.create_user(
            email=validated_data.get('email'),
            username=validated_data.get('username'),
            password=password,
            **{k: v for k, v in validated_data.items() if k not in ('email', 'username')}
        )

        self.send_otp_email(user)

        logger.info("User created and OTP sent to: %s", user.email)
        return user

    def get_tokens(self, obj):
        return obj.get_jwt_token()




from rest_framework import serializers
from .models import User
import secrets
import string

class studentRegistrationSerializer(serializers.ModelSerializer):
    # The password will not be exposed in the serializer, as it is generated automatically
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name','password']

    def generate_random_password(self, length=8):
        """Generate a random password of specified length (default: 8)."""
        alphabet = string.ascii_letters + string.digits  # Letters and digits
        password = ''.join(secrets.choice(alphabet) for i in range(length))
        return password

    def create(self, validated_data):
        # Generate a random password
        password = self.generate_random_password()

        # Create the user with the random password
        user = User.objects.create_user(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=password,
            is_email_verified=True,
            user_type='student'  # Assign the default user_type as 'student'
        )

        # Send the email with user credentials
        subject = "Welcome to the platform!"
        message = f"Hello {user.first_name},\n\nYour account has been created successfully.\n\nYour credentials:\nEmail: {user.email}\nPassword: {password}\n\nBest regards,\nATS"
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [user.email]

        send_mail(subject, message, from_email, recipient_list)

        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)

    def validate(self, attrs):
        email = attrs.get('email').strip().lower()
        password = attrs.get('password')
        user = authenticate(username=email, password=password)
        if not user:
            raise serializers.ValidationError({"detail": "Invalid credentials."})
        if not user.is_active:
            raise serializers.ValidationError({"detail": "User account is disabled."})
        tokens = user.get_jwt_token()
        attrs['access'] = tokens.get('access')
        attrs['refresh'] = tokens.get('refresh')
        attrs['user'] = user
        return attrs
import string
import random
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class SocialRegistrationSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=50, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=50, required=False, allow_blank=True)
    email = serializers.EmailField(max_length=254, required=True)
    profile_pic_url = serializers.URLField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'profile_pic_url']

    def generate_random_password(self, length=12):
        characters = string.ascii_letters + string.digits + string.punctuation
        return ''.join(random.choices(characters, k=length))

    def create(self, validated_data):
        email = validated_data.get('email')
        first_name = validated_data.get('first_name', '').strip()
        last_name = validated_data.get('last_name', '').strip()
        profile_pic_url = validated_data.get('profile_pic_url', '')

        base_username = f"{first_name}{last_name}".lower() if first_name or last_name else email.split('@')[0]
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        random_password = self.generate_random_password()

        user, created = User.objects.get_or_create(email=email, defaults={
            'first_name': first_name,
            'last_name': last_name,
            'profile_pic_url': profile_pic_url,
            'username': username,
            'password': make_password(random_password)
        })

        if not created:
            user.first_name = first_name
            user.last_name = last_name
            user.profile_pic_url = profile_pic_url
            if not user.username:
                user.username = email
            user.save()

        return user



# class FileUploadSerializern(serializers.Serializer):
#     file = serializers.FileField()  # This will handle the file upload







# class profileUserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = '__all__'


# class profileUserSerializernew(serializers.ModelSerializer):
#     image = serializers.ImageField(required=False)  # Remove this line if it exists

#     class Meta:
#         model = User
#         fields = '__all__'





# import random
# import string
# from rest_framework import serializers
# from django.contrib.auth.hashers import make_password
# from .models import User  # Import your custom User model

# class SocialRegistrationSerializer(serializers.ModelSerializer):
#     first_name = serializers.CharField(max_length=50, required=False, allow_blank=True)
#     last_name = serializers.CharField(max_length=50, required=False, allow_blank=True)
#     email = serializers.EmailField(max_length=254, required=True)
#     profile_pic_url = serializers.URLField(required=False, allow_blank=True)

#     class Meta:
#         model = User  # Your custom User model
#         fields = ['first_name', 'last_name', 'email', 'profile_pic_url']

#     def generate_random_password(self, length=12):
#         """Generate a random password with uppercase, lowercase, digits, and special characters."""
#         characters = string.ascii_letters + string.digits + string.punctuation
#         return ''.join(random.choices(characters, k=length))

#     def create(self, validated_data):
#         """
#         Create a new user or update the existing user based on email.
#         If no username is provided, concatenate first_name and last_name to form the username.
#         """
#         email = validated_data.get('email')
#         first_name = validated_data.get('first_name', '').strip()
#         last_name = validated_data.get('last_name', '').strip()
#         profile_pic_url = validated_data.get('profile_pic_url', '')

#         # Generate a base username by concatenating first_name and last_name
#         base_username = f"{first_name}{last_name}".lower() if first_name or last_name else email.split('@')[0]

#         # Ensure the username is unique
#         username = base_username
#         counter = 1
#         while User.objects.filter(username=username).exists():
#             username = f"{base_username}{counter}"
#             counter += 1

#         # Generate a random password
#         random_password = self.generate_random_password()

#         # Create or update the user
#         user, created = User.objects.get_or_create(email=email, defaults={
#             'first_name': first_name,
#             'last_name': last_name,
#             'profile_pic_url': profile_pic_url,
#             'username': username,
#             'password': make_password(random_password)  # Hash the generated password
#         })

#         # If user already exists, update the fields
#         if not created:
#             user.first_name = first_name
#             user.last_name = last_name
#             user.profile_pic_url = profile_pic_url

#             # Ensure the username is set to the email if it’s not set
#             if not user.username:
#                 user.username = email

#             user.save()

#         # You can send the generated password via email or return it in the response if needed
#         return user





# class VerifyOTPResetPasswordSerializer(serializers.Serializer):
#     email = serializers.EmailField()
#     otp = serializers.CharField(max_length=6)
#     new_password = serializers.CharField(write_only=True, min_length=6)
























