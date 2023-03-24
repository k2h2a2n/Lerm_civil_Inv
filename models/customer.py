from odoo import models,fields

class Customer(models.Model):
    _inherit = 'res.partner'

    pan_no = fields.Char(string="PAN No")


class AccountMoveInherited(models.Model):
    _inherit = 'account.move'

    project_name = fields.Char(string="Project Name")
    po_number = fields.Char(string="PO Number")
    customer_reference = fields.Char(string="Customer Reference")
    default_contact = fields.Many2one('res.partner',string="Default Contact")


class AccountMoveLineInherited(models.Model):
    _inherit = 'account.move.line'

    report_no = fields.Char(string="Report Number")