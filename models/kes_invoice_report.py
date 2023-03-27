from odoo import models , fields,api


class KesCustomInvoiceReport(models.AbstractModel):
    _name = 'report.lerm_civil_inv.kes_custom_invoice'
    _description = 'Kes Custom Invoice Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs1 = self.env['account.move'].sudo().browse(docids)
        print(docs1 , 'afzal khan ')
        return {
              'doc_ids': docids,
              'doc_model': 'account.move',
              'data': docs1,
        }
