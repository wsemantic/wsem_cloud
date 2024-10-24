odoo.define('cloud_crm.zip_autocomplete', function (require) {
    "use strict";

    var rpc = require('web.rpc');
    var Component = require('owl.Component');
    var useState = require('owl.hooks').useState;

    class ZipAutocomplete extends Component {
        constructor() {
            super(...arguments);
            this.state = useState({
                searchTerm: '',
                results: [],
                selectedZip: null,
            });
        }

        async onSearchInput(ev) {
            const term = ev.target.value;
            this.state.searchTerm = term;

            if (term.length >= 2) {
                const results = await rpc.query({
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

        onSelectZip(zip) {
            this.state.selectedZip = zip;
            this.state.results = [];
            this.trigger('zip-selected', { zip });
        }

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

    return ZipAutocomplete;
});
