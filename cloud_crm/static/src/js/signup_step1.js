odoo.define('cloud_crm.signup_step1', function (require) {
    "use strict";

    const { Component, useState, mount } = owl;
    const { xml } = owl.tags;
    const { rpc } = require('web.rpc');

    class SignupStep1 extends Component {
        // Definir el estado inicial
        constructor() {
            super(...arguments);
            this.state = useState({
                zip: '',
                zipOptions: [],
                selectedZip: null,
                city: '',
            });
        }

        // Método para manejar la entrada del código postal y realizar la búsqueda
        async onZipInput(event) {
            const term = event.target.value;
            this.state.zip = term;

            if (term.length >= 2) {
                // Hacer una llamada RPC a Odoo para buscar los códigos postales que coincidan
                const results = await rpc.query({
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

        // Manejar la selección de un código postal
        onSelectZip(zip) {
            this.state.selectedZip = zip;
            this.state.zipOptions = [];
            this.state.city = zip.city_id[1]; // Actualizamos la ciudad basada en el código postal seleccionado
        }

        // Renderizar el componente OWL
        static template = xml`
            <div>
                <!-- Campo de búsqueda de código postal -->
                <input
                    type="text"
                    class="form-control"
                    t-on-input="onZipInput"
                    placeholder="Ingrese el código postal"
                    t-model="state.zip"
                />
                
                <!-- Lista de resultados del autocompletado -->
                <ul class="autocomplete-results">
                    <t t-foreach="state.zipOptions" t-as="zip" t-key="zip.id">
                        <li t-on-click="() => this.onSelectZip(zip)">
                            <t t-esc="zip.name"/> - <t t-esc="zip.city_id[1]"/>
                        </li>
                    </t>
                </ul>
                
                <!-- Campo Población -->
                <input
                    type="text"
                    class="form-control"
                    placeholder="Población"
                    t-model="state.city"
                />
            </div>
        `;
    }

    // Montar el componente OWL en el DOM
    function mountSignupStep1() {
        const target = document.getElementById('signup_step1');
        if (target) {
            mount(SignupStep1, { target });
        }
    }

    // Ejecutar cuando el DOM esté listo
    document.addEventListener('DOMContentLoaded', mountSignupStep1);
});
