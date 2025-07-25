from odoo import http, fields
from datetime import datetime, time
from pytz import timezone, utc
import logging

_logger = logging.getLogger(__name__)

class AttendanceAPI(http.Controller):

    @http.route('/api/attendance/update', type='json', auth='none', methods=['POST'], csrf=False)
    def update_attendance(self, **post):
        uid = post.get('uid')
        if not uid:
            return {'status': 'fail', 'message': 'Missing uid'}

        try:
            # Get current datetime in Kolkata timezone
            kolkata = timezone('Asia/Kolkata')
            now_local = datetime.now(kolkata)
            today_date = now_local.date()

            # Convert to UTC naive for storage in Odoo DB
            now_utc_naive = now_local.astimezone(utc).replace(tzinfo=None)

            # Compute UTC range for "today" in Kolkata
            today_start_local = datetime.combine(today_date, time.min)
            today_end_local = datetime.combine(today_date, time.max)
            today_start_utc = kolkata.localize(today_start_local).astimezone(utc).replace(tzinfo=None)
            today_end_utc = kolkata.localize(today_end_local).astimezone(utc).replace(tzinfo=None)

            # Search employee
            employee = http.request.env['hr.employee'].sudo().search([('barcode', '=', uid)], limit=1)
            if not employee:
                return {'status': 'fail', 'message': 'Employee not found'}

            # Get today's attendance in UTC range
            attendance = http.request.env['hr.attendance'].sudo().search([
                ('employee_id', '=', employee.id),
                ('check_in', '>=', today_start_utc),
                ('check_in', '<=', today_end_utc),
            ], limit=1)

            if attendance:
                # If already checked in but no check_out → update it
                if not attendance.check_out:
                    attendance.check_out = now_utc_naive
                    action = 'check_out'
                else:
                    # Already checked out — update again if needed (last scan wins)
                    attendance.check_out = now_utc_naive
                    action = 'check_out_updated'
            else:
                # First scan today: check-in
                http.request.env['hr.attendance'].sudo().create({
                    'employee_id': employee.id,
                    'check_in': now_utc_naive,
                })
                action = 'check_in'

            # Log the API usage
            http.request.env['biometric.log'].sudo().create({
                'uid': uid,
                'timestamp': now_utc_naive,
                'status': 'success',
                'message': f'{action} recorded'
            })

            return {
                'status': 'success',
                'message': f'{action} recorded at {now_local.strftime("%Y-%m-%d %H:%M:%S")}'
            }

        except Exception as e:
            _logger.error(f"[Biometric API] Error: {e}")
            http.request.env['biometric.log'].sudo().create({
                'uid': uid or 'unknown',
                'timestamp': fields.Datetime.now(),
                'status': 'fail',
                'message': str(e)
            })
            return {'status': 'fail', 'message': str(e)}


    @http.route('/api/attendance/update_time', type='json', auth='none', methods=['POST'], csrf=False)
    def update_attendance_time(self, **post):
        _logger.info(f"[Biometric API] Received JSON: {post}")

        uid = post.get('uid')
        timestamp_str = post.get('timestamp')

        if not uid or not timestamp_str:
            return {'status': 'fail', 'message': 'Missing uid or timestamp'}

        try:
            # Convert input timestamp (Asia/Kolkata) to naive UTC
            local_tz = timezone('Asia/Kolkata')
            local_dt = local_tz.localize(datetime.fromisoformat(timestamp_str))
            utc_dt = local_dt.astimezone(utc).replace(tzinfo=None)

            # Check if the timestamp is today (in Kolkata time)
            server_today = datetime.now(local_tz).date()
            if local_dt.date() != server_today:
                return {'status': 'fail', 'message': 'Attendance can only be recorded for today.'}

            # Search employee
            employee = http.request.env['hr.employee'].sudo().search([('barcode', '=', uid)], limit=1)
            if not employee:
                return {'status': 'fail', 'message': 'Employee not found'}

            # Search today's attendance (only 1 per day)
            today_attendance = http.request.env['hr.attendance'].sudo().search([
                ('employee_id', '=', employee.id),
                ('check_in', '>=', utc_dt.replace(hour=0, minute=0, second=0, microsecond=0)),
                ('check_in', '<', utc_dt.replace(hour=23, minute=59, second=59, microsecond=999999))
            ], limit=1)

            if today_attendance:
                # If already has check_out, update it to new time
                today_attendance.check_out = utc_dt
                action = 'check_out'
            else:
                # No record for today yet → check_in
                http.request.env['hr.attendance'].sudo().create({
                    'employee_id': employee.id,
                    'check_in': utc_dt,
                })
                action = 'check_in'

            # Log the event
            http.request.env['biometric.log'].sudo().create({
                'uid': uid,
                'timestamp': utc_dt,
                'status': 'success',
                'message': f'{action} recorded'
            })

            return {'status': 'success', 'message': f'{action} recorded'}

        except Exception as e:
            _logger.error(f"[Biometric API] Error: {e}")
            http.request.env['biometric.log'].sudo().create({
                'uid': uid or 'unknown',
                'timestamp': fields.Datetime.now(),
                'status': 'fail',
                'message': str(e)
            })
            return {'status': 'fail', 'message': str(e)}
