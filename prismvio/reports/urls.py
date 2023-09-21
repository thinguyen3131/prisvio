from django.urls import path

from prismvio.reports.api import views

urlpatterns = [
    path('reports/', views.ReportCreateAPIView.as_view(), name='report-create'),
    path('reports/type/', views.ReportTypeListAPIView.as_view(), name='report-type'),
]
