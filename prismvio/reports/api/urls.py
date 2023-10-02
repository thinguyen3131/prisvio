from django.urls import path

from prismvio.reports.api import views

urlpatterns = [
    path("", views.ReportCreateAPIView.as_view(), name="report-create"),
    path("type/", views.ReportTypeListAPIView.as_view(), name="report-type"),
]
