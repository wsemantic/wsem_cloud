# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
import time, json, base64, hmac, hashlib

SECRET_KEY = "e97b8f1debf497b4c3b67ac469b0d79fa1f47cc6d6f75c1467c2b637109a94e2"  

class SSOLoginController(http.Controller):

    def verify_token(self, token):
        try:
            payload_b64, signature = token.split('.')
            expected_signature = hmac.new(SECRET_KEY.encode(), payload_b64.encode(), hashlib.sha256).hexdigest()
            if not hmac.compare_digest(expected_signature, signature):
                return None
            data = json.loads(base64.urlsafe_b64decode(payload_b64.encode()).decode())
            if time.time() > data['exp']:
                return None
            return data['login']
        except Exception:
            return None

    @http.route(['/auth/sso_login', '/auth/sso_login/<path:redirect_path>'], auth='public', website=True)
    def sso_login(self, token=None, redirect=None, redirect_path=None, **kwargs):
        login = self.verify_token(token)
        if not login:
            return request.redirect("/web/login?error=invalid_token")
        user = request.env['res.users'].sudo().search([('login', '=', login)], limit=1)
        if not user:
            return request.redirect("/web/login?error=user_not_found")

        request.session.uid = user.id
        request.session.session_token = user._compute_session_token(request.session.sid)

        target = redirect or (f"/{redirect_path}" if redirect_path else "/my")
        return request.redirect(target)
