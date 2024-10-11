import logging
from odoo import http
from odoo.addons.web.controllers.home import Home
from odoo.http import request
from odoo.exceptions import AccessError, SessionExpiredException
from odoo.addons.web.controllers.main import ensure_db, is_user_internal, security

_logger = logging.getLogger(__name__)

class CustomHome(Home):

    @http.route('/web', type='http', auth="none", sitemap=False)
    def web_client(self, s_action=None, **kw):
        _logger.info("WSEM - Accediendo a la ruta /web con session uid: %s", request.session.uid)

        # Asegurar que tenemos una base de datos y un usuario
        ensure_db()
        if not request.session.uid:
            return request.redirect('/web/login', 303)
        if kw.get('redirect'):
            return request.redirect(kw.get('redirect'), 303)
        if not security.check_session(request.session, request.env):
            raise SessionExpiredException("Session expired")
        if not is_user_internal(request.session.uid):
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
