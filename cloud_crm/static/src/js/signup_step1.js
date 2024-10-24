/** @odoo-module */

import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

class SignupStep1 extends Component {
    setup() {
        super.setup();
        this.state = useState({
            zip: '',
            zipOptions: [],
            selectedZip: null,
            city: '',
        });
        
        this.orm = useService("orm");
    }

    async onZipInput(event) {
        const term = event.target.value;
        this.state.zip = term;

        if (term.length >= 2) {
            try {
                const results = await this.orm.searchRead(
                    'res.city.zip',
                    [['name', 'ilike', term]],
                    ['id', 'name', 'city_id'],
                    { limit: 10 }
                );
                this.state.zipOptions = results;
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

    static template = 'cloud_crm.signup_step1_template';
}

registry.category("public_components").add("SignupStep1", SignupStep1);

export default SignupStep1;