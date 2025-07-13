/** @odoo-module **/
import { registry } from "@web/core/registry";
import { browser } from "@web/core/browser/browser";

registry.category("user_menuitems").add("documentation", (env) => {
    return {
        type: "item",
        id: "documentation",
        description: "Documentation",
        href: "https://verifact.wsemantic.com/documentacion", 
        callback: () => {
            browser.open("https://verifact.wsemantic.com/documentacion", "_blank");
        },
        sequence: 10,
    };
}, { force: true });

registry.category("user_menuitems").add("support", (env) => {
    return {
        type: "item",
        id: "support",
        description: "Support",
        href: "https://verifact.wsemantic.com/support", 
        callback: () => {
            browser.open("https://verifact.wsemantic.com/support", "_blank");
        },
        sequence: 20,
    };
}, { force: true });

registry.category("user_menuitems").add("odoo_account", (env) => {
    return {
        type: "item",
        id: "account",
        description: "Mi suscripción",
        href: "https://verifact.wsemantic.com/my", 
        callback: () => {
            browser.open("https://verifact.wsemantic.com/my", "_blank");
        },
        sequence: 60,
    };
}, { force: true });

