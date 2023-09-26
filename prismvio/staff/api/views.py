from datetime import datetime

from django.db.models import Q
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, UpdateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from prismvio.staff.api.serializers import (
    CancelInviteSerializer,
    LinkToStaffSerializer,
    StaffAcceptedInviteSerializer,
    StaffSerializer,
    UnlinkStaffSerializer,
)
from prismvio.staff.constants import STAFF_SORT_FIELDS
from prismvio.staff.enums import InviteStatusEnum, LinkStatusEnum
from prismvio.staff.exceptions import MerchantIDNotNullException, StaffDoesNotExists
from prismvio.staff.models import Staff
from prismvio.users.api.serializers import EmailPhoneLookupSerializer
from prismvio.users.tasks import invite_new_user


class StaffListCreateAPIView(ListCreateAPIView):
    serializer_class = StaffSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.request.method == "GET":
            self.permission_classes = (AllowAny,)
        return super().get_permissions()

    def get_queryset(self):
        merchant_id = self.request.GET.get("merchant_id", "")
        updated_at = self.request.GET.get("updated_at")
        sort_by = self.request.GET.get("sort_by")
        order = self.request.GET.get("order", "asc")
        if not merchant_id:
            raise MerchantIDNotNullException()
        where = Q(merchant=merchant_id)
        if updated_at:
            where &= Q(updated_at__gt=updated_at)

        queryset = Staff.objects.select_related("merchant").filter(where)

        if sort_by and sort_by in STAFF_SORT_FIELDS:
            order_by = sort_by
            if order == "desc":
                order_by = f"-{sort_by}"
            queryset = queryset.order_by(order_by)
        return queryset


class StaffDetailAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = StaffSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.request.method == "GET":
            self.permission_classes = (AllowAny,)
        return super().get_permissions()

    def get_object(self):
        try:
            return Staff.objects.get(pk=self.kwargs.get("pk"))
        except Staff.DoesNotExist:
            raise StaffDoesNotExists()

    def perform_destroy(self, instance):
        instance.deleted_at = datetime.now()
        instance.updated_at = datetime.now()
        instance.service.clear()
        instance.save()


class InviteStaffAPI(APIView):
    def post(self, request, *args, **kwargs):
        emails = request.data["emails"]
        serializer = EmailPhoneLookupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        invite_new_user.delay(**serializer.validated_data)
        Staff.objects.filter(email__in=emails).update(
            invite_status=InviteStatusEnum.PENDING.value, link_status=LinkStatusEnum.UNLINKED.value
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


class LinkToStaffAPIView(UpdateAPIView):
    serializer_class = LinkToStaffSerializer

    def get_object(self):
        try:
            return Staff.objects.get(pk=self.kwargs.get("pk"))
        except Staff.DoesNotExist:
            raise StaffDoesNotExists()


class StaffAcceptedInviteAPIView(UpdateAPIView):
    serializer_class = StaffAcceptedInviteSerializer

    def get_object(self):
        try:
            return Staff.objects.get(pk=self.kwargs.get("pk"))
        except Staff.DoesNotExist:
            raise StaffDoesNotExists()


class CancelInviteAPIView(UpdateAPIView):
    serializer_class = CancelInviteSerializer

    def get_object(self):
        try:
            return Staff.objects.get(pk=self.kwargs.get("pk"))
        except Staff.DoesNotExist:
            raise StaffDoesNotExists()


class UnlinkStaffAPIView(UpdateAPIView):
    serializer_class = UnlinkStaffSerializer

    def get_object(self):
        try:
            return Staff.objects.get(pk=self.kwargs.get("pk"))
        except Staff.DoesNotExist:
            raise StaffDoesNotExists()
