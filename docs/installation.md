# Installation Guide
This installation guide is for the Tallee backend service.

We recommend some familiarity with Docker before proceeding.
This guide also assumes you have a working Caddy reverse-proxy already set up.

## Networks
The stack uses two Docker networks:

- **internal**
- **web** (call this whatever you want, but it must match the `external` network name in `docker-compose.yml`)

Create the `web` network before starting:

```bash
docker network create web
```

## Starting

Copy the example environment file and adjust if needed:

```bash
cp .example.env .env
```

Then start the stack:

```bash
docker compose up -d
````


## Override File

To change any setting without modifying `docker-compose.yml`, 
create a `docker-compose.override.yml` file in the same directory. 

This prevents merge conflicts when updating the server later on.
