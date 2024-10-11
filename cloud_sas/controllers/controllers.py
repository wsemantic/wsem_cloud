import logging
from odoo.http import request, Response
from odoo import models

_logger = logging.getLogger(__name__)

class CustomIrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    @classmethod
    def _dispatch(cls, endpoint):
        # Log para verificar que estamos entrando en _dispatch
        _logger.info("WSEM Entrando en _dispatch con el usuario: %s", request.env.user.name)

        # Verificar si el parámetro 'debug' está presente en la URL
        if 'debug' in request.httprequest.args:
            _logger.info("WSEM Parámetro 'debug' encontrado en la URL.")
            
            # Verificar si el usuario pertenece al grupo factuadmin
            if not request.env.user.has_group('cloud_sas.factuadmin'):
                _logger.warning("El usuario %s NO tiene permiso para activar el modo debug.", request.env.user.name)
                
                # Desactivar el modo debug
                request.session.debug = ''
                _logger.info("WSEM Modo debug desactivado para el usuario: %s", request.env.user.name)

        # Continuar con el procesamiento original del método
        result = endpoint(**request.params)
        if isinstance(result, Response) and result.is_qweb:
            result.flatten()
        return result

