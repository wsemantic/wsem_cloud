/** @odoo-module **/
import { registry } from "@web/core/registry";
import { browser } from "@web/core/browser/browser";
import { session } from "@web/session";
console.log(session.user_id)
registry.category("user_menuitems").add("documentation", (env) => {
    return {
        type: "item",
        id: "documentation",
        description: "Documentation",
        href: "https://www.factuoo.com/documentacion", 
        callback: () => {
            browser.open("https://www.factuoo.com/documentacion", "_blank");
        },
        sequence: 10,
    };
}, { force: true });

registry.category("user_menuitems").add("support", (env) => {
    return {
        type: "item",
        id: "support",
        description: "Support",
        href: "/sso/redirect?redirect=/my/tickets",
        callback: () => {
            browser.open("/sso/redirect?redirect=/my/tickets", "_blank");
        },
        sequence: 20,
    };
}, { force: true });

registry.category("user_menuitems").add("odoo_account", (env) => {
    return {
        type: "item",
        id: "account",
        description: "Mi suscripción",
        href: "/sso/redirect",
        callback: () => {
            browser.open("/sso/redirect", "_blank");
        },
        sequence: 60,
    };
}, { force: true });
