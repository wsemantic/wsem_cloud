const { Component, useState } = owl;
const { xml } = owl.tags;

// Definir el componente
class ZipAutocomplete extends Component {
    // Configurar el estado del componente
    setup() {
        this.state = useState({
            zip: '',
            zipOptions: [],
            selectedZip: null,
            city: '',
        });
    }

    // Manejar el input del código postal y hacer una búsqueda RPC
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

    // Manejar la selección del código postal
    onSelectZip(zip) {
        this.state.selectedZip = zip;
        this.state.zipOptions = [];
        this.state.city = zip.city_id[1];
    }

    // Definir el template del componente
    static template = xml`
        <div>
            <input
                type="text"
                class="form-control"
                t-on-input="onZipInput"
                placeholder="Ingrese el código postal"
                t-model="state.zip"
            />
            <ul class="autocomplete-results">
                <t t-foreach="state.zipOptions" t-as="zip" t-key="zip.id">
                    <li t-on-click="() => this.onSelectZip(zip)">
                        <t t-esc="zip.name"/> - <t t-esc="zip.city_id[1]"/>
                    </li>
                </t>
            </ul>
            <input
                type="text"
                class="form-control"
                placeholder="Población"
                t-model="state.city"
            />
        </div>
    `;
}

// Montar el componente cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    const target = document.getElementById('signup_step1');
    if (target) {
        owl.mount(ZipAutocomplete, { target });
    }
});
