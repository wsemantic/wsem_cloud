from odoo import models, fields


class ContractContract(models.Model):
    _inherit = 'contract.contract'

    iban = fields.Char(string='IBAN')
