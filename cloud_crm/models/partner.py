from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    cloud_url = fields.Char(string='Cloud URL')