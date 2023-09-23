from django.http import JsonResponse
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from prismvio.core.permissions import MerchantPermission
from prismvio.merchant.api.serializers import ExclusionDateSerializer, TimeslotCollectionMerchantSerializer
from prismvio.merchant.exceptions import MerchantDoesNotExistsException
from prismvio.merchant.models import ExclusionDate, Merchant, TimeslotCollectionMerchant
from prismvio.utils.drf_utils import search

from .serializers import MerchantPreviewSerializer, MerchantSerializer


class MerchantListCreateView(generics.ListCreateAPIView):
    serializer_class = MerchantSerializer
    permission_classes = [MerchantPermission]

    def get_queryset(self):
        queryset = search(
            query_params=self.request.query_params,
            model=Merchant,
        )
        return queryset

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class MerchantDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MerchantPreviewSerializer
    permission_classes = [MerchantPermission]

    def get_object(self):
        try:
            return Merchant.objects.get(pk=self.kwargs.get("pk"))
        except Merchant.DoesNotExist:
            raise MerchantDoesNotExistsException()


class TimeslotsAPIView(APIView):
    permission_classes = [MerchantPermission]

    def get(self, request, merchant_id):
        try:
            timeslot_collection = TimeslotCollectionMerchant.objects.get(merchant=merchant_id)
            serializer = TimeslotCollectionMerchantSerializer(timeslot_collection)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except TimeslotCollectionMerchant.DoesNotExist:
            return Response(
                {"error": "Timeslot collection not found for the given merchant"}, status=status.HTTP_404_NOT_FOUND
            )

    def post(self, request, merchant_id, *args, **kwargs):
        data = request.data
        weekly = data.get("weekly", [])
        daily = data.get("daily", [])

        merchant = Merchant.objects.get(pk=merchant_id)

        # Check if timeslot collection already exists for the merchant
        timeslot_collection, created = TimeslotCollectionMerchant.objects.get_or_create(merchant=merchant)

        # Update the timeslot collection with the provided data
        timeslot_collection.weekly = weekly
        timeslot_collection.daily = daily
        timeslot_collection.save()

        # Serialize the response
        serializer = TimeslotCollectionMerchantSerializer(timeslot_collection)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ShiffsAPIView(APIView):
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.request.method == "GET":
            self.permission_classes = (AllowAny,)
        return super().get_permissions()

    def get(self, request, merchant_id):
        try:
            timeslot_collection = TimeslotCollectionMerchant.objects.get(merchant_id=merchant_id)
            shifts = timeslot_collection.shifts
            return JsonResponse({"shifts": shifts}, status=200)  # Return 200 OK with the shifts data
        except TimeslotCollectionMerchant.DoesNotExist:
            return JsonResponse({"error": "Merchant not found"}, status=404)

    def post(self, request, merchant_id, *args, **kwargs):
        data = request.data
        shifts = data.get("shifts", [])

        # Fetch the timeslot collection for the given merchant_id
        timeslot_collection, created = TimeslotCollectionMerchant.objects.get_or_create(merchant_id=merchant_id)

        # Update the shifts for the timeslot collection
        timeslot_collection.shifts = shifts
        timeslot_collection.save()

        return JsonResponse({}, status=200)  # Return 200 OK with an empty response body


class ExclusionDateAPIVIew(APIView):
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.request.method == "GET":
            self.permission_classes = (AllowAny,)
        return super().get_permissions()

    def get(self, request, merchant_id):
        exclusion_dates = ExclusionDate.objects.filter(merchant_id=merchant_id)
        serializer = ExclusionDateSerializer(exclusion_dates, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, merchant_id, *args, **kwargs):
        datetimes = request.data.get("datetimes", [])
        data = []
        for datetime in datetimes:
            datetime["merchant"] = merchant_id
            serializer = ExclusionDateSerializer(data=datetime)
            if serializer.is_valid():
                serializer.save()
                data.append(serializer.data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(data, status=status.HTTP_201_CREATED)

    def put(self, request, merchant_id, *args, **kwargs):
        datetimes = request.data.get("datetimes", [])
        data = []
        for datetime in datetimes:
            try:
                exclusion_date = ExclusionDate.objects.get(id=datetime.get("id"))
                serializer = ExclusionDateSerializer(exclusion_date, data=datetime, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    data.append(serializer.data)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except ExclusionDate.DoesNotExist:
                return Response({"error": "Exclusion date not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(data, status=status.HTTP_200_OK)

    def delete(self, request, merchant_id):
        ids_to_delete = request.data
        ExclusionDate.objects.filter(id__in=ids_to_delete).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
