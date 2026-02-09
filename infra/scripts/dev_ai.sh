#!/usr/bin/env bash
set -e
ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT_DIR/apps/ai-service"

source .venv/bin/activate
exec uvicorn app.main:app --reload --port 8001
