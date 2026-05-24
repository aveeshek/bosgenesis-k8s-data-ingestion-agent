#!/usr/bin/env sh
set -eu

QDRANT_URL="${QDRANT_URL:-http://qdrant.bosgenesis.svc.cluster.local:6333}"
QDRANT_COLLECTION="${QDRANT_COLLECTION:-bosgenesis_k8s_observations}"
VECTOR_SIZE="${VECTOR_SIZE:-1536}"

AUTH_HEADER=""
if [ -n "${QDRANT_API_KEY:-}" ]; then
  AUTH_HEADER="api-key: ${QDRANT_API_KEY}"
fi

TMP_PAYLOAD="$(mktemp)"
sed "s/\"size\": 1536/\"size\": ${VECTOR_SIZE}/" "$(dirname "$0")/collection_payload.json" > "${TMP_PAYLOAD}"

if [ -n "${AUTH_HEADER}" ]; then
  curl -fsS -X PUT "${QDRANT_URL}/collections/${QDRANT_COLLECTION}" \
    -H "Content-Type: application/json" \
    -H "${AUTH_HEADER}" \
    --data-binary "@${TMP_PAYLOAD}"
else
  curl -fsS -X PUT "${QDRANT_URL}/collections/${QDRANT_COLLECTION}" \
    -H "Content-Type: application/json" \
    --data-binary "@${TMP_PAYLOAD}"
fi

rm -f "${TMP_PAYLOAD}"

echo "Initialized Qdrant collection: ${QDRANT_COLLECTION}"

