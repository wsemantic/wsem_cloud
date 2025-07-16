from odoo import models, fields, api
import xmlrpc.client
import logging

_logger = logging.getLogger(__name__)

class ResUsersInherit(models.Model):
    _inherit = 'res.users'

    price = fields.Selection([
        ('community', 'Community'),
        ('standard', 'Standard'),
        ('custom', 'Custom')
    ], string='Plan')
    
    dni = fields.Char(string='DNI')
    phone = fields.Char(string='phone')
    address = fields.Char(string='Address')

    @api.model_create_multi
    def create(self, vals_list):
        users = super(ResUsersInherit, self).create(vals_list)

        url = 'http://192.168.1.76:8069'
        db = 'wsem_verifactu_cloud'
        password = 'Admin'
        uid = 2
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
        
        for user, vals in zip(users, vals_list):
            partner_id = models.execute_kw(db, uid, password, 'res.partner', 'create', [{
                'name': vals.get('name', ''),  
                'email': vals.get('email', ''),
                'dni': vals.get('dni', ''),  
                'phone': vals.get('phone', ''),
                'address': vals.get('address', ''),  
                'price': vals.get('price', ''),      
            }])

            user.partner_id = partner_id

            _logger.info('Partner created with id: %s', partner_id)
            _logger.info('User created with id: %s', user.id)

        return users
