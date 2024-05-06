from odoo import fields, models

class ResUsersInherit(models.Model):
    _inherit = 'res.users'

    price = fields.Selection([
        ('community', 'Community'),
        ('standard', 'Standard'),
        ('custom', 'Custom')
    ], string='Price')
