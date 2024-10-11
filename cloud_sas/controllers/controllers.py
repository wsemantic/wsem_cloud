from odoo.addons.web.controllers.main import Home
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class CustomHome(Home):

    @classmethod
    def _dispatch(cls):
        # Log para verificar que estamos entrando en _dispatch
        _logger.info("WSEM Entrando en _dispatch con el usuario: %s", request.env.user.name)

        # Verificar si el parámetro 'debug' está presente
        if 'debug' in request.httprequest.args:
            _logger.info("WSEM Parámetro 'debug' encontrado en la URL.")
            # Verificar si el usuario pertenece al grupo factuadmin
            if not request.env.user.has_group('cloud_sas.factuadmin'):
                _logger.warning("WSEM El usuario %s NO tiene permiso para activar el modo debug.", request.env.user.name)
                request.session.debug = ''
                _logger.info("WSEM Modo debug desactivado para el usuario: %s", request.env.user.name)

        # Continuar con el comportamiento estándar
        return super(CustomHome, cls)._dispatch()

