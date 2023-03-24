from odoo import models,fields

class Customer(models.Model):
    _inherit = 'res.partner'

    pan_no = fields.Char(string="PAN No")

class AccountMoveInherited(models.Model):
    _inherit = 'account.move'

    project_name = fields.Char(string="Project Name")
    default_contact = fields.Many2one('res.partner',string="Default Contact")