/** @odoo-module **/

import { Component } from "@odoo/owl";
import { useState } from "@odoo/owl";
import { registry } from "@web/core/registry";

export class SignupStep1 extends Component {
    static template = 'cloud_crm.signup_step1_template';
    
    setup() {
        this.state = useState({
            zip: '',
            zipOptions: [],
            selectedZip: null,
            city: '',
        });
    }

    async onZipInput(ev) {
        const term = ev.target.value;
        this.state.zip = term;

        if (term.length >= 2) {
            try {
                const response = await this.env.services.rpc(
                    '/web/dataset/call_kw/res.city.zip/search_read',
                    {
                        model: 'res.city.zip',
                        method: 'search_read',
                        args: [],
                        kwargs: {
                            domain: [['name', 'ilike', term]],
                            fields: ['id', 'name', 'city_id'],
                            limit: 10,
                        },
                    }
                );
                this.state.zipOptions = response;
            } catch (error) {
                console.error('Error fetching zip codes:', error);
                this.state.zipOptions = [];
            }
        } else {
            this.state.zipOptions = [];
        }
    }

    onSelectZip(zip) {
        this.state.selectedZip = zip;
        this.state.zipOptions = [];
        this.state.city = zip.city_id[1];
    }
}

registry.category("public_components").add("SignupStep1", SignupStep1);