from odoo import models, fields
from odoo.http import request

class ResPartner(models.Model):
    _inherit = 'res.partner'

    dni = fields.Char(string='DNI')
    phone = fields.Char(string='Phone')
    address = fields.Char(string='Address')
    price = fields.Selection([
        ('community', 'Community'),
        ('standard', 'Standard'),
        ('custom', 'Custom')
    ], string='Plan')


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'
    
    
    @classmethod
    def _handle_debug(cls):
        if 'debug' in request.httprequest.args:
            user = request.env.user
            if not user:
                user_id = request.session.uid
                user = request.env['res.users'].sudo().search([('id', '=', user_id)], limit=1)
            if user.login == 'factuoo':
                return super(IrHttp, cls)._handle_debug()
            request.session.debug = ''