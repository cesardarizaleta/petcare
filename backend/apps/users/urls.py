from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'supplies-test', views.SupplyViewSet, basename='supply-test')

urlpatterns = [
    # Auth endpoints
    path('register/', views.register, name='auth-register'),
    path('login/', views.login, name='auth-login'),
    path('refresh/', views.refresh, name='auth-refresh'),

    # Security & Test endpoints
    path('receptionist/', views.ReceptionistTestView.as_view(), name='receptionist_test'),
    path('manager/', views.ManagerDashboardView.as_view(), name='manager_dashboard'),
    path('me/', views.VerifyUserView.as_view(), name='verify_user'),
    path('logs/', views.LogDashboardView.as_view(), name='log_entry_list'),
    path('', include(router.urls)),
]
