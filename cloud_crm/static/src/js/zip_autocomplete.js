// File: zip_autocomplete.js
import { Component, useState } from owl;
import { rpc } from 'web.rpc'; // para llamadas RPC en OWL

class ZipAutocomplete extends Component {
    // Definimos el estado del componente
    constructor() {
        super(...arguments);
        this.state = useState({
            searchTerm: '',
            results: [],
            selectedZip: null,
        });
    }

    // Método para manejar la búsqueda dinámica
    async onSearchInput(ev) {
        const term = ev.target.value;
        this.state.searchTerm = term;

        if (term.length >= 2) {
            // Hacer la llamada RPC para obtener los códigos postales
            const results = await rpc({
                model: 'res.city.zip',
                method: 'search_read',
                args: [[['name', 'ilike', term]], ['id', 'name', 'city_id']],
                limit: 10,
            });
            this.state.results = results;
        } else {
            this.state.results = [];
        }
    }

    // Método para manejar la selección del código postal
    onSelectZip(zip) {
        this.state.selectedZip = zip;
        this.state.results = [];
        this.trigger('zip-selected', { zip });
    }

    // Renderizado del componente OWL
    render() {
        return (
            <div>
                <input
                    type="text"
                    class="form-control"
                    t-on-input="onSearchInput"
                    placeholder="Ingrese el código postal o la ciudad"
                />
                <ul class="autocomplete-results">
                    <t t-foreach="state.results" t-as="zip" t-key="zip.id">
                        <li t-on-click="() => this.onSelectZip(zip)">
                            <t t-esc="zip.name"/> - <t t-esc="zip.city_id[1]"/>
                        </li>
                    </t>
                </ul>
            </div>
        );
    }
}

export default ZipAutocomplete;
