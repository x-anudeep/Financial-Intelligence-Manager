#!/usr/bin/env bash
set -euo pipefail

if [ "${USE_POSTGRES:-0}" = "1" ]; then
  docker compose -f docker-compose.yml -f docker-compose.postgres.yml up --build
else
  docker compose up --build
fi
