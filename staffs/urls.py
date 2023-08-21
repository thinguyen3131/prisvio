from django.urls import path

from rest_framework_extensions.routers import ExtendedSimpleRouter

from staffs.api.views import (CancelInviteAPIView, InviteStaffAPI, LinkToStaffAPIView, StaffAcceptedInviteAPIView,
                             StaffDetailAPIView, StaffListCreateAPIView, UnlinkStaffAPIView, UserListAPIView)

router = ExtendedSimpleRouter()


urlpatterns = [
    path('staffs/', StaffListCreateAPIView.as_view(), name='staffs-list-create'),
    path('staffs/invite/', InviteStaffAPI.as_view(), name='staffs-invite'),
    path('staffs/users/', UserListAPIView.as_view(), name='staffs-users'),
    path('staffs/<int:pk>/', StaffDetailAPIView.as_view(), name='staffs-detail'),
    path('staffs/<int:pk>/link/', LinkToStaffAPIView.as_view(), name='link-to-staff'),
    path('staffs/<int:pk>/unlink/', UnlinkStaffAPIView.as_view(), name='merchant-unlink'),
    path('staffs/<int:pk>/cancel/', CancelInviteAPIView.as_view(),
         name='staff-cancel-invite'),
    path('staffs/<int:pk>/accept/', StaffAcceptedInviteAPIView.as_view(), name='staff-accept-invite'),
]
