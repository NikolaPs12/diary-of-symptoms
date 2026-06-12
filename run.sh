#!/usr/bin/env sh
set -eu

ENV_FILE="diary-of-symptoms/.env"

if [ ! -f "$ENV_FILE" ]; then
  cp diary-of-symptoms/.env.example "$ENV_FILE"
  echo "Created $ENV_FILE from .env.example. Fill TOKEN/API_AI_KEY if you need bot or AI features."
fi

docker compose --env-file "$ENV_FILE" up --build
