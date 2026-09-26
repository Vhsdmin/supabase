# EasyPanel: Supabase for Deskcomm

This fork adds a standalone `docker-compose.easypanel.yml`. It keeps the upstream
services and configuration files, removes global container names and published
host ports, and preserves the Realtime gateway alias. PostgreSQL data, Storage
files and Studio snippets use named volumes. Deploy this Compose before Deskcomm.

## Panel source

| Field | Value |
| --- | --- |
| Repository | `https://github.com/Vhsdmin/supabase` |
| Branch | `easypanel` |
| Build Path | `/docker` |
| Docker Compose File | `docker-compose.easypanel.yml` |

Do not select the upstream tag: tags do not include the changes on this branch.
Use the full Git source: the YAML references files under `volumes/`.

## Environment

For a new installation, download/clone this branch and run from `docker/`:

```bash
python3 generate-easypanel-env.py
```

On Windows: `py generate-easypanel-env.py`. The script writes a private `.env`
without printing credentials. Copy its contents to EasyPanel **Environment**,
replace the old sample environment, and enable **Create .env file**.
Do not commit `.env`. Keep the generated file: the Deskcomm environment generator
reuses its keys, database password and URLs. Never regenerate it for an existing DB.

The template uses the two hostnames from the installation configuration:

- Supabase: `https://crmvendepay-supabase.f8zify.easypanel.host`
- CRM: `https://crmvendepay-app.f8zify.easypanel.host`

If these change, update `SUPABASE_PUBLIC_URL`, `API_EXTERNAL_URL`, `SITE_URL` and
`ADDITIONAL_REDIRECT_URLS`. Configure the SMTP fields before relying on invitations
or password recovery. Public signups and phone signups are disabled; Deskcomm
creates its initial administrator through the administrative Auth API.

## Domain and private network

Edit the Supabase domain in EasyPanel: **internal service `api-gw`, port `8000`,
internal protocol HTTP, public HTTPS enabled**. Studio uses `DASHBOARD_USERNAME`
and `DASHBOARD_PASSWORD` from `.env`. Do not publish Studio directly or put another
Basic Auth layer over the entire API domain.

The Compose creates the bridge `crmvendepay_backend`. Only the gateway and DB
join it, as `supabase-envoy` and `supabase-db`. The Deskcomm Compose consumes that
existing network. The rest of Supabase stays on its own default network.
`SINGLE_SERVER_NETWORK` must match in both environments; use a different value
for a second independent installation. Both stacks must run on the same Docker
host. A standalone EasyPanel App/Swarm service is not this Compose topology.

No service publishes 80, 443, 5432, 6543 or 8000 on the host. EasyPanel Domains
owns HTTP routing. Supabase must remain deployed while Deskcomm uses its network.

## Scope and data

This is a NEW-installation path, not a migration of existing volumes. Previously
created bind-mounted data is not imported into the new named volumes. Preserve
backups before changing a running installation. Do not delete the service or
volumes to troubleshoot. Redeploy preserves the volumes as long as the Compose
project/service identity stays the same.

Deskcomm setup instructions:
https://github.com/Vhsdmin/DeskcommCRM/blob/easypanel/EASYPANEL.md

Validation: Compose configuration and local file references can be checked with
`docker compose -f docker-compose.easypanel.yml --env-file .env config --quiet`.
A successful config check does not prove container startup or application login.
