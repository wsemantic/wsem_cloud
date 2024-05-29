from odoo import models, fields, api
import xmlrpc.client

class ResUsersInherit(models.Model):
    _inherit = 'res.users'

    price = fields.Selection([
        ('community', 'Community'),
        ('standard', 'Standard'),
        ('custom', 'Custom')
    ], string='Price')

    @api.model
    def create(self, vals):
        user = super(ResUsersInherit, self).create(vals)
        
        
        if 'wsem_verifactu_crm' in vals.get('login'):
                 
            url = 'http://192.168.1.76:8069'  
            db = 'wsem_verifactu_crm'  
            username = 'alfongd@gmail.com'  
            password = 'P~7na.G*&6WxuqU'  
            api_key = 'f27b3a499870852a4b21f77b8065a01cbf740f78'  
            
            
            common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
            uid = common.authenticate(db, username, password, {})
            models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
            
            
            partner_id = models.execute_kw(db, uid, password, 'res.partner', 'create', [{
                'name': 'name',  
                'email': 'email',
                
            }])
            
            user.partner_id = partner_id
        
        return user
