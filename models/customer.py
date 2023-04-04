from odoo import models, fields ,api
import base64
from datetime import datetime , date
import logging
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError


_logger = logging.getLogger(__name__)

class Customer(models.Model):
    _inherit = 'res.partner'

    pan_no = fields.Char(string="PAN No")
    msme_reg_no = fields.Char(string="MSME REG No.")
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
    type = fields.Selection(
        selection = '_compute_res_type',
        string='Address Type',
        default='contact',
        help="Invoice & Delivery addresses are used in sales orders. Private addresses are only visible by authorized users.")


    @api.model
    def _compute_res_type(self):
        selection = [
            ('contact', 'Contact'),
            ('delivery', 'Delivery Address'),
            ('other', 'Other Address'),
            ("private", "Private Address"),
                    ]
        return selection


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
    
    
    invoice_date = fields.Date(string='Invoice/Bill Date',default=datetime.today(), readonly=True, index=True, copy=False,states={'draft': [('readonly', False)]})
    customer_parent = fields.Many2one('res.partner',string="Main Customer")
    project_name = fields.Many2one('res.partner.project',string="Project")
    po_number = fields.One2many('account.move.po','account_move_id',string="PO Number")
    customer_reference = fields.Char(string="Customer Reference")
    contact_person = fields.Many2one('res.partner',string="Contact Person")
    contact_person_ids = fields.Many2many('res.partner',compute='compute_contact_person_ids',string='Partner ID')
    ids_partner = fields.Many2many('res.partner',compute='compute_ids', string='Partner ID')
    project_ids = fields.Many2many('res.partner.project',compute='compute_project_ids', string='Projects ID')
    invoice_to = fields.Many2one('res.partner', inverse="inverse_invoice_to" ,compute='compute_invoice_to',string="Invoice To" )
    signed_by_ids= fields.Many2many('res.partner',compute='compute_signed_by_ids', string='Signed By IDS')
    signed_by = fields.Many2one('res.partner', string='Signed By')


    @api.model_create_multi
    def create(self, vals_list):

        invoice_date = vals_list[0]["invoice_date"]
        invoice_date = datetime.strptime(invoice_date, '%Y-%m-%d').date()
        todays_date = datetime.strptime(str(date.today()), '%Y-%m-%d').date()
        # _logger.info("Value List" + str(invoice_date))

        if invoice_date < todays_date:
            if self.env.user.has_group('lerm_civil_inv.kes_invocing_creation_backdate_group') :
                pass
            else:
                raise UserError('You are Not allowed to create Invoice in Backdate')


        # OVERRIDE
        if any('state' in vals and vals.get('state') == 'posted' for vals in vals_list):
            raise UserError('You cannot create a move already in the posted state. Please create a draft move and post it after.')

        vals_list = self._move_autocomplete_invoice_lines_create(vals_list)
        return super(AccountMoveInherited, self).create(vals_list)
    

    def write(self, vals):
        if vals["invoice_date"]:
            invoice_date = vals["invoice_date"]
            invoice_date = datetime.strptime(invoice_date, '%Y-%m-%d').date()
            todays_date = datetime.strptime(str(date.today()), '%Y-%m-%d').date()

            # _logger.info(invoice_date)
            # _logger.info(todays_date)
            # _logger.info("Value List" + str(invoice_date))

            if invoice_date < todays_date:
                if self.env.user.has_group('lerm_civil_inv.kes_invocing_creation_backdate_group') :
                    pass
                else:
                    raise UserError('You are Not allowed to create Invoice in Backdate')
            _logger.info(vals)
        super(AccountMoveInherited, self).write(vals)

    

    @api.depends("partner_id")
    def compute_signed_by_ids(self):
        for rec in self:
            contact_id = self.env.ref('base.main_partner').id
            signed_by_ids = self.env['res.partner'].search([('parent_id', '=', contact_id),('type','=','contact')])
            rec.signed_by_ids = signed_by_ids


    def action_invoice_sent_mail(self):
        
        invoice_report_id = self.env.ref('lerm_civil_inv.kes_invoice')
        generated_report = invoice_report_id._render_qweb_pdf(self.id)
        data_record = base64.b64encode(generated_report[0])
    
        ir_values = {
            'name': 'Invoice Report',
            'type': 'binary',
            'datas': data_record,
            'store_fname': data_record,
            'mimetype': 'application/pdf',
            'res_model': 'account.move',
            }
        report_attachment = self.env['ir.attachment'].sudo().create(ir_values)
        _logger.info(report_attachment)

        ctx = {
            'default_model': 'account.move',
            'default_res_id': self.ids[0],
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'default_attachment_ids': [report_attachment.id],
            'default_partner_ids': [self.partner_id.id]
        }


        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx
        }



    @api.depends("partner_id")
    def compute_invoice_to(self):
        for rec in self:
            if rec.partner_id:
                rec.invoice_to = rec.partner_id
    
    @api.depends("partner_id")
    def inverse_invoice_to(self):
        for rec in self:
            pass



    @api.depends("partner_id")
    def compute_ids(self):
        for rec in self:
            if rec.partner_id:
                # _logger.info("Parent ID found")
                partners = self.env['res.partner'].search([('parent_id', '=', rec.partner_id.id)])
                rec.ids_partner = partners

            else:
                # _logger.info("Partner ID not found")
                rec.ids_partner = []
       
    

    @api.depends("partner_id")
    def compute_project_ids(self):
        for rec in self:
            if rec.partner_id:
                projects = self.env['res.partner.project'].search([('contact_id', '=', rec.partner_id.id),('closed_boolean','=',False)])
                rec.project_ids = projects
            else:
                rec.project_ids = []

    @api.depends("partner_id")
    def compute_project_ids(self):
        for rec in self:
            if rec.partner_id:
                projects = self.env['res.partner.project'].search([('contact_id', '=', rec.partner_id.id),('closed_boolean','=',False)])
                rec.project_ids = projects
            else:
                rec.project_ids = []
    
    @api.depends("partner_id")
    def compute_contact_person_ids(self):
         for rec in self:
            if rec.partner_id:
                contact_person_ids = self.env['res.partner'].search([('parent_id', '=', rec.partner_id.id),('type','=','contact')])
                rec.contact_person_ids = contact_person_ids
            else:
                rec.contact_person_ids = []

    

    # @api.onchange("partner_id")
    # def set_domain_for_contact_person(self):
    #     if self.partner_id:
    #         domain = [('parent_id', '=', self.partner_id.id),('type', '=', 'contact')]
     
    #         result = { 
    #                     'domain': {'contact_person': domain} 
    #                 } 
    #         return result

class AccountMovePO(models.Model):
    _name = 'account.move.po'


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

            # return reountsult 
            return result

        
        # if self.customer:
        #     domain = [('contact_id', '=', self.customer.id),('closed_boolean', '=', False)]
     
        #     result = { 
        #                 'domain': {'po_number': domain} 
        #             } 
        #     return result

class AccountMoveLineInherited(models.Model):
    _inherit = 'account.move.line'
    report_no = fields.Char('Report No')