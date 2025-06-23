# cloud_sas

The `cloud_sas` addon installs security rules to restrict access to developer features and hides itself from regular users.
It also creates a maintenance user (`factuoo`) that administrators can use across customer databases.

### Dependencies
- `base`
- `web`

### Setup
Install this module in the template database that will be cloned for new customers.
The security rules are initially inactive so that administrators can review them before going live.
