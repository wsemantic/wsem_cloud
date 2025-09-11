from odoo import http
from odoo.http import request
import time, json, base64, hmac, hashlib
from werkzeug.utils import redirect
SECRET_KEY = "e97b8f1debf497b4c3b67ac469b0d79fa1f47cc6d6f75c1467c2b637109a94e2" 

class SSORedirectController(http.Controller):

    def generate_token(self, login, expiration=300):
        data = {
            'login': login,
            'exp': time.time() + expiration,
        }
        payload = base64.urlsafe_b64encode(json.dumps(data).encode()).decode()
        signature = hmac.new(SECRET_KEY.encode(), payload.encode(), hashlib.sha256).hexdigest()
        return f"{payload}.{signature}"

    @http.route(["/sso/redirect", "/sso/redirect/<path:redirect_path>"], auth="user")
    def sso_redirect(self, redirect=None, redirect_path=None, **kw):
        login = request.env.user.login
        token = self.generate_token(login)
        target = redirect or redirect_path or "my"
        target_url = (
            f"https://crm.factuoo.com/auth/sso_login/{target.lstrip('/')}?token={token}"
        )
        return redirect(target_url)
