from django.urls import path

from prismvio.social_login.api.views import GCSStorageAPIView, GCSUploadSignedUrlAPIView, google_login

urlpatterns = [
    path("google/login/", google_login, name="google-login"),
    path("google/signed-url/", GCSUploadSignedUrlAPIView.as_view(), name="gcs"),
    path("google/storage/", GCSStorageAPIView.as_view(), name="gcs-storage"),
]
