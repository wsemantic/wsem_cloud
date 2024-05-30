from odoo import models, fields, api
import xmlrpc.client

class ResUsersInherit(models.Model):
    _inherit = 'res.users'

    price = fields.Selection([
        ('community', 'Community'),
        ('standard', 'Standard'),
        ('custom', 'Custom')
    ], string='price')

    @api.model
    def create(self, vals):
        user = super(ResUsersInherit, self).create(vals)

        url = 'http://192.168.1.76:8069'
        db = 'wsem_verifactu_cloud'
        password = 'Admin'
        uid = 2
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
        
        partner_id = models.execute_kw(db, uid, password, 'res.partner', 'create', [{
            'name': vals.get('name', ''),  
            'email': vals.get('email', ''),  
        }])

        user.partner_id = partner_id

        return user