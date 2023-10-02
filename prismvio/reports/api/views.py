from rest_framework import generics

from prismvio.reports.api.serializers import ReportSerializer, ReportTypeSerializer
from prismvio.reports.models import ReportType


class ReportTypeListAPIView(generics.ListAPIView):
    permission_classes = ()
    queryset = ReportType.objects.all()
    serializer_class = ReportTypeSerializer


class ReportCreateAPIView(generics.CreateAPIView):
    permission_classes = ()
    serializer_class = ReportSerializer
