from odoo import models, fields ,api

import logging

_logger = logging.getLogger(__name__)

class Customer(models.Model):
    _inherit = 'res.partner'

    pan_no = fields.Char(string="PAN No")
    consultant = fields.Char(string="Consultant")
    quality_manager = fields.Char(string="Quality Manager")
    quality_manager_no = fields.Char(string="Quality Manager Number")    
    projects  = fields.One2many('res.partner.project','contact_id', string="Projects" )
    po_numbers  = fields.One2many('res.partner.po','contact_id', string="Po Number" )
    bank_name = fields.Char(string="Bank Name")
    ac_no = fields.Char(string="A/C No.")
    ifsc_code = fields.Char(string="IFSC Code")
    branch_name = fields.Char(string="Branch Name")
    sac_code = fields.Char(string="SAC Code")



    # vat = fields.Char(string="GSTIN")



class CustomerProject(models.Model):
    _name = 'res.partner.project'
    _rec_name = "project_name" 

    contact_id = fields.Many2one('res.partner',string="Contact ID")
    project_name = fields.Char(string="Project Name")
    closed_boolean = fields.Boolean(string="Closed")


class CustomerPO(models.Model):
    _name = 'res.partner.po'
    _rec_name = "po_number" 

    contact_id = fields.Many2one('res.partner',string="Contact ID")
    po_number = fields.Char(string="PO Number")
    closed_boolean = fields.Boolean(string="Closed")

    # vat = fields.Char(string="GSTIN")


class AccountMoveInherited(models.Model):
    _inherit = 'account.move'

    project_name = fields.Many2one('res.partner.project',string="Project")
    po_number = fields.One2many('account.move.po','account_move_id',string="PO Number")
    customer_reference = fields.Char(string="Customer Reference")
    contact_person = fields.Many2one('res.partner',string="Contact Person")



    @api.onchange("partner_id")
    def set_domain_for_project_name(self):
        if self.partner_id:
            domain = [('contact_id', '=', self.partner_id.id),('closed_boolean', '=', False)]
     
            result = { 
                        'domain': {'project_name': domain} 
                    } 
            return result
    
    # @api.onchange("partner_id")
    # def set_domain_for_po_number(self):
    #     if self.partner_id:
    #         domain = [('contact_id', '=', self.partner_id.id),('closed_boolean', '=', False)]
     
    #         result = { 
    #                     'domain': {'po_number': domain} 
    #                 } 
    #         return result
    

    @api.onchange("partner_id")
    def set_domain_for_contact_person(self):
        if self.partner_id:
            domain = [('parent_id', '=', self.partner_id.id),('type', '=', 'contact')]
     
            result = { 
                        'domain': {'contact_person': domain} 
                    } 
            return result

class AccountMovePO(models.Model):
    _name = 'account.move.po'

    _sql_constraints = [
        ("unique_po_number",
         "UNIQUE(po_number)",
         "PO Number Already Exist"),
    ]

    account_move_id = fields.Many2one('account.move',string='Account Move ID')
    customer = fields.Many2one('res.partner',string='Customer')
    po_number = fields.Many2one('res.partner.po',required=True,string="PO Number")

    @api.onchange("customer")
    def set_domain_for_po_number(self):
        for rec in self:
            ids_already_in_lists = []
            list_ids = []

            for po_number  in rec.account_move_id.po_number.po_number:
                ids_already_in_lists.append(po_number.id)

            _logger.info("already :" + str(ids_already_in_lists))

            for po_number in rec.customer.po_numbers:
                list_ids.append(po_number.id)

            unique_elements = set(ids_already_in_lists).symmetric_difference(set(list_ids))
            
            _logger.info("already :" + str(list(unique_elements)))

            ids = list(unique_elements)

            domain = [('id', 'in', ids ),('closed_boolean', '=', False)]
        
            result = { 
                            'domain': {'po_number': domain} 
                        }

            # return result 
            return result

        
        # if self.customer:
        #     domain = [('contact_id', '=', self.customer.id),('closed_boolean', '=', False)]
     
        #     result = { 
        #                 'domain': {'po_number': domain} 
        #             } 
        #     return result

class AccountMoveLineInherited(models.Model):
    _inherit = 'account.move.line'

    report_no = fields.Char(string="Report Number")