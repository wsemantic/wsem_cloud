from odoo import models

from .mail_mail import FACTUOO_DOMAIN, FACTUOO_IDENTITY


FACTUOO_SERVER_RESET_FIELDS = {
    name,
    "smtp_host",
    "smtp_port",
    "smtp_user",
    "smtp_pass",
    "from_filter",
}


class IrMailServer(models.Model):
    _inherit = "ir.mail_server"

    def write(self, vals):
        factuoo_servers = self._cloud_sas_filter_factuoo_servers()
        other_servers = self - factuoo_servers

        result = True
        if other_servers:
            result = super(IrMailServer, other_servers).write(vals)

        if factuoo_servers:
            factuoo_vals = factuoo_servers._cloud_sas_prepare_factuoo_vals(vals)
            factuoo_result = super(IrMailServer, factuoo_servers).write(factuoo_vals)
            result = result and factuoo_result

        return result

    def _cloud_sas_prepare_factuoo_vals(self, vals):
        factuoo_vals = vals.copy()
        if not factuoo_vals:
            return factuoo_vals

        reset_required = False

        if "from_filter" in factuoo_vals:
            new_filter = (factuoo_vals["from_filter"] or "").strip().lower()
            if new_filter != FACTUOO_DOMAIN:
                reset_required = True

        if reset_required:
            for field in FACTUOO_SERVER_RESET_FIELDS:
                if field == "from_filter":
                    if field not in factuoo_vals:
                        factuoo_vals[field] = False
                    else:
                        current = (factuoo_vals[field] or "").strip().lower()
                        if current == FACTUOO_DOMAIN:
                            factuoo_vals[field] = False
                else:
                    factuoo_vals.setdefault(field, False)

        return factuoo_vals

    def _cloud_sas_filter_factuoo_servers(self):
        return self.filtered(
            lambda server: (server.from_filter or "").strip().lower() == FACTUOO_DOMAIN
        )
