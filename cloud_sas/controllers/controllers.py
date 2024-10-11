import logging
from odoo.http import request
from odoo.addons.web.controllers.main import Home
from odoo import http

# Crear un logger para el módulo
_logger = logging.getLogger(__name__)

class CustomHome(Home):

    @http.route('/web', type='http', auth="user", website=True)
    def web_client(self, s_action=None, **kw):
        # Log para verificar si se ha accedido a la ruta /web
        _logger.info("WSEM Accediendo a la ruta /web con el usuario: %s", request.env.user.name)
        
        # Verificar si el parámetro "debug" está presente en la URL
        if 'debug' in request.httprequest.args:
            _logger.info("WSEM Parámetro 'debug' encontrado en la URL.")
            
            # Verificar si el usuario tiene permisos para entrar en modo debug
            if not request.env.user.has_group('cloud_sas.factuadmin'):
                _logger.warning("El usuario %s NO tiene permiso para activar el modo debug.", request.env.user.name)
                
                # Desactivar el modo debug
                request.session.debug = ''
                _logger.info("WSEM Modo debug desactivado para el usuario: %s", request.env.user.name)
            else:
                _logger.info("WSEM El usuario %s tiene permiso para activar el modo debug.", request.env.user.name)
        else:
            _logger.info("WSEM No se encontró el parámetro 'debug' en la URL.")
        
        # Llamar al método original de Home para continuar con el procesamiento estándar
        _logger.info("Continuando con el procesamiento estándar del método 'web_client'.")
        return super(CustomHome, self).web_client(s_action=s_action, **kw)
