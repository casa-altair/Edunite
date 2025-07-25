from odoo import models, fields

class UHFTag(models.Model):
    _name = 'uhf.tag'
    _description = 'UHF RFID Tag'

    name = fields.Char('RFID Tag', required=True, index=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, ondelete='cascade')

