#!/usr/bin/env bash
set -euo pipefail

APP_NAME="${APP_NAME:-bosgenesis-k8s-data-ingestion-agent}"
IMAGE_REPOSITORY="${IMAGE_REPOSITORY:-bosgenesis-k8s-data-ingestion-agent}"
IMAGE_TAG="${IMAGE_TAG:-0.0.1}"
IMAGE="${IMAGE_REPOSITORY}:${IMAGE_TAG}"
IMAGE_TAR="${IMAGE_REPOSITORY}-${IMAGE_TAG}.tar"
NAMESPACE="${NAMESPACE:-bosgenesis}"
REMOTE_USER="${REMOTE_USER:-taieuser}"
REMOTE_HOST="${REMOTE_HOST:-10.99.52.165}"
REMOTE_TMP_DIR="${REMOTE_TMP_DIR:-/tmp}"
REMOTE_IMAGE_TAR="${REMOTE_TMP_DIR}/${IMAGE_TAR}"
DEPLOYMENT_NAME="${DEPLOYMENT_NAME:-bosgenesis-k8s-data-ingestion-agent}"
CONTAINER_NAME="${CONTAINER_NAME:-app}"
DEPLOY_METHOD="${DEPLOY_METHOD:-kustomize}"
HELM_RELEASE="${HELM_RELEASE:-bosgenesis-k8s-data-ingestion-agent}"
HELM_CHART="${HELM_CHART:-charts/bosgenesis-k8s-data-ingestion-agent}"
KUSTOMIZE_DIR="${KUSTOMIZE_DIR:-deploy/k8s}"
ENABLE_INGRESS="${ENABLE_INGRESS:-false}"
SKIP_BUILD="${SKIP_BUILD:-false}"
SKIP_IMAGE_TRANSFER="${SKIP_IMAGE_TRANSFER:-false}"

log() {
  printf '\n[%s] %s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" "$*"
}

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Required command not found: $1" >&2
    exit 127
  fi
}

require_cmd kubectl
require_cmd ssh
require_cmd scp

if [ "${SKIP_BUILD}" != "true" ]; then
  require_cmd docker
  log "Building image ${IMAGE}"
  docker build -t "${IMAGE}" .

  log "Saving image to ${IMAGE_TAR}"
  docker save "${IMAGE}" -o "${IMAGE_TAR}"
fi

if [ "${SKIP_IMAGE_TRANSFER}" != "true" ]; then
  log "Copying image tar to ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_IMAGE_TAR}"
  scp "${IMAGE_TAR}" "${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_IMAGE_TAR}"

  log "Importing image into containerd on ${REMOTE_HOST}"
  ssh "${REMOTE_USER}@${REMOTE_HOST}" "sudo ctr -n k8s.io images import '${REMOTE_IMAGE_TAR}'"

  log "Verifying imported image on ${REMOTE_HOST}"
  ssh "${REMOTE_USER}@${REMOTE_HOST}" "sudo ctr -n k8s.io images list | grep '${IMAGE_REPOSITORY}'"
fi

log "Ensuring namespace ${NAMESPACE} exists"
kubectl get namespace "${NAMESPACE}" >/dev/null 2>&1 || kubectl create namespace "${NAMESPACE}"

if [ "${DEPLOY_METHOD}" = "helm" ]; then
  require_cmd helm
  log "Deploying with Helm release ${HELM_RELEASE}"
  helm upgrade --install "${HELM_RELEASE}" "${HELM_CHART}" \
    --namespace "${NAMESPACE}" \
    --set image.repository="${IMAGE_REPOSITORY}" \
    --set image.tag="${IMAGE_TAG}" \
    --set ingress.enabled="${ENABLE_INGRESS}"
else
  log "Applying Kubernetes manifests from ${KUSTOMIZE_DIR}"
  kubectl apply -k "${KUSTOMIZE_DIR}"

  if [ "${ENABLE_INGRESS}" = "true" ]; then
    log "Applying optional ingress"
    kubectl apply -f "${KUSTOMIZE_DIR}/ingress.yaml"
  fi

  log "Setting deployment image to ${IMAGE}"
  kubectl set image "deployment/${DEPLOYMENT_NAME}" \
    "${CONTAINER_NAME}=${IMAGE}" \
    -n "${NAMESPACE}"
fi

log "Waiting for rollout"
kubectl rollout status "deployment/${DEPLOYMENT_NAME}" -n "${NAMESPACE}"

log "Deployment containers"
kubectl get deployment "${DEPLOYMENT_NAME}" \
  -n "${NAMESPACE}" \
  -o jsonpath='{.spec.template.spec.containers[*].name}'
echo

log "Pods"
kubectl get pod -n "${NAMESPACE}" -o wide | grep "${DEPLOYMENT_NAME}" || true

log "Service"
kubectl get svc "${DEPLOYMENT_NAME}" -n "${NAMESPACE}"

log "Done"

