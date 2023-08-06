from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import authenticate, login
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .serializers import UserSerializer, UserCloneSerializer, ChangePasswordSerializer
from django.core.mail import send_mail
from django.conf import settings
import jwt
from datetime import datetime, timedelta

User = get_user_model()

@api_view(['POST'])
def signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({'refresh': str(refresh), 'access': str(refresh.access_token)}, status=status.HTTP_201_CREATED)
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
        'parent_id': parent_user,
    }

    serializer = UserCloneSerializer(data=data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({'user': UserCloneSerializer(user).data, 'refresh': str(refresh), 'access': str(refresh.access_token)},
                        status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def change_password(request):
    serializer = ChangePasswordSerializer(data=request.data)

    if serializer.is_valid():
        user = request.user

        # Check if the old password is correct
        old_password = serializer.validated_data.get('old_password')
        if not user.check_password(old_password):
            return Response({'error': 'Old password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)

        # Set the new password and save the user
        new_password = serializer.validated_data.get('new_password')
        user.set_password(new_password)
        user.save()

        return Response({'message': 'Password updated successfully'}, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def forgot_password(request):
    serializer = ForgotPasswordSerializer(data=request.data)

    if serializer.is_valid():
        email = serializer.validated_data.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User with the given email does not exist'}, status=status.HTTP_404_NOT_FOUND)

        # Create a JWT token containing the user's email
        token_payload = {
            'email': user.email,
            'exp': datetime.utcnow() + timedelta(hours=1),  # Token expiration time (1 hour in this case)
        }
        token = jwt.encode(token_payload, settings.SECRET_KEY, algorithm='HS256')

        # Send the reset password link to the user's email
        reset_password_link = f'http://your-domain/reset_password?token={token}'
        send_mail(
            'Reset Your Password',
            f'Click the link below to reset your password:\n\n{reset_password_link}',
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )

        return Response({'message': 'Password reset link has been sent to your email'}, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)