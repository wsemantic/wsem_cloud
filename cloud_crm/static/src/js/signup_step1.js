/** @odoo-module */

import { Component, useState } from "@odoo/owl";
import { xml } from "@odoo/owl";
import { loadTemplate } from 'web.utils'; // Asegurarte de que esté disponible

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

    // Cargar y asignar el template desde el XML
    static async willStart() {
        const template = await loadTemplate("/cloud_crm/views/owl_step1_template.xml");
        this.template = template;
    }
}

// Registrar el componente OWL en el sistema de módulos de Odoo
owl.component.ZipAutocomplete = ZipAutocomplete;
