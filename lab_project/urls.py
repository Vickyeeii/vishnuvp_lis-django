from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from . import views
from .api_views import (
    UserViewSet, PatientViewSet, TestCategoryViewSet,
    LabTestViewSet, LabOrderViewSet, ResultEntryViewSet
)

# DRF Router Setup
router = DefaultRouter()
router.register(r'patients', PatientViewSet, basename='patient-api')
router.register(r'tests/assays', LabTestViewSet, basename='test-api')
router.register(r'tests/menus', TestCategoryViewSet, basename='category-api')
router.register(r'orders', LabOrderViewSet, basename='order-api')
router.register(r'results', ResultEntryViewSet, basename='result-api')
router.register(r'users', UserViewSet, basename='user-api')


from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_logout_view(request):
    return Response({"message": "Successfully logged out."})

urlpatterns = [
    # Admin Interface
    path('admin/', admin.site.urls),

    # Session-Based UI Views
    path('', views.login_view, name='login'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('patient-register/', views.patient_register_view, name='patient_register'),
    path('patients/', views.patient_list_view, name='patients'),
    path('orders/', views.order_entry_view, name='orders'),
    path('phlebotomist-worklist/', views.phlebotomist_worklist_view, name='phlebotomist_worklist'),
    path('technician-worklist/', views.technician_worklist_view, name='technician_worklist'),
    path('lab-report/', views.lab_report_view, name='lab_report'),
    path('admin-tests/', views.admin_tests_view, name='admin_tests'),
    path('admin-users/', views.admin_users_view, name='admin_users'),
    path('logout/', views.logout_view, name='logout'),

    # REST Framework & JWT Endpoints (/api/v1/)
    path('api/v1/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/auth/login/', TokenObtainPairView.as_view(), name='token_login'),
    path('api/v1/auth/logout/', api_logout_view, name='token_logout'),
    path('api/v1/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/', include(router.urls)),
]