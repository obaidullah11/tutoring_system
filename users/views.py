
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import *
from .models import User
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from datetime import datetime
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import logging

logger = logging.getLogger(__name__)




class LoginView(APIView):
    @swagger_auto_schema(
        operation_description="Obtain JWT tokens by logging in with email and password",
        request_body=LoginSerializer,
        responses={
            200: openapi.Response(
                description="Login successful",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'data': openapi.Schema(type=openapi.TYPE_OBJECT)
                    }
                )
            ),
            400: openapi.Response(description="Invalid credentials"),
        },
        tags=['Auth']
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'success': False, 'message': 'Login failed', 'data': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        data = serializer.validated_data
        user = data.pop('user')
        user_data = UserProfileSerializer(user).data
        payload = {
            'access': data.get('access'),
            'refresh': data.get('refresh'),
            'user': user_data
        }
        return Response(
            {'success': True, 'message': 'Login successful', 'data': payload},
            status=status.HTTP_200_OK
        )

class RegisterUserView(APIView):
    @swagger_auto_schema(
        operation_description="Register a new user with email and optional profile",
        request_body=RegisterUserSerializer,
        responses={
            201: openapi.Response(
                description="User successfully registered",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'data': openapi.Schema(type=openapi.TYPE_OBJECT),
                        'email_sent': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    }
                )
            ),
            400: openapi.Response(description="Validation errors"),
        },
        tags=['Auth']
    )
    def post(self, request):
        serializer = RegisterUserSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            logger.warning("Registration validation failed: %s", serializer.errors)
            return Response(
                {"success": False, "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = serializer.save()
        user_data = serializer.data

        # Send welcome email (optional)
        email_sent = False
        try:
            
            email_sent = True
        except Exception as e:
            logger.error("Welcome email failed for %s: %s", user.email, e)

        return Response(
            {
                "success": True,
                "message": "User registered successfully",
                "data": user_data,
                "email_sent": email_sent,
            },
            status=status.HTTP_201_CREATED
        )




class SocialLoginOrRegisterView(APIView):
    @swagger_auto_schema(
        operation_description="Register or log in a user via social sign-in.",
        request_body=SocialRegistrationSerializer,
        responses={
            200: openapi.Response(
                description="Successfully logged in or registered the user",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'data': openapi.Schema(type=openapi.TYPE_OBJECT)
                    }
                )
            ),
            400: openapi.Response(
                description="Failed to register or log in the user",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'data': openapi.Schema(type=openapi.TYPE_OBJECT)
                    }
                )
            )
        },
        tags=['Auth']
    )
    def post(self, request):
        serializer = SocialRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            # Extract email from validated data
            email = serializer.validated_data.get('email').strip().lower()
            # Attempt to fetch existing user
            try:
                user = User.objects.get(email=email)
                message = 'User logged in successfully.'
            except User.DoesNotExist:
                user = serializer.save()
                message = 'User registered successfully.'

            # Generate tokens
            tokens = user.get_jwt_token()
            user_profile = UserProfileSerializer(user).data

            return Response(
                {
                    'success': True,
                    'message': message,
                    'data': {
                        'refresh': tokens.get('refresh'),
                        'access': tokens.get('access'),
                        'user': user_profile
                    }
                },
                status=status.HTTP_200_OK
            )

        return Response(
            {
                'success': False,
                'message': 'Social auth failed.',
                'data': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from django.contrib.auth import get_user_model

User = get_user_model()

class VerifyOTPView(APIView):

    @swagger_auto_schema(
        operation_description="Verify OTP and mark the user's email as verified.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'otp': openapi.Schema(type=openapi.TYPE_STRING, description='The OTP to verify')
            }
        ),
        responses={
            200: openapi.Response(
                description="OTP verified successfully and email verified.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Indicates whether the OTP was successfully verified'),
                        'message': openapi.Schema(type=openapi.TYPE_STRING, description='Success message')
                    }
                )
            ),
            400: openapi.Response(
                description="Invalid OTP or other errors.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'detail': openapi.Schema(type=openapi.TYPE_STRING, description='Error message')
                    }
                )
            )
        },tags=['Auth']
    )
    def post(self, request):
        otp = request.data.get('otp')  # OTP passed in request body

        if not otp:
            return Response({'detail': 'OTP is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if OTP exists for any user
        user = User.objects.filter(otp=otp).first()

        if user:
            # OTP matched with a user, mark the user's email as verified
            user.is_email_verified = True
            user.save()

            return Response({
                'success': True,
                'message': 'OTP verified successfully and email verified.'
            }, status=status.HTTP_200_OK)
        
        return Response({'detail': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)

# #api to validate jwt

# class ValidateJWTView(APIView):
#     """
#     API endpoint to validate JWT token.
#     """

#     authentication_classes = [JWTAuthentication]  # Enables JWT Authentication
#     permission_classes = [IsAuthenticated]  # Requires authentication

#     @swagger_auto_schema(
#         operation_description="Validate JWT token and return authenticated user info",
#         manual_parameters=[
#             openapi.Parameter(
#                 'Authorization',
#                 openapi.IN_HEADER,
#                 description="Bearer <access_token>",
#                 type=openapi.TYPE_STRING,
#                 required=True
#             )
#         ],
#         responses={
#             200: openapi.Response(
#                 "Token is valid",
#                 openapi.Schema(
#                     type=openapi.TYPE_OBJECT,
#                     properties={
#                         'message': openapi.Schema(type=openapi.TYPE_STRING),
#                         'user': openapi.Schema(type=openapi.TYPE_OBJECT)
#                     }
#                 )
#             ),
#             401: openapi.Response("Unauthorized - Token is invalid or expired"),
#         },
#         tags=['Authentication']
#     )
#     def get(self, request):
#         """
#         Validate JWT token and return the authenticated user.
#         """
#         return Response({
#             "message": "Token is valid",
#             "user": {
#                 "id": request.user.id,
#                 "email": request.user.email,
#                 "full_name": request.user.get_full_name(),
#             }
#         }, status=status.HTTP_200_OK)
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import *

@api_view(['POST'])
def register_student(request):
    """
    Register a new user (student) with a randomly generated password.
    - `email`: User's email address.
    - `first_name`: User's first name.
    - `last_name`: User's last name.

    The password will be randomly generated and sent to the user's email.
    """
    if request.method == 'POST':
        serializer = studentRegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()  # This will automatically send an email with the credentials
            
            return Response({"message": "User registered successfully, credentials sent to email."}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
