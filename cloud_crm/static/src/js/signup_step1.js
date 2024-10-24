/** @odoo-module */

import { Component, useState } from "@odoo/owl";
import { xml } from "@odoo/owl";

// Definir el componente de autocompletado de códigos postales
class ZipAutocomplete extends Component {
    setup() {
        this.state = useState({
            zip: '',
            zipOptions: [],
            selectedZip: null,
            city: '',
        });
    }

    async onZipInput(event) {
        const term = event.target.value;
        this.state.zip = term;

        if (term.length >= 2) {
            const results = await this.env.services.rpc({
                model: 'res.city.zip',
                method: 'search_read',
                args: [[['name', 'ilike', term]], ['id', 'name', 'city_id']],
                limit: 10,
            });

            this.state.zipOptions = results;
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

// Montar el componente al cargar el DOM
document.addEventListener('DOMContentLoaded', async () => {
    const target = document.getElementById('signup_step1');
    if (target) {
        owl.mount(ZipAutocomplete, { target });
    }
});

export default ZipAutocomplete;
