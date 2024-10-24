odoo.define('cloud_crm.signup_step1', function (require) {
    "use strict";

    const { Component, useState, mount } = require('web.owl');
    const { rpc } = require('web.rpc');
    const core = require('web.core');  // Necesario para cargar plantillas

    // Cargar el template desde el archivo XML
    const template = core.qweb.templates['cloud_crm.signup_step1_template'];

    class SignupStep1 extends Component {
        constructor() {
            super(...arguments);
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

        onSelectZip(zip) {
            this.state.selectedZip = zip;
            this.state.zipOptions = [];
            this.state.city = zip.city_id[1];
        }

        static template = template;  // Asigna el template desde el XML cargado
    }

    function mountSignupStep1() {
        const target = document.getElementById('signup_step1');
        if (target) {
            mount(SignupStep1, { target });
        }
    }

    document.addEventListener('DOMContentLoaded', mountSignupStep1);
});
