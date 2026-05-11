from rest_framework import viewsets, permissions, filters
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend

from accounts.models import CustomUser
from patients.models import Patient
from labtests.models import LabTest, TestCategory, SampleCollection
from orders.models import LabOrder
from results.models import ResultEntry

from .serializers import (
    UserSerializer, PatientSerializer, TestCategorySerializer,
    LabTestSerializer, LabOrderSerializer, ResultEntrySerializer,
    DetailedLabOrderSerializer
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

    def get_serializer_class(self):
        if self.request.query_params.get('detailed') == 'true':
            return DetailedLabOrderSerializer
        return super().get_serializer_class()

    @action(detail=True, methods=['patch'])
    def collect(self, request, pk=None):
        order = self.get_object()
        if order.status != 1:
            return Response({"error": "Can only collect samples for Ordered status."}, status=status.HTTP_400_BAD_REQUEST)
        
        collected_by_id = request.data.get('collected_by')
        condition = request.data.get('condition', 'good')
        
        if not collected_by_id:
            return Response({"error": "collected_by is required."}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            collected_by = CustomUser.objects.get(id=collected_by_id)
        except CustomUser.DoesNotExist:
            return Response({"error": "Invalid collected_by user ID."}, status=status.HTTP_400_BAD_REQUEST)

        if SampleCollection.objects.filter(order=order).exists():
            return Response({"error": "Sample already collected for this order."}, status=status.HTTP_400_BAD_REQUEST)

        SampleCollection.objects.create(
            sample_id=f"SMP-{order.id}",
            order=order,
            collected_by=collected_by,
            sample_condition=condition,
            status='collected'
        )

        order.status = 2
        order.save()
        return Response({"status": "Sample collected and recorded."})

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
        
        # Determine if data is a list (bulk) or single object
        is_many = isinstance(request.data, list)
        serializer = ResultEntrySerializer(data=request.data, many=is_many)
        
        if serializer.is_valid():
            # For bulk save, we might need to iterate or DRF might handle it if we pass order
            if is_many:
                for item in serializer.validated_data:
                    ResultEntry.objects.update_or_create(
                        order=order,
                        test=item.get('test'),
                        defaults={
                            'entered_by': request.user,
                            'result_value': item.get('result_value'),
                            'flag': item.get('flag', 'normal'),
                            'remarks': item.get('remarks', ''),
                            'status': 'completed'
                        }
                    )
            else:
                serializer.save(order=order, entered_by=request.user)
            
            # Transition parent order to completed status
            order.status = 4
            order.save()
            
            return Response({"status": "Results saved successfully."}, status=status.HTTP_201_CREATED)
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

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_dashboard_stats(request):
    user = request.user
    role = user.role

    data = {}
    
    if role == 'admin':
        data['total_patients'] = Patient.objects.count()
        data['total_orders'] = LabOrder.objects.count()
        data['pending_collections'] = LabOrder.objects.filter(status=1).count()
        data['completed_reports'] = LabOrder.objects.filter(status=4).count()
    elif role in ['physician', 'nurse']:
        data['completed_reports'] = LabOrder.objects.filter(status=4).count()
        data['total_patients'] = Patient.objects.count()
        
        recent_patients = Patient.objects.all().order_by('-id')[:5]
        data['recent_patients'] = PatientSerializer(recent_patients, many=True).data
    elif role == 'phlebotomist':
        data['pending_collections'] = LabOrder.objects.filter(status=1).count()
    elif role in ['technician', 'lab_technician']:
        data['pending_in_lab'] = LabOrder.objects.filter(status=2).count()
        data['completed_reports'] = LabOrder.objects.filter(status=4).count()

    return Response(data)
