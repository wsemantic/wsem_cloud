from odoo import models, fields

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
