/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { xml } from "@odoo/owl";

// Definir y exportar la clase del componente OWL
export class ZipAutocomplete extends Component {
    setup() {
        this.state = useState({
            zip: '',
            zipOptions: [],
            selectedZip: null,
            city: '',
        });
    }

    // Método para manejar la entrada del código postal
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

    // Método para manejar la selección de un código postal
    onSelectZip(zip) {
        this.state.selectedZip = zip;
        this.state.zipOptions = [];
        this.state.city = zip.city_id[1];
        // Disparar el evento para QWeb
        this.trigger('zip-selected', { zip: zip });
    }
}

// Asignación directa del template heredado
// Asignar el template OWL desde el archivo XML
ZipAutocomplete.template = 'signup_step1_template';
