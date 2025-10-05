# -*- coding: utf-8 -*-
from odoo import _, api, models
from odoo.exceptions import AccessError


class ResCompany(models.Model):
    _inherit = "res.company"

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.is_superuser():
            raise AccessError(
                _("Creating companies is disabled because the database is configured for a single company.")
            )
        return super().create(vals_list)

    def unlink(self):
        if not self.env.is_superuser():
            raise AccessError(
                _("Deleting companies is disabled because the database is configured for a single company.")
            )
        return super().unlink()
