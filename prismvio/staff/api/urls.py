from django.conf import settings
from django.urls import path
from rest_framework.routers import DefaultRouter, SimpleRouter

from prismvio.staff.api.views import (
    CancelInviteAPIView,
    InviteStaffAPI,
    LinkToStaffAPIView,
    StaffAcceptedInviteAPIView,
    StaffDetailAPIView,
    StaffListCreateAPIView,
    UnlinkStaffAPIView,
    UserListAPIView,
)

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()


# staff
urlpatterns = [
    path("", StaffListCreateAPIView.as_view(), name="staffs-list-create"),
    path("invite/", InviteStaffAPI.as_view(), name="staffs-invite"),
    path("users/", UserListAPIView.as_view(), name="staffs-users"),
    path("<int:pk>/", StaffDetailAPIView.as_view(), name="staffs-detail"),
    path("<int:pk>/link/", LinkToStaffAPIView.as_view(), name="link-to-staff"),
    path("<int:pk>/unlink/", UnlinkStaffAPIView.as_view(), name="merchant-unlink"),
    path("<int:pk>/cancel/", CancelInviteAPIView.as_view(), name="staff-cancel-invite"),
    path("<int:pk>/accept/", StaffAcceptedInviteAPIView.as_view(), name="staff-accept-invite"),
]
