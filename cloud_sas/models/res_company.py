# -*- coding: utf-8 -*-
from odoo import _, api, models
from odoo.exceptions import AccessError


class ResCompany(models.Model):
    _inherit = "res.company"

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.is_superuser():
            raise AccessError(
                _("No esta permitida la creacion multiempresa en este plan")
            )
        return super().create(vals_list)

    def unlink(self):
        if not self.env.is_superuser():
            raise AccessError(
                _("No esta permitida la eliminación multiempresa en este plan")
            )
        return super().unlink()
