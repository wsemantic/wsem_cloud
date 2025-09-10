from odoo import http
from odoo.http import request
from odoo.exceptions import AccessError, MissingError


class ContractPortal(http.Controller):
    @http.route(
        ['/my/contracts/<int:contract_id>/iban'],
        type='http',
        auth='user',
        website=True,
        methods=['POST']
    )
    def contract_update_iban(self, contract_id, **post):
        iban = post.get('iban')
        try:
            contract = request.env['contract.contract'].sudo().browse(contract_id)
            if not contract.exists():
                raise MissingError
            if contract.partner_id != request.env.user.partner_id:
                raise AccessError
            contract.write({'iban': iban})
        except (AccessError, MissingError):
            return request.redirect('/my')
        return request.redirect('/my/contracts/%s' % contract_id)
