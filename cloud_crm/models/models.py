from odoo import models, fields
import logging

_logger = logging.getLogger(__name__)

#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100


class AuthSignupHome(models.Model):
    _inherit = 'auth.signup.home'
        

    def _prepare_signup_values(self, qcontext):
        _logger.info(f"WSEM Entrado en prepare {product.display_name}")
        # Primero, obtener los valores originales llamando al método de la superclase
        values = super(AuthSignupHome, self)._prepare_signup_values(qcontext)

        # Ahora, añadir o modificar valores como sea necesario
        if 'price' in qcontext:
            values['price'] = qcontext.get('price')

        return values

        