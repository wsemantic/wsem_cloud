import logging
from odoo import http
from odoo.addons.web.controllers.main import Home
from odoo.http import request

_logger = logging.getLogger(__name__)

class CustomHome(Home):

    @http.route('/web', type='http', auth="user", website=True)
    def web_client(self, s_action=None, **kw):
        # Log para verificar acceso a /web
        _logger.info("WSEM - Accediendo a la ruta /web con el usuario: %s", request.env.user.name)

        # Verificar si el parámetro "debug" está presente en la URL
        if 'debug' in request.httprequest.args:
            _logger.info("WSEM - Parámetro 'debug' encontrado en la URL.")

            # Verificar si el usuario pertenece al grupo 'factuadmin'
            if not request.env.user.has_group('cloud_sas.factuadmin'):
                _logger.warning("WSEM - El usuario %s NO tiene permiso para activar el modo debug.", request.env.user.name)

                # Desactivar el modo debug
                request.session.debug = ''
                _logger.info("WSEM - Modo debug desactivado para el usuario: %s", request.env.user.name)
            else:
                _logger.info("WSEM - El usuario %s tiene permiso para activar el modo debug.", request.env.user.name)
        else:
            _logger.info("WSEM - No se encontró el parámetro 'debug' en la URL.")

        # Continuar con el procesamiento estándar
        return super(CustomHome, self).web_client(s_action=s_action, **kw)

