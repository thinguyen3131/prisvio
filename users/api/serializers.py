from rest_framework import serializers
from django.contrib.auth import get_user_model
from prisvio.utils.drf_utils import ImageFieldWithDefaultURLRepr

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
    parent_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False, allow_null=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone_number', 'password', 'role', 'gender', 'marital_status', 'parent_id', 'business_admin']
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


class UserBaseReprSerializer(serializers.ModelSerializer):
    # TODO move is_friend, is_follow, is_follower
    class Meta:
        model = User
        fields = ('email', 'phone_number', 'profile_type', 'about')

    def to_representation(self, instance):
        res = super().to_representation(instance)
        for f in User.PROFILE_FIELDS_MAP[instance.profile_type]['not_applicable']:
            res.pop(f, None)
        try:
            res.pop('about') if hasattr(
                res, 'pop') is True and instance.profile_type not in User.BRAND_PROFILE_TYPES else None
        except KeyError:
            pass
        return res


class UserPreviewSerializer(UserBaseReprSerializer):
    """Most minimal serializer for viewing users"""
    avatar = ImageFieldWithDefaultURLRepr(default_url_repr=User.DEFAULT_AVATAR_URL, read_only=True)

    class Meta:
        model = User
        fields = ('id', 'profile_type', 'first_name', 'middle_name', 'last_name', 'birth_date',
                  'brand_name', 'avatar', 'full_name', 'is_friend', 'is_follower', 'is_follow', 'currency', 'about',
                  'phone_number', 'email', 'location', 'full_location', 'latitude', 'longitude', 'background',
                  'is_active')
        read_only_fields = fields

    def to_representation(self, instance):
        serializer = super(UserPreviewSerializer, self).to_representation(instance)
        return serializer


class UserDetailSerializer(UserPreviewSerializer):
    """Serializer for viewing users (other than current users, use MeDetailSerializer for that)"""
    # TODO Move feature Subscribed, FollowedBy, NotificationSetting, counters, background, participant.
    class Meta:
        model = User
        fields = ('id', 'profile_type', 'birth_date',
                  'first_name', 'middle_name', 'last_name', 'brand_name', 'full_name',
                  'bio', 'title', 'website', 'avatar', 'email', 'phone_number',
                  'currency', 'about', 'location', 'full_location', 'latitude', 'longitude',
                  'country_code', 'verified_email_at', 'verified_phone_number_at')
        read_only_fields = fields

    def to_representation(self, instance):
        serializer = super().to_representation(instance)
        serializer['title'] = instance.title.name if instance.title else None
        return serializer


class EmailPhoneLookupSerializer(serializers.Serializer):
    emails = serializers.ListField(child=serializers.CharField(), required=False)
    phones = serializers.ListField(child=serializers.CharField(), required=False)
    link = serializers.CharField(required=False)

    def to_internal_value(self, data):
        for f in ['emails', 'phones']:
            if data.get(f):
                # Get unique elements, preserving order
                data[f] = list(dict.fromkeys(data[f]))
        return super().to_internal_value(data)

    def validate(self, data):
        if not data.get('emails') and not data.get('phones'):
            raise serializers.ValidationError('Fields "emails" or "phones" required.')
        return data
