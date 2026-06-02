# backend/apps/reporting/urls.py
from django.urls import path
from .views import (
    DashboardSummaryView,
    KPIListView,
    RevenueChartView,
    ExportReportView
)

urlpatterns = [
    path('dashboard/', DashboardSummaryView.as_view(), name='reporting-dashboard'),
    path('kpis/', KPIListView.as_view(), name='reporting-kpis'),
    path('revenue/', RevenueChartView.as_view(), name='reporting-revenue'),
    path('export/', ExportReportView.as_view(), name='reporting-export'),
]
