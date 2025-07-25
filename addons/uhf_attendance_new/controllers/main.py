from odoo import http, fields
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class UHFAPIController(http.Controller):

    @http.route('/api/uhf/verify', type='json', auth='none', methods=['POST'], csrf=False)
    def verify_uhf_tag(self, **post):
        try:
            _logger.debug("UHF API Called")
            tag_data = post.get('tag_data')
            attend = post.get('attendance')

            if not tag_data:
                return {"status": 500, "access": -1, "message": "Missing tag_data"}

            tag = request.env['uhf.tag'].sudo().search([('name', '=', tag_data)], limit=1)
            if not tag:
                _logger.info("RFID tag not matched: %s", tag_data)
                return {"status": 200, "access": 0}

            found_employee = tag.employee_id
            _logger.debug("Tag matched for employee: %s", found_employee.name)

            if attend == 1:
                # Mark attendance
                check_in_out = request.env['hr.attendance'].sudo()
                latest_attendance = check_in_out.search([
                    ('employee_id', '=', found_employee.id)
                ], order='check_in desc', limit=1)

                if latest_attendance and not latest_attendance.check_out:
                    latest_attendance.write({'check_out': fields.Datetime.now()})
                    _logger.info("Checked out: %s", found_employee.name)
                else:
                    check_in_out.create({
                        'employee_id': found_employee.id,
                        'check_in': fields.Datetime.now()
                    })
                    _logger.info("Checked in: %s", found_employee.name)

            return {"status": 200, "access": 1}

        except Exception as e:
            _logger.exception("Error in UHF API")
            return {"status": 500, "access": -1, "message": str(e)}

