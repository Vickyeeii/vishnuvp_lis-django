from rest_framework import serializers
from accounts.models import CustomUser
from patients.models import Patient
from labtests.models import LabTest, TestCategory, SampleCollection
from orders.models import LabOrder
from results.models import ResultEntry


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'role', 'phone_number', 'is_active']
        extra_kwargs = {'password': {'write_only': True}}


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = '__all__'


class TestCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TestCategory
        fields = '__all__'


class LabTestSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')

    class Meta:
        model = LabTest
        fields = ['id', 'category', 'category_name', 'test_name', 'test_code', 'sample_type', 'price', 'turnaround_time', 'status']


class SampleCollectionSerializer(serializers.ModelSerializer):
    collected_by_name = serializers.ReadOnlyField(source='collected_by.username')

    class Meta:
        model = SampleCollection
        fields = '__all__'


class LabOrderSerializer(serializers.ModelSerializer):
    patient_name = serializers.SerializerMethodField()
    physician_name = serializers.ReadOnlyField(source='physician.username')
    tests_details = LabTestSerializer(many=True, read_only=True, source='tests')

    class Meta:
        model = LabOrder
        fields = ['id', 'patient', 'patient_name', 'physician', 'physician_name', 'tests', 'tests_details', 'priority', 'status', 'clinical_notes', 'ordered_at']

    def get_patient_name(self, obj):
        return f"{obj.patient.first_name} {obj.patient.last_name}"

    def validate_tests(self, value):
        for test in value:
            if test.status != 'active':
                raise serializers.ValidationError(f"Cannot order inactive assay: {test.test_name}")
        return value

    def update(self, instance, validated_data):
        new_status = validated_data.get('status', instance.status)
        if new_status < instance.status:
            raise serializers.ValidationError("Order status cannot be rolled back.")
        return super().update(instance, validated_data)


class ResultEntrySerializer(serializers.ModelSerializer):
    entered_by_name = serializers.ReadOnlyField(source='entered_by.username')
    test_name = serializers.ReadOnlyField(source='test.test_name')

    class Meta:
        model = ResultEntry
        fields = ['id', 'order', 'test', 'test_name', 'result_value', 'normal_range', 'unit', 'entered_by', 'entered_by_name', 'flag', 'status', 'remarks', 'created_at']

    def validate_order(self, value):
        if value.status != 3:
            raise serializers.ValidationError("Results can only be entered when the order is In-Lab (status 3).")
        return value
