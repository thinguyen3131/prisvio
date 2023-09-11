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
    path("staffs/", StaffListCreateAPIView.as_view(), name="staffs-list-create"),
    path("staffs/invite/", InviteStaffAPI.as_view(), name="staffs-invite"),
    path("staffs/users/", UserListAPIView.as_view(), name="staffs-users"),
    path("staffs/<int:pk>/", StaffDetailAPIView.as_view(), name="staffs-detail"),
    path("staffs/<int:pk>/link/", LinkToStaffAPIView.as_view(), name="link-to-staff"),
    path("staffs/<int:pk>/unlink/", UnlinkStaffAPIView.as_view(), name="merchant-unlink"),
    path("staffs/<int:pk>/cancel/", CancelInviteAPIView.as_view(), name="staff-cancel-invite"),
    path("staffs/<int:pk>/accept/", StaffAcceptedInviteAPIView.as_view(), name="staff-accept-invite"),
]
