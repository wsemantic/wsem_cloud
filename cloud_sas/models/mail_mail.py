from odoo import models, api


FACTUOO_DOMAIN = "factuoo.com"
FACTUOO_IDENTITY = "registro@factuoo.com"


class MailMail(models.Model):
    _inherit = "mail.mail"

    @api.model_create_multi
    def create(self, vals_list):
        mails = super().create(vals_list)
        mails._cloud_sas_force_factuoo_identity()
        return mails

    def write(self, vals):
        if self.env.context.get("cloud_sas_skip_force_factuoo_identity"):
            return super().write(vals)

        res = super().write(vals)
        self._cloud_sas_force_factuoo_identity()
        return res

    def _cloud_sas_force_factuoo_identity(self):
        if not self:
            return

        if not self._cloud_sas_should_force_identity():
            return

        # At this point any dynamic email_from expression from templates has
        # already been evaluated because we run after the base create/write
        # logic stores the final message values.
        factuoo_identity = FACTUOO_IDENTITY
        lower_identity = factuoo_identity.lower()

        for mail in self:
            updates = {}

            sender = (mail.email_from or "").strip()
            if sender.lower() != lower_identity:
                updates["email_from"] = factuoo_identity

                if not (mail.reply_to or "").strip():
                    reply_to = self._cloud_sas_get_reply_to(mail)
                    if reply_to:
                        updates["reply_to"] = reply_to

            if updates:
                mail.with_context(cloud_sas_skip_force_factuoo_identity=True).write(updates)

    @api.model
    def _cloud_sas_should_force_identity(self):
        if self.env.context.get("cloud_sas_skip_force_factuoo_identity"):
            return False

        servers = self.env["ir.mail_server"].sudo().search([
            ("active", "=", True),
            ("from_filter", "!=", False),
        ])
        return any(
            (server.from_filter or "").strip().lower() == FACTUOO_DOMAIN
            for server in servers
        )

    @staticmethod
    def _cloud_sas_get_reply_to(mail):
        author = mail.author_id
        if author:
            reply_to = author.email_formatted or author.email
            if reply_to:
                return reply_to

        creator_partner = mail.create_uid.partner_id if mail.create_uid else False
        if creator_partner:
            reply_to = creator_partner.email_formatted or creator_partner.email
            if reply_to:
                return reply_to

        return False
