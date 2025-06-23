# cloud_crm

`cloud_crm` implements a two-step signup wizard that allows new customers to register a database in the WSEM cloud.
The wizard is based on standard QWeb templates and optionally provides an OWL component for zip code autocomplete.

### Dependencies
- `sale`
- `l10n_es_toponyms`
- `contract`

### Setup
Copy the module into your Odoo addons path and install it from the Apps menu. The addon expects the `cloud_sas` module to be present in the template database used for new signups.
