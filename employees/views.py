from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Q
from .models import Employee, Attendance
from .serializers import EmployeeSerializer, AttendanceSerializer, AttendanceListSerializer
from datetime import datetime


class EmployeeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Employee CRUD operations
    """
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

    def list(self, request):
        """Get all employees"""
        try:
            employees = self.get_queryset()
            serializer = self.get_serializer(employees, many=True)
            return Response({
                'success': True,
                'count': employees.count(),
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'success': False,
                'message': 'Failed to fetch employees',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, pk=None):
        """Get single employee"""
        try:
            employee = self.get_object()
            serializer = self.get_serializer(employee)
            return Response({
                'success': True,
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except Employee.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Employee not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'message': 'Failed to fetch employee',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request):
        """Create new employee"""
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'success': True,
                    'message': 'Employee created successfully',
                    'data': serializer.data
                }, status=status.HTTP_201_CREATED)
            return Response({
                'success': False,
                'message': 'Validation failed',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'success': False,
                'message': 'Failed to create employee',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, pk=None):
        """Delete employee"""
        try:
            employee = self.get_object()
            employee_id = employee.employee_id
            employee.delete()
            return Response({
                'success': True,
                'message': f'Employee {employee_id} deleted successfully'
            }, status=status.HTTP_200_OK)
        except Employee.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Employee not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'message': 'Failed to delete employee',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['get'])
    def attendances(self, request, pk=None):
        """Get attendance records for a specific employee"""
        try:
            employee = self.get_object()
            attendances = employee.attendances.all()
            
            # Optional date filtering
            date_param = request.query_params.get('date', None)
            if date_param:
                try:
                    filter_date = datetime.strptime(date_param, '%Y-%m-%d').date()
                    attendances = attendances.filter(date=filter_date)
                except ValueError:
                    return Response({
                        'success': False,
                        'message': 'Invalid date format. Use YYYY-MM-DD'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = AttendanceListSerializer(attendances, many=True)
            
            # Calculate statistics
            total_records = attendances.count()
            present_count = attendances.filter(status='Present').count()
            absent_count = attendances.filter(status='Absent').count()
            
            return Response({
                'success': True,
                'employee': {
                    'id': employee.id,
                    'employee_id': employee.employee_id,
                    'full_name': employee.full_name,
                    'department': employee.department
                },
                'statistics': {
                    'total_records': total_records,
                    'present_days': present_count,
                    'absent_days': absent_count
                },
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except Employee.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Employee not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'message': 'Failed to fetch attendance records',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AttendanceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Attendance CRUD operations
    """
    queryset = Attendance.objects.all().select_related('employee')
    serializer_class = AttendanceSerializer

    def get_serializer_class(self):
        if self.action == 'list':
            return AttendanceListSerializer
        return AttendanceSerializer

    def list(self, request):
        """Get all attendance records"""
        try:
            attendances = self.get_queryset()
            
            # Optional filtering by date
            date_param = request.query_params.get('date', None)
            if date_param:
                try:
                    filter_date = datetime.strptime(date_param, '%Y-%m-%d').date()
                    attendances = attendances.filter(date=filter_date)
                except ValueError:
                    return Response({
                        'success': False,
                        'message': 'Invalid date format. Use YYYY-MM-DD'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Optional filtering by employee
            employee_id = request.query_params.get('employee_id', None)
            if employee_id:
                attendances = attendances.filter(employee__employee_id__iexact=employee_id)
            
            serializer = self.get_serializer(attendances, many=True)
            return Response({
                'success': True,
                'count': attendances.count(),
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'success': False,
                'message': 'Failed to fetch attendance records',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request):
        """Mark attendance"""
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'success': True,
                    'message': 'Attendance marked successfully',
                    'data': serializer.data
                }, status=status.HTTP_201_CREATED)
            return Response({
                'success': False,
                'message': 'Validation failed',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'success': False,
                'message': 'Failed to mark attendance',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, pk=None):
        """Delete attendance record"""
        try:
            attendance = self.get_object()
            attendance.delete()
            return Response({
                'success': True,
                'message': 'Attendance record deleted successfully'
            }, status=status.HTTP_200_OK)
        except Attendance.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Attendance record not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'message': 'Failed to delete attendance record',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get dashboard statistics"""
        try:
            # Employee statistics
            total_employees = Employee.objects.count()
            
            # Attendance statistics
            total_attendance_records = Attendance.objects.count()
            present_today = Attendance.objects.filter(
                date=datetime.now().date(),
                status='Present'
            ).count()
            absent_today = Attendance.objects.filter(
                date=datetime.now().date(),
                status='Absent'
            ).count()
            
            # Department wise count
            departments = Employee.objects.values('department').annotate(
                count=Count('id')
            ).order_by('-count')
            
            return Response({
                'success': True,
                'data': {
                    'total_employees': total_employees,
                    'total_attendance_records': total_attendance_records,
                    'today_present': present_today,
                    'today_absent': absent_today,
                    'departments': list(departments)
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'success': False,
                'message': 'Failed to fetch dashboard data',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
