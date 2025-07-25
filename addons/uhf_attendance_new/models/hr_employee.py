from odoo import models, fields

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    uhf_tag_ids = fields.One2many('uhf.tag', 'employee_id', string='UHF RFID Tags')

