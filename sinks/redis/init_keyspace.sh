#!/usr/bin/env sh
set -eu

REDIS_HOST="${REDIS_HOST:-redis-master.bosgenesis.svc.cluster.local}"
REDIS_PORT="${REDIS_PORT:-6379}"
REDIS_DB="${REDIS_DB:-0}"
REDIS_KEY_PREFIX="${REDIS_KEY_PREFIX:-bg:k8s-ingestion}"
REDIS_CONSUMER_GROUP="${REDIS_CONSUMER_GROUP:-k8s-ingestion-agent}"
INITIALIZED_AT="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

AUTH_ARGS=""
if [ -n "${REDIS_PASSWORD:-}" ]; then
  AUTH_ARGS="-a ${REDIS_PASSWORD}"
fi

if command -v redis-cli >/dev/null 2>&1; then
  redis-cli -h "${REDIS_HOST}" -p "${REDIS_PORT}" -n "${REDIS_DB}" ${AUTH_ARGS} \
    HSET "${REDIS_KEY_PREFIX}:meta" \
    agent "bosgenesis-k8s-data-ingestion-agent" \
    namespace "bosgenesis" \
    owner "bosgenesis" \
    initialized_at "${INITIALIZED_AT}"

  redis-cli -h "${REDIS_HOST}" -p "${REDIS_PORT}" -n "${REDIS_DB}" ${AUTH_ARGS} \
    XGROUP CREATE "${REDIS_KEY_PREFIX}:stream:changes" "${REDIS_CONSUMER_GROUP}" "$" MKSTREAM \
    2>/dev/null || true

  redis-cli -h "${REDIS_HOST}" -p "${REDIS_PORT}" -n "${REDIS_DB}" ${AUTH_ARGS} \
    XGROUP CREATE "${REDIS_KEY_PREFIX}:stream:sink-audit" "${REDIS_CONSUMER_GROUP}" "$" MKSTREAM \
    2>/dev/null || true
elif command -v python3 >/dev/null 2>&1; then
  REDIS_HOST="${REDIS_HOST}" \
  REDIS_PORT="${REDIS_PORT}" \
  REDIS_DB="${REDIS_DB}" \
  REDIS_PASSWORD="${REDIS_PASSWORD:-}" \
  REDIS_KEY_PREFIX="${REDIS_KEY_PREFIX}" \
  REDIS_CONSUMER_GROUP="${REDIS_CONSUMER_GROUP}" \
  INITIALIZED_AT="${INITIALIZED_AT}" \
  python3 "$(dirname "$0")/init_keyspace.py"
else
  echo "Neither redis-cli nor python3 was found. Install one of them and rerun this script." >&2
  exit 127
fi

echo "Initialized Redis keyspace prefix: ${REDIS_KEY_PREFIX}"
