import re

from django.conf import settings
from django.contrib.auth import login
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from social_django.utils import load_backend, load_strategy

from prismvio.social_login.exceptions import GCSMissingFilenameException, GCSMissingFileTypeException
from prismvio.social_login.services.signed_url import GCSService, GCSSignedUrlService


@api_view(["POST"])
@permission_classes([AllowAny])
def google_login(request):
    strategy = load_strategy(request)
    backend = load_backend(strategy=strategy, name="google-oauth2", redirect_uri=None)

    try:
        user = backend.do_auth(request.data.get("access_token"))
        login(request, user)
    except Exception as e:
        check_email = str(e).split()
        string = check_email[9]
        regex = r"\w+@\w+\.\w+"
        emails = re.findall(regex, string)
        return Response({"is_registered": False, "error": emails}, status=status.HTTP_505_HTTP_VERSION_NOT_SUPPORTED)
    refresh = RefreshToken.for_user(user)
    user.email_verified = True
    user.save()

    if user.is_registered:
        return Response(
            {
                "id": user.id,
                "user_avatar": user.avatar,
                "parent_id": user.parent.id if user.parent else "",
                "banner": user.banner,
                "full_name": f"{user.last_name} {user.first_name}",
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "is_registered": user.is_registered,
                "profile_type": user.profile_type,
            }
        )
    else:
        return Response(
            {
                "id": user.id,
                "user_avatar": user.avatar,
                "parent_id": user.parent.id if user.parent else "",
                "banner": user.banner,
                "full_name": f"{user.last_name} {user.first_name}",
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "is_registered": user.is_registered,
                "profile_type": user.profile_type,
            }
        )


class GCSUploadSignedUrlAPIView(GenericAPIView):
    def get(self, request):
        is_private = request.GET.get("is_private", False)
        filename = request.GET.get("filename", "")
        file_type = request.GET.get("file_type", "")
        if not filename:
            raise GCSMissingFilenameException()
        if not file_type:
            raise GCSMissingFileTypeException()
        bucket_name = settings.GCS_PUBLIC_BUCKET_NAME
        media_url = f"{settings.GCS_STORAGE_DOMAIN}/{bucket_name}/{filename}"
        # This URL is valid for 30 minutes
        seconds = 1800
        if is_private:
            bucket_name = settings.GCS_PRIVATE_BUCKET_NAME
            media_url = ""
        url = GCSSignedUrlService(bucket_name, filename, file_type).generate_upload_signed_url_v4(seconds=1800)
        return Response(
            {
                "data": {
                    "signed_url": url,
                    "expire_time": seconds,
                    "filename": filename,
                    "media_url": media_url,
                    "is_private": is_private,
                },
            }
        )


class GCSStorageAPIView(GenericAPIView):
    def delete(self, request):
        blobs = request.data.get("data", [])
        GCSService().delete_blobs(blobs)
        return Response()
