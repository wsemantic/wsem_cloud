import logging
from odoo import http
from odoo.addons.web.controllers.home import Home
from odoo.http import request, SessionExpiredException
from odoo.exceptions import AccessError

_logger = logging.getLogger(__name__)

class CustomHome(Home):

    @http.route('/odoo', type='http', auth="none", sitemap=False)
    def web_client(self, s_action=None, **kw):
        _logger.info("Accediendo a la ruta /odoo con session uid: %s", request.session.uid)

        # Asegurar que tenemos una base de datos y un usuario
        if not request.session.db:
            return request.redirect('/odoo/database/selector')

        if not request.session.uid:
            return request.redirect('/odoo/login', 303)

        if kw.get('redirect'):
            return request.redirect(kw.get('redirect'), 303)

        # Validar la sesión del usuario
        if not self._validate_session():
            raise SessionExpiredException("Session expired")

        # Verificar si el usuario es interno
        if not self.is_user_internal(request.session.uid):
            return request.redirect('/odoo/login_success', 303)

        # Refrescar el tiempo de vida de la sesión
        request.session.touch()

        # Restaurar el usuario en el entorno
        request.update_env(user=request.session.uid)

        # Implementar la lógica para restringir el modo debug
        if 'debug' in request.httprequest.args:
            _logger.info("Parámetro 'debug' encontrado en la URL.")

            user = request.env.user
            if user.login != 'factuoo':
                _logger.warning("El usuario %s NO tiene permiso para activar el modo debug.", user.login)

                # Desactivar el modo debug
                request.session.debug = ''
                _logger.info("Modo debug desactivado para el usuario: %s", user.login)
            else:
                _logger.info("El usuario %s tiene permiso para activar el modo debug.", user.login)
        else:
            _logger.info("No se encontró el parámetro 'debug' en la URL.")

        # Continuar con el procesamiento estándar
        try:
            context = request.env['ir.http'].webclient_rendering_context()
            response = request.render('web.webclient_bootstrap', qcontext=context)
            response.headers['X-Frame-Options'] = 'DENY'
            return response
        except AccessError:
            return request.redirect('/odoo/login?error=access')

    def is_user_internal(self, uid):
        """Determina si un usuario es interno (no es usuario portal ni público)"""
        user = request.env['res.users'].sudo().browse(uid)
        return not user._is_public() and not user.share

    def _validate_session(self):
        """Valida la sesión del usuario."""
        user = request.env['res.users'].sudo().browse(request.session.uid)
        return user.exists() and user.active
