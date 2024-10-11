import logging
from odoo import http
from odoo.addons.web.controllers.home import Home
from odoo.http import request, SessionExpiredException
from odoo.exceptions import AccessError

_logger = logging.getLogger(__name__)

class CustomHome(Home):

    @http.route('/web', type='http', auth="none", sitemap=False)
    def web_client(self, s_action=None, **kw):
        _logger.info("WSEM - Accediendo a la ruta /web con session uid: %s", request.session.uid)

        # Asegurar que tenemos una base de datos y un usuario
        if not request.session.db:
            return request.redirect('/web/database/selector')

        if not request.session.uid:
            return request.redirect('/web/login', 303)

        if kw.get('redirect'):
            return request.redirect(kw.get('redirect'), 303)

        # Verificar si la sesión es válida
        if not self._validate_session():
            raise SessionExpiredException("Session expired")

        if not self.is_user_internal(request.session.uid):
            return request.redirect('/web/login_successful', 303)

        # Refrescar el tiempo de vida de la sesión
        request.session.touch()

        # Restaurar el usuario en el entorno, ya que se perdió debido a auth="none"
        request.update_env(user=request.session.uid)

        # Aquí, tenemos una sesión de usuario válida
        # Implementar la lógica personalizada para restringir el modo debug
        if 'debug' in request.httprequest.args:
            _logger.info("WSEM - Parámetro 'debug' encontrado en la URL.")

            user = request.env.user
            if not user.has_group('cloud_sas.factuadmin'):
                _logger.warning("WSEM - El usuario %s NO tiene permiso para activar el modo debug.", user.name)

                # Desactivar el modo debug
                request.session.debug = ''
                _logger.info("WSEM - Modo debug desactivado para el usuario: %s", user.name)
            else:
                _logger.info("WSEM - El usuario %s tiene permiso para activar el modo debug.", user.name)
        else:
            _logger.info("WSEM - No se encontró el parámetro 'debug' en la URL.")

        # Continuar con el procesamiento estándar
        try:
            context = request.env['ir.http'].webclient_rendering_context()
            response = request.render('web.webclient_bootstrap', qcontext=context)
            response.headers['X-Frame-Options'] = 'DENY'
            return response
        except AccessError:
            return request.redirect('/web/login?error=access')

    def is_user_internal(self, uid):
        """Determina si un usuario es interno (no es usuario portal ni público)"""
        user = request.env['res.users'].sudo().browse(uid)
        return not user._is_public() and not user.share

    def _validate_session(self):
        """Valida la sesión del usuario."""
        # En Odoo 16, podemos validar la sesión comprobando si el usuario está activo
        user = request.env['res.users'].sudo().browse(request.session.uid)
        return user.exists() and user.active
