import pandas as pd
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from .models import UploadBatch, UploadError, Employee, AttendanceRecord, Shift, CostCenter, MandayRecord, OvertimeEntry
import logging
import json

logger = logging.getLogger(__name__)

class DataIngester:
    def __init__(self, file, upload_type, company, user):
        self.file = file
        self.upload_type = upload_type
        self.company = company
        self.user = user
        self.batch = None
        self.df = None

    def run(self):
        try:
            self._create_batch()
            self._parse_file()
            self._process_data()
            self._finish_batch()
        except Exception as e:
            logger.exception("Global upload error")
            if self.batch:
                self.batch.status = 'failed'
                self.batch.error_count += 1
                UploadError.objects.create(
                    batch=self.batch,
                    error_message=f"Global error: {str(e)}"
                )
                self.batch.save()
            else:
                raise e

    def _create_batch(self):
        self.batch = UploadBatch.objects.create(
            uploader=self.user,
            company=self.company,
            file_name=self.file.name,
            upload_type=self.upload_type,
            status='processing'
        )

    def _parse_file(self):
        try:
            if self.file.name.endswith('.csv'):
                self.df = pd.read_csv(self.file)
            else:
                self.df = pd.read_excel(self.file)
            
            # Normalize headers: strip whitespace, lowercase, replace spaces with underscores
            self.df.columns = [str(c).strip().lower().replace(' ', '_') for c in self.df.columns]
            
            self.batch.row_count = len(self.df)
            self.batch.save()
        except Exception as e:
            raise ValidationError(f"Failed to read file: {str(e)}")

    def _process_data(self):
        method_name = f"_process_{self.upload_type}"
        if hasattr(self, method_name):
            getattr(self, method_name)()
        else:
            raise ValidationError(f"Unknown upload type: {self.upload_type}")

    def _finish_batch(self):
        self.batch.status = 'completed' if self.batch.error_count == 0 else 'completed_with_errors'
        self.batch.save()

    def _log_error(self, row_index, message, row_data=None):
        self.batch.error_count += 1
        
        # specific handling for row_data serialization
        if row_data is not None:
            try:
                # Convert pandas series to dict, then to json
                if hasattr(row_data, 'to_dict'):
                    data_dict = row_data.to_dict()
                    # Convert timestamp objects to string
                    for k, v in data_dict.items():
                        if pd.api.types.is_datetime64_any_dtype(v) or isinstance(v, (pd.Timestamp, datetime.datetime, datetime.date)):
                            data_dict[k] = str(v)
                    row_json = json.dumps(data_dict, default=str)
                else:
                    row_json = json.dumps(row_data, default=str)
            except:
                row_json = str(row_data)
        else:
            row_json = None

        UploadError.objects.create(
            batch=self.batch,
            row_number=row_index + 1, # User friendly (1-based)
            error_message=message,
            row_data=row_json
        )

    def _process_employee(self):
        required = ['employee_id', 'first_name', 'last_name']
        missing = [col for col in required if col not in self.df.columns]
        if missing:
             raise ValidationError(f"Missing required columns: {', '.join(missing)}")
        
        cost_centers = {c.code: c for c in CostCenter.objects.filter(company=self.company)}
        
        valid_records = []
        
        for index, row in self.df.iterrows():
            try:
                emp_id = str(row['employee_id']).strip()
                if not emp_id:
                     self._log_error(index, "Empty Employee ID", row)
                     continue

                email = row.get('email')
                if pd.isna(email): email = None
                
                cc_code = row.get('cost_center_code')
                cc = None
                if cc_code and pd.notna(cc_code):
                    cc = cost_centers.get(str(cc_code).strip())
                
                record = Employee(
                    company=self.company,
                    employee_id=emp_id,
                    first_name=row['first_name'],
                    last_name=row['last_name'],
                    email=email,
                    department=row.get('department'),
                    cost_center=cc
                )
                valid_records.append(record)
            except Exception as e:
                self._log_error(index, str(e), row)
        
        if valid_records:
            Employee.objects.bulk_create(
                valid_records,
                update_conflicts=True,
                unique_fields=['company', 'employee_id'],
                update_fields=['first_name', 'last_name', 'email', 'department', 'cost_center', 'updated_at']
            )
            self.batch.success_count = len(valid_records)

    def _process_attendance(self):
        required = ['employee_id', 'date']
        missing = [col for col in required if col not in self.df.columns]
        if missing:
             raise ValidationError(f"Missing required columns: {', '.join(missing)}")
        
        employees = {e.employee_id: e for e in Employee.objects.filter(company=self.company)}
        shifts = {s.name: s for s in Shift.objects.filter(company=self.company)}
        
        valid_records = []
        
        for index, row in self.df.iterrows():
            try:
                emp_id = str(row['employee_id']).strip()
                if emp_id not in employees:
                    self._log_error(index, f"Employee ID {emp_id} not found", row)
                    continue
                
                date_str = str(row['date'])
                try:
                    date_val = pd.to_datetime(date_str).date()
                except:
                    self._log_error(index, f"Invalid date format: {date_str}", row)
                    continue

                check_in = None
                if 'check_in' in row and pd.notna(row['check_in']):
                    try:
                        check_in = pd.to_datetime(row['check_in'])
                        # Handle Excel 1900/1970 dates or default "today" from pandas when parsing time-only strings
                        is_default_date = (
                            check_in.date() == pd.Timestamp('1900-01-01').date() or 
                            check_in.date() == pd.Timestamp('1970-01-01').date() or
                            (check_in.date() == pd.Timestamp.now().date() and date_val != pd.Timestamp.now().date())
                        )
                        
                        if is_default_date:
                             check_in = check_in.replace(year=date_val.year, month=date_val.month, day=date_val.day)
                    except:
                         self._log_error(index, f"Invalid check_in format: {row['check_in']}", row)
                         continue

                check_out = None
                if 'check_out' in row and pd.notna(row['check_out']):
                    try:
                        check_out = pd.to_datetime(row['check_out'])
                        is_default_date = (
                            check_out.date() == pd.Timestamp('1900-01-01').date() or 
                            check_out.date() == pd.Timestamp('1970-01-01').date() or
                            (check_out.date() == pd.Timestamp.now().date() and date_val != pd.Timestamp.now().date())
                        )
                        
                        if is_default_date:
                             check_out = check_out.replace(year=date_val.year, month=date_val.month, day=date_val.day)
                             # Handle overnight shift crossing midnight?
                             if check_in and check_out < check_in:
                                 check_out += pd.Timedelta(days=1)
                    except:
                        self._log_error(index, f"Invalid check_out format: {row['check_out']}", row)
                        continue
                
                shift = None
                if 'shift' in row and pd.notna(row['shift']):
                    shift_name = str(row['shift']).strip()
                    shift = shifts.get(shift_name)

                record = AttendanceRecord(
                    company=self.company,
                    employee=employees[emp_id],
                    date=date_val,
                    check_in=check_in,
                    check_out=check_out,
                    shift=shift,
                    batch=self.batch
                )
                valid_records.append(record)

            except Exception as e:
                self._log_error(index, str(e), row)

        if valid_records:
            AttendanceRecord.objects.bulk_create(
                valid_records,
                update_conflicts=True,
                unique_fields=['employee', 'date'],
                update_fields=['check_in', 'check_out', 'shift', 'batch', 'updated_at']
            )
            self.batch.success_count = len(valid_records)

    def _process_manday(self):
        required = ['employee_id', 'date', 'manday_value']
        missing = [col for col in required if col not in self.df.columns]
        if missing:
             raise ValidationError(f"Missing required columns: {', '.join(missing)}")
             
        employees = {e.employee_id: e for e in Employee.objects.filter(company=self.company)}
        
        valid_records = []
        for index, row in self.df.iterrows():
            try:
                emp_id = str(row['employee_id']).strip()
                if emp_id not in employees:
                    self._log_error(index, f"Employee ID {emp_id} not found", row)
                    continue
                    
                date_val = pd.to_datetime(row['date']).date()
                manday_val = row['manday_value']
                
                record = MandayRecord(
                    company=self.company,
                    employee=employees[emp_id],
                    date=date_val,
                    manday_value=manday_val,
                    batch=self.batch
                )
                valid_records.append(record)
            except Exception as e:
                self._log_error(index, str(e), row)
                
        if valid_records:
            MandayRecord.objects.bulk_create(
                valid_records,
                update_conflicts=True,
                unique_fields=['employee', 'date'],
                update_fields=['manday_value', 'batch', 'updated_at']
            )
            self.batch.success_count = len(valid_records)
            
    def _process_overtime(self):
        required = ['employee_id', 'date', 'hours']
        missing = [col for col in required if col not in self.df.columns]
        if missing:
             raise ValidationError(f"Missing required columns: {', '.join(missing)}")
             
        employees = {e.employee_id: e for e in Employee.objects.filter(company=self.company)}
        
        valid_records = []
        for index, row in self.df.iterrows():
            try:
                emp_id = str(row['employee_id']).strip()
                if emp_id not in employees:
                    self._log_error(index, f"Employee ID {emp_id} not found", row)
                    continue
                    
                date_val = pd.to_datetime(row['date']).date()
                hours = row['hours']
                
                record = OvertimeEntry(
                    company=self.company,
                    employee=employees[emp_id],
                    date=date_val,
                    hours=hours,
                    batch=self.batch
                )
                valid_records.append(record)
            except Exception as e:
                self._log_error(index, str(e), row)
                
        if valid_records:
            OvertimeEntry.objects.bulk_create(
                valid_records,
                update_conflicts=True,
                unique_fields=['employee', 'date'],
                update_fields=['hours', 'batch', 'updated_at']
            )
            self.batch.success_count = len(valid_records)

