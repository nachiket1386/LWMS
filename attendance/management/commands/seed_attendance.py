from django.core.management.base import BaseCommand
from accounts.models import User
from companies.models import Company
from attendance.models import Employee, AttendanceRecord, Shift, CostCenter, UploadBatch
from django.utils import timezone
import random
from datetime import timedelta, datetime

class Command(BaseCommand):
    help = 'Seeds attendance data'

    def handle(self, *args, **options):
        # Create Company
        company, _ = Company.objects.get_or_create(name='Acme Corp', slug='acme')
        
        # Ensure user exists
        if User.objects.count() == 0:
            user = User.objects.create_superuser('admin', 'admin@example.com', 'password')
        else:
            user = User.objects.filter(is_superuser=True).first()
            if not user:
                 user = User.objects.first()
        
        user.company = company
        user.save()

        # Create Shifts
        shift_morning, created = Shift.objects.get_or_create(
            company=company, 
            name='Morning', 
            defaults={
                'start_time': datetime.strptime('09:00', '%H:%M').time(),
                'end_time': datetime.strptime('17:00', '%H:%M').time()
            }
        )
        if not created and isinstance(shift_morning.start_time, str):
             # Fix legacy data if any
             shift_morning.start_time = datetime.strptime(shift_morning.start_time, '%H:%M:%S' if len(shift_morning.start_time) > 5 else '%H:%M').time()
             shift_morning.end_time = datetime.strptime(shift_morning.end_time, '%H:%M:%S' if len(shift_morning.end_time) > 5 else '%H:%M').time()
             shift_morning.save()
             
        shift_night, _ = Shift.objects.get_or_create(
            company=company, 
            name='Night', 
            defaults={
                'start_time': datetime.strptime('21:00', '%H:%M').time(),
                'end_time': datetime.strptime('05:00', '%H:%M').time()
            }
        )

        # Create Employees (1000 employees)
        self.stdout.write("Creating employees...")
        employees = []
        existing_employees = set(Employee.objects.filter(company=company).values_list('employee_id', flat=True))
        
        new_employees = []
        for i in range(1000):
            emp_id = f'EMP{i:04d}'
            if emp_id not in existing_employees:
                new_employees.append(Employee(
                    company=company,
                    employee_id=emp_id,
                    first_name=f'First{i}',
                    last_name=f'Last{i}',
                    email=f'emp{i}@acme.com'
                ))
        
        if new_employees:
            Employee.objects.bulk_create(new_employees)
            self.stdout.write(f"Created {len(new_employees)} employees")

        employees = list(Employee.objects.filter(company=company))

        # Create Attendance Records (100 days * 1000 employees = 100k rows)
        self.stdout.write("Creating attendance records...")
        start_date = timezone.now().date() - timedelta(days=100)
        
        batch = UploadBatch.objects.create(
            company=company,
            uploader=user,
            file_name='seed_data',
            upload_type='attendance',
            status='completed'
        )
        
        records = []
        # Check existing records to avoid duplicates if run multiple times
        existing_dates = set(AttendanceRecord.objects.filter(company=company).values_list('date', flat=True))
        
        # This check is too simple (doesn't check employee), but good enough for seeding.
        # Better: just try to insert and ignore conflicts if using postgres, but sqlite doesn't support ignore_conflicts easily in older django or without unique constraint matching
        # We have unique_together = ('employee', 'date')
        
        count = 0
        for day in range(100):
            current_date = start_date + timedelta(days=day)
            
            # Simple check: if we have roughly enough records for this day, skip
            if AttendanceRecord.objects.filter(company=company, date=current_date).count() > 800:
                continue

            for emp in employees:
                # Randomize a bit
                if random.random() > 0.1: # 90% attendance
                    records.append(AttendanceRecord(
                        company=company,
                        employee=emp,
                        date=current_date,
                        check_in=datetime.combine(current_date, shift_morning.start_time),
                        check_out=datetime.combine(current_date, shift_morning.end_time),
                        shift=shift_morning,
                        batch=batch
                    ))
            
            if len(records) > 5000:
                AttendanceRecord.objects.bulk_create(records, ignore_conflicts=True)
                count += len(records)
                records = []
                self.stdout.write(f"Created records for day {day}")
        
        if records:
            AttendanceRecord.objects.bulk_create(records, ignore_conflicts=True)
            count += len(records)
            
        self.stdout.write(self.style.SUCCESS(f'Successfully seeded attendance data. Total records created: {count}'))
