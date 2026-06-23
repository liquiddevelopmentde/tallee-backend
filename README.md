# Tallee Backend

A simple, short-lived relay service for sharing tallee match data between devices. An app can upload a match and get back a 6-character code. Other devices can use this code to download the match data. Data is automatically deleted after 10 minutes.
## Local Development

To run the server on your local machine, you'll need `Docker and `mkcert`.

**1. First-Time Setup: Create a local SSL certificate**

This is required for the mobile apps to connect to your local server over HTTPS.

First, install `mkcert` if you don't have it. On macOS with [Homebrew](https://brew.sh/):
```sh
brew install mkcert
```
For other platforms, see the [mkcert installation guide](https://github.com/FiloSottile/mkcert#installation).

Once `mkcert` is installed, you can create the local certificate:
```sh
# Create and install a local Certificate Authority in your system's trust stores
mkcert -install

# Generate the certificate files in the project root
mkcert -cert-file dev-cert.pem -key-file dev-key.pem "localhost" "127.0.0.1" "::1"
```
These `.pem` files are listed in `.gitignore` and will not be committed.

**2. Run the Server**

```sh
docker-compose up
```

The API will be running at `https://localhost:8000`. API documentation is available at `https://localhost:8000/docs`.

---

## Production Deployment

The production environment uses a separate compose file and runs behind a reverse proxy (like Nginx, Caddy, or Traefik) that handles SSL.

On your server, run the following command:
```sh
docker-compose -f docker-compose.prod.yml up --build -d
```

The `docker-compose.prod.yml` file runs the app without SSL, as it expects the reverse proxy to terminate the TLS connection.

---

## API Endpoints

| Method | Path                  | Description                                      |
|--------|-----------------------|--------------------------------------------------|
| POST   | `/v1/shares`          | Upload match data and receive a token.           |
| GET    | `/v1/shares/{token}`  | Fetch match data using a token.                  |
| DELETE | `/v1/shares/{token}`  | Immediately delete a shared match.               |
| GET    | `/health`             | Health check endpoint.                           |

---

## Testing

To run the test suite:
```sh
pytest
```