#!/bin/sh
set -eu

# Generate a self-signed certificate for development (CN=localhost)
OUT_DIR="./nginx/certs"
mkdir -p "$OUT_DIR"

openssl req -x509 -nodes -days 365 \
  -newkey rsa:2048 \
  -keyout "$OUT_DIR/dev.key" \
  -out "$OUT_DIR/dev.crt" \
  -subj "/C=US/ST=State/L=City/O=Dev/OU=Dev/CN=localhost"

echo "Created $OUT_DIR/dev.crt and $OUT_DIR/dev.key"
