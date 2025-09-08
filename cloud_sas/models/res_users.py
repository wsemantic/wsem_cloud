from odoo import models, api, _

class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model_create_multi
    def create(self, vals_list):
        users = super(ResUsers, self).create(vals_list)
        # Verificar si el usuario tiene permisos de contabilidad
        for user in users:
            self._assign_accounting_technical_group(user)
        return users

    def write(self, vals):
        res = super(ResUsers, self).write(vals)
        # Si se actualizan los grupos del usuario, verificar permisos
        if 'groups_id' in vals:
            for user in self:
                self._assign_accounting_technical_group(user)
        return res

    def _assign_accounting_technical_group(self, user):
        """
        Verifica si el usuario tiene permisos de administración de contabilidad
        y lo añade al grupo técnico correspondiente.
        """
        # Referencia al grupo de contabilidad de administración
        admin_accounting_group = self.env.ref('account.group_account_manager')
        technical_accounting_group = self.env.ref('account.group_account_user')

        # Verificar si el usuario tiene permisos de administración de contabilidad
        if admin_accounting_group in user.groups_id:
            if technical_accounting_group not in user.groups_id:
                user.write({'groups_id': [(4, technical_accounting_group.id)]})
