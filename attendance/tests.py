from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from accounts.models import User
from companies.models import Company
from .models import Attendance, ManDays, Overtime, UploadBatch, AuditLog


class AttendanceModelTest(TestCase):
    def setUp(self):
        self.company = Company.objects.create(
            name='Test Company',
            slug='test-company'
        )
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass',
            role='ADMIN',
            company=self.company
        )

    def test_create_attendance(self):
        attendance = Attendance.objects.create(
            company=self.company,
            employee=self.user,
            attendance_date=timezone.now().date(),
            status='PRESENT',
            hours_worked=Decimal('8.0')
        )
        self.assertEqual(attendance.status, 'PRESENT')
        self.assertEqual(attendance.version, 1)

    def test_unique_attendance_constraint(self):
        date = timezone.now().date()
        Attendance.objects.create(
            company=self.company,
            employee=self.user,
            attendance_date=date,
            status='PRESENT'
        )
        with self.assertRaises(Exception):
            Attendance.objects.create(
                company=self.company,
                employee=self.user,
                attendance_date=date,
                status='ABSENT'
            )


class ManDaysModelTest(TestCase):
    def setUp(self):
        self.company = Company.objects.create(
            name='Test Company',
            slug='test-company'
        )
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass',
            role='ADMIN',
            company=self.company
        )

    def test_create_mandays(self):
        mandays = ManDays.objects.create(
            company=self.company,
            employee=self.user,
            project='Project A',
            mandays_date=timezone.now().date(),
            days_allocated=Decimal('5.0')
        )
        self.assertEqual(mandays.project, 'Project A')
        self.assertEqual(mandays.days_allocated, Decimal('5.0'))

    def test_mandays_aggregate(self):
        date = timezone.now().date()
        ManDays.objects.create(
            company=self.company,
            employee=self.user,
            project='Project A',
            mandays_date=date,
            days_allocated=Decimal('5.0'),
            days_utilized=Decimal('3.0')
        )
        ManDays.objects.create(
            company=self.company,
            employee=self.user,
            project='Project B',
            mandays_date=date,
            days_allocated=Decimal('3.0'),
            days_utilized=Decimal('2.0')
        )
        from django.db.models import Sum
        agg = ManDays.objects.filter(company=self.company).aggregate(
            total=Sum('days_allocated')
        )
        self.assertEqual(agg['total'], Decimal('8.0'))


class OvertimeModelTest(TestCase):
    def setUp(self):
        self.company = Company.objects.create(
            name='Test Company',
            slug='test-company'
        )
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass',
            role='ADMIN',
            company=self.company
        )

    def test_create_overtime(self):
        overtime = Overtime.objects.create(
            company=self.company,
            employee=self.user,
            overtime_date=timezone.now().date(),
            hours=Decimal('2.0')
        )
        self.assertEqual(overtime.hours, Decimal('2.0'))
        self.assertFalse(overtime.supervisor_approved)

    def test_overtime_approval(self):
        overtime = Overtime.objects.create(
            company=self.company,
            employee=self.user,
            overtime_date=timezone.now().date(),
            hours=Decimal('2.0')
        )
        supervisor = User.objects.create_user(
            username='supervisor',
            email='supervisor@example.com',
            password='testpass',
            role='ADMIN',
            company=self.company
        )
        overtime.supervisor_approved = True
        overtime.approved_by = supervisor
        overtime.save()
        
        overtime.refresh_from_db()
        self.assertTrue(overtime.supervisor_approved)
        self.assertEqual(overtime.approved_by, supervisor)


class AttendanceDashboardTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.company = Company.objects.create(
            name='Test Company',
            slug='test-company'
        )
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass',
            role='ADMIN',
            company=self.company
        )
        self.client.login(username='testuser', password='testpass')

    def test_dashboard_view(self):
        response = self.client.get(reverse('attendance:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'attendance/dashboard.html')

    def test_dashboard_metrics(self):
        today = timezone.now().date()
        Attendance.objects.create(
            company=self.company,
            employee=self.user,
            attendance_date=today,
            status='PRESENT'
        )
        
        response = self.client.get(reverse('attendance:dashboard'))
        self.assertEqual(response.context['total_attendance'], 1)
        self.assertEqual(response.context['present_today'], 1)


class AttendanceListTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.company = Company.objects.create(
            name='Test Company',
            slug='test-company'
        )
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass',
            role='ADMIN',
            company=self.company
        )
        self.client.login(username='testuser', password='testpass')

    def test_attendance_list_view(self):
        response = self.client.get(reverse('attendance:attendance_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'attendance/attendance_list.html')

    def test_attendance_filtering(self):
        today = timezone.now().date()
        Attendance.objects.create(
            company=self.company,
            employee=self.user,
            attendance_date=today,
            status='PRESENT'
        )
        
        response = self.client.get(reverse('attendance:attendance_list'), {
            'date_from': today.strftime('%Y-%m-%d'),
            'date_to': today.strftime('%Y-%m-%d'),
            'status': 'PRESENT'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['records']), 1)

    def test_attendance_create(self):
        response = self.client.post(reverse('attendance:attendance_create'), {
            'employee': self.user.id,
            'attendance_date': timezone.now().date().strftime('%Y-%m-%d'),
            'status': 'PRESENT',
            'hours_worked': '8.0'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Attendance.objects.count(), 1)

    def test_attendance_edit_with_optimistic_locking(self):
        today = timezone.now().date()
        attendance = Attendance.objects.create(
            company=self.company,
            employee=self.user,
            attendance_date=today,
            status='PRESENT',
            hours_worked=Decimal('8.0'),
            version=1
        )
        
        response = self.client.post(
            reverse('attendance:attendance_edit', args=[attendance.id]),
            {
                'employee': self.user.id,
                'attendance_date': today.strftime('%Y-%m-%d'),
                'status': 'ABSENT',
                'hours_worked': '0',
                'version': '1'
            }
        )
        self.assertEqual(response.status_code, 302)
        
        attendance.refresh_from_db()
        self.assertEqual(attendance.status, 'ABSENT')
        self.assertEqual(attendance.version, 2)

    def test_attendance_delete(self):
        today = timezone.now().date()
        attendance = Attendance.objects.create(
            company=self.company,
            employee=self.user,
            attendance_date=today,
            status='PRESENT'
        )
        
        response = self.client.post(
            reverse('attendance:attendance_delete', args=[attendance.id])
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Attendance.objects.count(), 0)

    def test_attendance_export_csv(self):
        today = timezone.now().date()
        Attendance.objects.create(
            company=self.company,
            employee=self.user,
            attendance_date=today,
            status='PRESENT'
        )
        
        response = self.client.get(reverse('attendance:attendance_export'), {
            'format': 'csv'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')

    def test_attendance_export_excel(self):
        today = timezone.now().date()
        Attendance.objects.create(
            company=self.company,
            employee=self.user,
            attendance_date=today,
            status='PRESENT'
        )
        
        response = self.client.get(reverse('attendance:attendance_export'), {
            'format': 'excel'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('spreadsheet', response['Content-Type'])


class ManDaysListTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.company = Company.objects.create(
            name='Test Company',
            slug='test-company'
        )
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass',
            role='ADMIN',
            company=self.company
        )
        self.client.login(username='testuser', password='testpass')

    def test_mandays_list_view(self):
        response = self.client.get(reverse('attendance:mandays_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'attendance/mandays_list.html')

    def test_mandays_create(self):
        response = self.client.post(reverse('attendance:mandays_create'), {
            'employee': str(self.user.id),
            'project': 'Test Project',
            'mandays_date': timezone.now().date().strftime('%Y-%m-%d'),
            'days_allocated': '5.0',
            'days_utilized': '0'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ManDays.objects.count(), 1)

    def test_mandays_by_project_summary(self):
        today = timezone.now().date()
        ManDays.objects.create(
            company=self.company,
            employee=self.user,
            project='Project A',
            mandays_date=today,
            days_allocated=Decimal('5.0')
        )
        ManDays.objects.create(
            company=self.company,
            employee=self.user,
            project='Project B',
            mandays_date=today,
            days_allocated=Decimal('3.0')
        )
        
        response = self.client.get(reverse('attendance:mandays_by_project'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['summary']), 2)


class OvertimeListTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.company = Company.objects.create(
            name='Test Company',
            slug='test-company'
        )
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass',
            role='ADMIN',
            company=self.company
        )
        self.client.login(username='testuser', password='testpass')

    def test_overtime_list_view(self):
        response = self.client.get(reverse('attendance:overtime_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'attendance/overtime_list.html')

    def test_overtime_create(self):
        response = self.client.post(reverse('attendance:overtime_create'), {
            'employee': self.user.id,
            'overtime_date': timezone.now().date().strftime('%Y-%m-%d'),
            'hours': '2.0'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Overtime.objects.count(), 1)

    def test_overtime_by_employee_summary(self):
        today = timezone.now().date()
        Overtime.objects.create(
            company=self.company,
            employee=self.user,
            overtime_date=today,
            hours=Decimal('2.0')
        )
        Overtime.objects.create(
            company=self.company,
            employee=self.user,
            overtime_date=today + timedelta(days=1),
            hours=Decimal('3.0')
        )
        
        response = self.client.get(reverse('attendance:overtime_by_employee'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_hours'], Decimal('5.0'))


class AuditLogTest(TestCase):
    def setUp(self):
        self.company = Company.objects.create(
            name='Test Company',
            slug='test-company'
        )
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass',
            role='ADMIN',
            company=self.company
        )

    def test_audit_log_creation(self):
        log = AuditLog.objects.create(
            action='CREATE',
            user=self.user,
            company=self.company,
            record_type='Attendance',
            record_id=1
        )
        self.assertEqual(log.action, 'CREATE')
        self.assertEqual(log.record_type, 'Attendance')

    def test_audit_log_with_changes(self):
        changes = {'status': 'PRESENT', 'hours': '8.0'}
        log = AuditLog.objects.create(
            action='UPDATE',
            user=self.user,
            company=self.company,
            record_type='Attendance',
            record_id=1,
            changes=changes
        )
        self.assertEqual(log.changes, changes)


class RBACTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.company = Company.objects.create(
            name='Test Company',
            slug='test-company'
        )
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='testpass',
            role='ADMIN',
            company=self.company
        )
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='testpass',
            role='USER1',
            company=self.company
        )

    def test_admin_can_create_attendance(self):
        self.client.login(username='admin', password='testpass')
        response = self.client.post(reverse('attendance:attendance_create'), {
            'employee': self.user1.id,
            'attendance_date': timezone.now().date().strftime('%Y-%m-%d'),
            'status': 'PRESENT',
            'hours_worked': '8.0'
        })
        self.assertEqual(response.status_code, 302)

    def test_attendance_filtering_respects_company(self):
        self.client.login(username='admin', password='testpass')
        
        other_company = Company.objects.create(
            name='Other Company',
            slug='other-company'
        )
        other_user = User.objects.create_user(
            username='otheruser',
            email='otheruser@example.com',
            password='testpass',
            role='USER1',
            company=other_company
        )
        
        today = timezone.now().date()
        Attendance.objects.create(
            company=self.company,
            employee=self.user1,
            attendance_date=today,
            status='PRESENT'
        )
        Attendance.objects.create(
            company=other_company,
            employee=other_user,
            attendance_date=today,
            status='PRESENT'
        )
        
        response = self.client.get(reverse('attendance:attendance_list'))
        self.assertEqual(len(response.context['records']), 1)
