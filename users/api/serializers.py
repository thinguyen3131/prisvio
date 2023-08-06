from rest_framework import serializers
from django.contrib.auth import get_user_model
from ..models import User

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'password', 'role', 'gender', 'marital_status','parent_id']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

class UserCloneSerializer(serializers.ModelSerializer):
    parent_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone_number', 'password', 'role', 'gender', 'marital_status', 'parent_id']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        parent_id = validated_data.pop('parent_id', None)
        password = validated_data.get('password')

        # Create a new user with the provided data
        user = User.objects.create(**validated_data)

        # Set the parent_id if provided
        if parent_id:
            user.parent_id = parent_id.id

        # Set the password for the user
        user.set_password(password)
        user.save()

        return user

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)