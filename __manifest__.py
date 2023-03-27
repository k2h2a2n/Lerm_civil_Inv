{'name':'Kes_Invoicing',
 'summary': "Invoicing",
 'author': "Usman Shaikhnag and Khan Afzal", 
 'website': "http://www.esehat.org", 
 'category': 'Uncategorized', 
 'version': '13.0.1', 
 'depends':['base' , 'contacts','account' , 'web'],
 'data': [
        'views/customer.xml',
        'report/kes_invoice_action.xml',
        'report/kes_invoice_template.xml'
    ],
 'assets': {
        'web.report_assets_common': [
            '/lerm_civil_inv/static/src/css/kes_invoice.scss',
        ],
    }
}
