import json
import logging
import time
from datetime import datetime, timedelta

import jwt
import requests
from decouple import config
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, login
from django.core.mail import send_mail
from django.http import HttpResponse
from rest_framework.exceptions import ValidationError
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from users.constants import URL_GOOGLE_ME, URL_GOOGLE_TOKEN, PROVIDER_GOOGLE_OAUTH2
from users.models import UserSocialAuth

from prisvio.permissions import IsAdminUserOrReadOnly, IsBusinessAdminOrAdmin

from .serializers import (ChangePasswordSerializer, ForgotPasswordSerializer,
                          UserCloneSerializer, UserSerializer)

logger = logging.getLogger('django')

User = get_user_model()

@api_view(['POST'])
def signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({'id': user.id, 'user': serializer.data, 'refresh': str(refresh), 'access': str(refresh.access_token)}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def signin(request):
    username = request.data.get('username', None)
    email = request.data.get('email', None)
    phone_number = request.data.get('phone_number', None)
    password = request.data.get('password', None)

    if not (username or email or phone_number) or not password:
        return Response({'error': 'Please provide either username, email or phone number and password'},
                        status=status.HTTP_400_BAD_REQUEST)

    user = None
    if email:
        user = User.objects.filter(email=email).first()
    elif phone_number:
        user = User.objects.filter(phone_number=phone_number).first()
    elif username:
        user = User.objects.filter(username=username).first()

    if user is not None:
        if user.check_password(password):
            refresh = RefreshToken.for_user(user)
            return Response({
                'id': user.id,
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token)
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid password'}, status=status.HTTP_401_UNAUTHORIZED)

    return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

def generate_unique_email(email):
    base_email, domain = email.split('@')
    index = 1
    while True:
        new_email = f"{base_email}+{index}@{domain}"
        if not User.objects.filter(email=new_email).exists():
            return new_email
        index += 1

def generate_unique_phone_number(phone_number):
    index = 1
    while True:
        new_phone_number = f"{phone_number}{index}"
        if not User.objects.filter(phone_number=new_phone_number).exists():
            return new_phone_number
        index += 1

def generate_unique_username(username):
    index = 1
    while True:
        new_username = f"{username}{index}"
        if not User.objects.filter(username=new_username).exists():
            return new_username
        index += 1

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def clone_user(request):
    parent_id = request.data.get('parent_id')
    password = request.data.get('password')

    if not parent_id or not password:
        return Response({'error': 'Please provide both parent_id and password'},
                        status=status.HTTP_400_BAD_REQUEST)

    try:
        parent_user = User.objects.get(id=parent_id)
    except User.DoesNotExist:
        return Response({'error': 'Parent user with the given id does not exist'},
                        status=status.HTTP_404_NOT_FOUND)

    new_email = generate_unique_email(parent_user.email) if parent_user.email else None
    new_phone_number = generate_unique_phone_number(parent_user.phone_number) if parent_user.phone_number else None
    new_username = generate_unique_username(parent_user.username) if parent_user.username else None

    

    data = {
        'id': parent_user.id,
        'email': new_email,
        'phone_number': new_phone_number,
        'username': new_username,
        'password': password,
        'role': parent_user.role,
        'gender': parent_user.gender,
        'marital_status': parent_user.marital_status,
        'parent_id': parent_id,
        'business_admin': True,
    }
    serializer = UserCloneSerializer(data=data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({'user': UserCloneSerializer(user).data, 'refresh': str(refresh), 'access': str(refresh.access_token)},
                        status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def google_signup_webhook(request):
    authorization_code = request.GET.get('code', None)
    if authorization_code:
        params = {
                'client_id': config('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY'),
                'client_secret': config('SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET'),
                'grant_type': 'authorization_code',
                'code': authorization_code,
                'redirect_uri': config('SOCIAL_AUTH_GOOGLE_OAUTH2_REDIRECT_URI'),
            }

        response = requests.post(URL_GOOGLE_TOKEN, data=params)
        if response.status_code != 200:
            logger.error(params)
            logger.error(
                f'Something gone wrong for user during registering google get token: '
                f'{response.status_code} -- {response.content}')
            raise ValidationError(
                {'authorization_code': ['Google get token error, please try again later.']},
            )

        res = response.json()
        extra_data = {
            'access_token': res.get('access_token', ''),
            'refresh_token': res.get('refresh_token', ''),
            'id_token': res.get('id_token', ''),
            'token_type': res.get('token_type', ''),
            'expires': res.get('expires_in', ''),
            'expires_in': res.get('expires_in', ''),
            'first_auth_time': int(time.time()),
            'auth_time': int(time.time()),
            'auth_time_count': 1,
        }

        access_token = extra_data['access_token']

        """
        Get email from google api
        Note: Need to enable People API in project
        URL: https://developers.google.com/people/api/rest/v1/people/get
        Response: https://developers.google.com/people/api/rest/v1/people#Person
        """
        headers = {'Authorization': f'Bearer {access_token}'}
        params = {
            'personFields': 'emailAddresses,birthdays,names',
        }
        try:
            response = requests.get(URL_GOOGLE_ME, headers=headers, params=params)
        except Exception as e:
            logger.error(f'userinfo.email error: {str(e)}')
            raise
        else:
            if response.status_code == status.HTTP_200_OK:
                result = response.json()
                emails = result.get('emailAddresses', [])
                if len(emails) > 0:
                    for email in emails:
                        metadata = email.get('metadata', {})
                        extra_data['email'] = email.get('value')
                        if metadata.get('primary'):
                            break

                user = User.objects.filter(email=extra_data.get('email')).first()

                if not user:
                    names = result.get('names', [])
                    if len(names) > 0:
                        for name in names:
                            metadata = name.get('metadata', {})

                            user_new = User.objects.create(
                                email=extra_data.get('email'),
                            )

                            UserSocialAuth.objects.create(
                                provider=PROVIDER_GOOGLE_OAUTH2,
                                extra_data=extra_data,
                                user_id=user_new.id,
                            )
                            if metadata.get('primary'):
                                break
                else:
                    user_social_auth = UserSocialAuth.objects.filter(user_id=user.id).first()
                    if not user_social_auth:
                        UserSocialAuth.objects.create(
                            provider=PROVIDER_GOOGLE_OAUTH2,
                            extra_data=extra_data,
                            user_id=user.id,
                        )
                    else:
                        user_social_auth.provider = PROVIDER_GOOGLE_OAUTH2
                        user_social_auth.extra_data = extra_data
                        user_social_auth.save()
        return HttpResponse(json.dumps({
            'access_token': str(extra_data.get('access_token')),
        }), status=status.HTTP_200_OK)
    return HttpResponse(json.dumps({'access_token': ''}), status=status.HTTP_400_BAD_REQUEST)

# @api_view(['POST'])
# def change_password(request):
#     serializer = ChangePasswordSerializer(data=request.data)

#     if serializer.is_valid():
#         user = request.user

#         # Check if the old password is correct
#         old_password = serializer.validated_data.get('old_password')
#         if not user.check_password(old_password):
#             return Response({'error': 'Old password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)

#         # Set the new password and save the user
#         new_password = serializer.validated_data.get('new_password')
#         user.set_password(new_password)
#         user.save()

#         return Response({'message': 'Password updated successfully'}, status=status.HTTP_200_OK)

#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# @api_view(['POST'])
# def forgot_password(request):
#     serializer = ForgotPasswordSerializer(data=request.data)

#     if serializer.is_valid():
#         email = serializer.validated_data.get('email')
#         try:
#             user = User.objects.get(email=email)
#         except User.DoesNotExist:
#             return Response({'error': 'User with the given email does not exist'}, status=status.HTTP_404_NOT_FOUND)

#         # Create a JWT token containing the user's email
#         token_payload = {
#             'email': user.email,
#             'exp': datetime.utcnow() + timedelta(hours=1),  # Token expiration time (1 hour in this case)
#         }
#         token = jwt.encode(token_payload, settings.SECRET_KEY, algorithm='HS256')

#         # Send the reset password link to the user's email
#         reset_password_link = f'http://your-domain/reset_password?token={token}'
#         send_mail(
#             'Reset Your Password',
#             f'Click the link below to reset your password:\n\n{reset_password_link}',
#             settings.EMAIL_HOST_USER,
#             [user.email],
#             fail_silently=False,
#         )

#         return Response({'message': 'Password reset link has been sent to your email'}, status=status.HTTP_200_OK)

#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)