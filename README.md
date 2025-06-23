# WSEM Cloud Addons

This repository contains two custom Odoo addons for managing customer signup and security:

- **cloud_crm**: Implements a multi-step signup wizard for new customers. It relies on standard QWeb templates, though an OWL template is included as an optional alternative for zip-code autocomplete.
- **cloud_sas**: Provides access control utilities used by the signup process.

Both addons were originally written for Odoo 16 and updated here to target Odoo 18. They have been tested on Ubuntu 24.

## Requirements

Install the Python dependencies using `pip`:

```bash
pip install -r requirements.txt
```

## Installation

1. Copy both folders into your Odoo addons path.
2. Update the app list and install the `cloud_crm` module. The required dependencies are `sale`, `l10n_es_toponyms` and `contract`.
3. Install Python dependencies with `pip install -r requirements.txt`.

The signup workflow starts at `/signup_step1` and guides users through database creation and module selection.
After the first step, users continue to `/signup_step2` to choose optional modules.

OWL components are optional; the standard QWeb forms work on Odoo 18 without OWL.
## Template Database

Prepare a template database named `veri-template` containing the `cloud_sas` module and a maintenance user with ID `2` (login `factuoo`). New customer databases are cloned from this template and the security rules can be activated when ready.

