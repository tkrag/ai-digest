#!/bin/sh
# Seed config to persistent storage if missing or empty
if [ ! -s /storage/config.yaml ]; then
    mkdir -p /storage
    cp /app/config.yaml /storage/config.yaml
fi

exec "$@"
