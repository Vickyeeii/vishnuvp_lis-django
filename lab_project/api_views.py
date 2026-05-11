from rest_framework import viewsets, permissions, filters
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend

from accounts.models import CustomUser
from patients.models import Patient
from labtests.models import LabTest, TestCategory
from orders.models import LabOrder
from results.models import ResultEntry

from .serializers import (
    UserSerializer, PatientSerializer, TestCategorySerializer,
    LabTestSerializer, LabOrderSerializer, ResultEntrySerializer
)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all().order_by('id')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'role']


class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all().order_by('-id')
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['first_name', 'last_name', 'mrn']
    filterset_fields = ['gender']


class TestCategoryViewSet(viewsets.ModelViewSet):
    queryset = TestCategory.objects.all().order_by('id')
    serializer_class = TestCategorySerializer
    permission_classes = [permissions.IsAuthenticated]


class LabTestViewSet(viewsets.ModelViewSet):
    queryset = LabTest.objects.all().order_by('test_code')
    serializer_class = LabTestSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['test_name', 'test_code']
    filterset_fields = ['status', 'sample_type']


from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

class LabOrderViewSet(viewsets.ModelViewSet):
    queryset = LabOrder.objects.all().order_by('-id')
    serializer_class = LabOrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['patient__first_name', 'patient__last_name', 'patient__mrn']
    filterset_fields = ['status', 'priority']

    @action(detail=True, methods=['patch'])
    def collect(self, request, pk=None):
        order = self.get_object()
        if order.status != 1:
            return Response({"error": "Can only collect samples for Ordered status."}, status=status.HTTP_400_BAD_REQUEST)
        order.status = 2
        order.save()
        return Response({"status": "Sample collected."})

    @action(detail=True, methods=['patch'])
    def receive(self, request, pk=None):
        order = self.get_object()
        if order.status != 2:
            return Response({"error": "Can only receive samples that have been collected."}, status=status.HTTP_400_BAD_REQUEST)
        order.status = 3
        order.save()
        return Response({"status": "Sample received in lab."})

    @action(detail=True, methods=['post'])
    def results(self, request, pk=None):
        order = self.get_object()
        if order.status != 3:
            return Response({"error": "Order must be In-Lab before adding results."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = ResultEntrySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(order=order)
            
            # Transition parent order to completed status
            order.status = 4
            order.save()
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def report(self, request, pk=None):
        order = self.get_object()
        if order.status != 4:
            return Response({"error": "Report only available for completed orders."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(order)
        return Response(serializer.data)


class ResultEntryViewSet(viewsets.ModelViewSet):
    queryset = ResultEntry.objects.all().order_by('-id')
    serializer_class = ResultEntrySerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['order__patient__first_name', 'order__patient__last_name', 'order__patient__mrn']
    filterset_fields = ['status', 'flag']
