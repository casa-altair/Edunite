# from odoo import models, fields

# class BiometricLog(models.Model):
#     _name = 'biometric.log'
#     _description = 'Biometric Attendance Log'

#     uid = fields.Char(required=True)
#     timestamp = fields.Datetime(required=True)
#     status = fields.Selection([
#         ('success', 'Success'),
#         ('fail', 'Fail')
#     ], default='success')
#     message = fields.Text()

from odoo import models, fields, api

class BiometricLog(models.Model):
    _name = 'biometric.log'
    _description = 'Biometric Attendance Log'

    uid = fields.Char(required=True)
    timestamp = fields.Datetime(required=True)
    status = fields.Selection([
        ('success', 'Success'),
        ('fail', 'Fail')
    ], default='success')
    message = fields.Text()

    employee_id = fields.Many2one('hr.employee', string='Employee', compute='_compute_employee', store=True)

    @api.depends('uid')
    def _compute_employee(self):
        for record in self:
            employee = self.env['hr.employee'].sudo().search([('barcode', '=', record.uid)], limit=1)
            record.employee_id = employee

