from rest_framework import serializers
from .models import Employee, Attendance
from django.core.validators import EmailValidator
import re


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['id', 'employee_id', 'full_name', 'email', 'department', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_employee_id(self, value):
        """Validate employee ID"""
        if not value:
            raise serializers.ValidationError("Employee ID is required")
        
        # Convert to uppercase for validation
        value = value.upper()
        
        # Check format
        if not re.match(r'^[A-Z0-9]+$', value):
            raise serializers.ValidationError("Employee ID must contain only letters and numbers")
        
        # Check uniqueness for new records or updates
        if self.instance:
            # Update case: check if another employee has this ID
            if Employee.objects.filter(employee_id=value).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError("Employee ID already exists")
        else:
            # Create case: check if ID exists
            if Employee.objects.filter(employee_id=value).exists():
                raise serializers.ValidationError("Employee ID already exists")
        
        return value

    def validate_full_name(self, value):
        """Validate full name"""
        if not value or not value.strip():
            raise serializers.ValidationError("Full name is required")
        
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Full name must be at least 2 characters long")
        
        return value.strip()

    def validate_email(self, value):
        """Validate email"""
        if not value:
            raise serializers.ValidationError("Email is required")
        
        # Convert to lowercase
        value = value.lower()
        
        # Validate email format
        validator = EmailValidator()
        try:
            validator(value)
        except:
            raise serializers.ValidationError("Please enter a valid email address")
        
        # Check uniqueness
        if self.instance:
            # Update case: check if another employee has this email
            if Employee.objects.filter(email=value).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError("Email already exists")
        else:
            # Create case: check if email exists
            if Employee.objects.filter(email=value).exists():
                raise serializers.ValidationError("Email already exists")
        
        return value

    def validate_department(self, value):
        """Validate department"""
        if not value or not value.strip():
            raise serializers.ValidationError("Department is required")
        
        return value.strip()


class AttendanceSerializer(serializers.ModelSerializer):
    employee_id = serializers.CharField(source='employee.employee_id', read_only=True)
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    employee_pk = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(),
        source='employee',
        write_only=True
    )

    class Meta:
        model = Attendance
        fields = ['id', 'employee', 'employee_id', 'employee_name', 'employee_pk', 'date', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'employee', 'employee_id', 'employee_name', 'created_at', 'updated_at']

    def validate_date(self, value):
        """Validate date"""
        if not value:
            raise serializers.ValidationError("Date is required")
        return value

    def validate_status(self, value):
        """Validate status"""
        if not value:
            raise serializers.ValidationError("Status is required")
        
        if value not in ['Present', 'Absent']:
            raise serializers.ValidationError("Status must be either 'Present' or 'Absent'")
        
        return value

    def validate(self, data):
        """Validate unique attendance record"""
        employee = data.get('employee')
        date = data.get('date')

        if employee and date:
            # Check for existing attendance
            if self.instance:
                # Update case
                if Attendance.objects.filter(employee=employee, date=date).exclude(id=self.instance.id).exists():
                    raise serializers.ValidationError("Attendance for this employee on this date already exists")
            else:
                # Create case
                if Attendance.objects.filter(employee=employee, date=date).exists():
                    raise serializers.ValidationError("Attendance for this employee on this date already exists")

        return data


class AttendanceListSerializer(serializers.ModelSerializer):
    """Serializer for listing attendance with employee details"""
    employee_id = serializers.CharField(source='employee.employee_id')
    employee_name = serializers.CharField(source='employee.full_name')
    department = serializers.CharField(source='employee.department')

    class Meta:
        model = Attendance
        fields = ['id', 'employee', 'employee_id', 'employee_name', 'department', 'date', 'status', 'created_at']
