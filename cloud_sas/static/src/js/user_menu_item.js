/** @odoo-module **/
import { registry } from "@web/core/registry";

registry.category("user_menuitems").add(
    "documentation",
    () => ({
        type: "item",
        id: "documentation",
        description: "Documentation",
        href: "https://www.factuoo.com/documentacion",
        sequence: 10,
    }),
    { force: true }
);

registry.category("user_menuitems").add(
    "support",
    () => ({
        type: "item",
        id: "support",
        description: "Mis solicitudes asistencia",
        href: "/sso/redirect/my/tickets",
        sequence: 20,
    }),
    { force: true }
);

registry.category("user_menuitems").add(
    "odoo_account",
    () => ({
        type: "item",
        id: "odoo_account",
        description: "Mi suscripción",
        href: "/sso/redirect",
        sequence: 60,
    }),
    { force: true }
);
