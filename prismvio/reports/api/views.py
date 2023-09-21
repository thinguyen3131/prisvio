from rest_framework import generics
from rest_framework.permissions import AllowAny

from prismvio.reports.api.serializers import ReportSerializer, ReportTypeSerializer
from prismvio.reports.models import ReportType


class ReportTypeListAPIView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    queryset = ReportType.objects.all()
    serializer_class = ReportTypeSerializer


class ReportCreateAPIView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = ReportSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
