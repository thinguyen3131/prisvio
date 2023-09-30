from copy import deepcopy
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
from prismvio.staff.enums import InviteStatusEnum, LinkStatusEnum
from prismvio.staff.exceptions import MerchantIDAndUserIDNullException, StaffDoesNotExists
from prismvio.staff.models import Staff
from prismvio.users.api.serializers import EmailPhoneLookupSerializer
from prismvio.users.tasks import invite_new_user
from prismvio.utils.drf_utils import search


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
        query_params = deepcopy(self.request.query_params)
        merchant_id = query_params.get("merchant_id", None)
        user_id = query_params.get("user_id", None)
        updated_at = query_params.get("updated_at")
        if not merchant_id and not user_id:
            raise MerchantIDAndUserIDNullException()
        where = Q()
        if merchant_id:
            where &= Q(merchant=merchant_id)
        if user_id:
            where &= Q(user=user_id)
        if updated_at:
            where &= Q(updated_at__gt=updated_at)
        queryset = Staff.objects.select_related("user").select_related("merchant").filter(where)
        return search(
            queryset=queryset,
            query_params=query_params,
            model=Staff,
            exclude_fields=["updated_at", "merchant", "user"],
        )


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
        instance.services.clear()
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
