from odoo import models, fields ,api

class Customer(models.Model):
    _inherit = 'res.partner'

    pan_no = fields.Char(string="PAN No")
    consultant = fields.Char(string="Consultant")
    quality_manager = fields.Char(string="Quality Manager")
    quality_manager_no = fields.Char(string="Quality Manager Number")    
    projects  = fields.One2many('res.partner.project','contact_id', string="Projects" )
    po_numbers  = fields.One2many('res.partner.po','contact_id', string="Po Number" )



    # vat = fields.Char(string="GSTIN")



class CustomerProject(models.Model):
    _name = 'res.partner.project'
    _rec_name = "project_name" 

    contact_id = fields.Many2one('res.partner',string="Contact ID")
    project_name = fields.Char(string="Project Name")


class CustomerPO(models.Model):
    _name = 'res.partner.po'
    _rec_name = "po_number" 

    contact_id = fields.Many2one('res.partner',string="Contact ID")
    po_number = fields.Char(string="PO Number")
    # vat = fields.Char(string="GSTIN")


class AccountMoveInherited(models.Model):
    _inherit = 'account.move'

    project_name = fields.Many2one('res.partner.project',string="Project")
    po_number = fields.Many2one('res.partner.po',string="PO")
    customer_reference = fields.Char(string="Customer Reference")
    contact_person = fields.Many2one('res.partner',string="Contact Person")

    @api.onchange("partner_id")
    def set_domain_for_project_name(self):
        if self.partner_id:
            domain = [('contact_id', '=', self.partner_id.id)]
     
            result = { 
                        'domain': {'project_name': domain} 
                    } 
            return result
    
    @api.onchange("partner_id")
    def set_domain_for_po_number(self):
        if self.partner_id:
            domain = [('contact_id', '=', self.partner_id.id)]
     
            result = { 
                        'domain': {'po_number': domain} 
                    } 
            return result
    

    @api.onchange("partner_id")
    def set_domain_for_contact_person(self):
        if self.partner_id:
            domain = [('parent_id', '=', self.partner_id.id),('type', '=', 'contact')]
     
            result = { 
                        'domain': {'contact_person': domain} 
                    } 
            return result


class AccountMoveLineInherited(models.Model):
    _inherit = 'account.move.line'

    report_no = fields.Char(string="Report Number")