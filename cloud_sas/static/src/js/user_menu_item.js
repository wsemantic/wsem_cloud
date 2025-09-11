/** @odoo-module **/
import { registry } from "@web/core/registry";
import { browser } from "@web/core/browser/browser";

registry.category("user_menuitems").add(
    "documentation",
    () => ({
        type: "item",
        id: "documentation",
        description: "Documentation",
        href: "https://www.factuoo.com/documentacion",
        callback: () => {
            browser.open("https://www.factuoo.com/documentacion", "_blank");
        },
        sequence: 10,
    }),
    { force: true }
);

registry.category("user_menuitems").add(
    "support",
    () => ({
        type: "item",
        id: "support",
        description: "Soporte",
        href: "/sso/redirect/my/tickets",
        callback: () => {
            browser.open("/sso/redirect/my/tickets", "_blank");
        },
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
        callback: () => {
            browser.open("/sso/redirect", "_blank");
        },
        sequence: 60,
    }),
    { force: true }
);
