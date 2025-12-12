from rest_framework import serializers
from .models import Employee, AttendanceRecord, MandayRecord, OvertimeEntry, UploadBatch, Shift, CostCenter, UploadError

class ShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shift
        fields = '__all__'

class CostCenterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CostCenter
        fields = '__all__'

class EmployeeSerializer(serializers.ModelSerializer):
    cost_center_code = serializers.CharField(source='cost_center.code', read_only=True)
    
    class Meta:
        model = Employee
        fields = '__all__'

class AttendanceRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceRecord
        fields = '__all__'

class MandayRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = MandayRecord
        fields = '__all__'

class OvertimeEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = OvertimeEntry
        fields = '__all__'

class UploadErrorSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadError
        fields = '__all__'

class UploadBatchSerializer(serializers.ModelSerializer):
    errors = UploadErrorSerializer(many=True, read_only=True)
    
    class Meta:
        model = UploadBatch
        fields = '__all__'
