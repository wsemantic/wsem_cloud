# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ContractContractInherit(models.Model):
    _inherit = 'contract.contract'

    partner_bank_id = fields.Many2one(
        'res.partner.bank',
        string='Bank account (IBAN)',
        domain="[('partner_id', '=', partner_id)]"
    )

    def _default_partner_bank_id(self):
        for contract in self:
            if contract.partner_id:
                bank = self.env['res.partner.bank'].search([
                    ('partner_id', '=', contract.partner_id.id),
                    ('acc_type', '=', 'iban')
                ], limit=1)
                contract.partner_bank_id = bank.id if bank else False

    @api.onchange('partner_id')
    def _onchange_partner_id_set_bank(self):
        self._default_partner_bank_id()
