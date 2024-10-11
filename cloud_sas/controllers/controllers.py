from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class CustomDebugController(http.Controller):

    @http.route('/web', type='http', auth="user", website=True)
    def check_debug_mode(self, **kw):
        # Log para verificar que se ha accedido a la ruta /web
        _logger.info("WSEM - Accediendo a la ruta /web con el usuario: %s", request.env.user.name)

        # Verificar si el parámetro "debug" está presente en la URL
        if 'debug' in request.httprequest.args:
            _logger.info("WSEM - Parámetro 'debug' encontrado en la URL.")
            
            # Verificar si el usuario pertenece al grupo factuadmin
            if not request.env.user.has_group('cloud_sas.factuadmin'):
                _logger.warning("WSEM - El usuario %s NO tiene permiso para activar el modo debug.", request.env.user.name)
                
                # Desactivar el modo debug
                request.session.debug = ''
                _logger.info("WSEM - Modo debug desactivado para el usuario: %s", request.env.user.name)
            else:
                _logger.info("WSEM - El usuario %s tiene permiso para activar el modo debug.", request.env.user.name)
        else:
            _logger.info("WSEM - No se encontró el parámetro 'debug' en la URL.")

        # Llamar al método original para continuar con el procesamiento estándar
        return request.render('web.webclient_bootstrap')
