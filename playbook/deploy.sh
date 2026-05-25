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
DEPLOY_METHOD="${DEPLOY_METHOD:-helm}"
HELM_RELEASE="${HELM_RELEASE:-bosgenesis-k8s-data-ingestion-agent}"
HELM_CHART="${HELM_CHART:-charts/bosgenesis-k8s-data-ingestion-agent}"
DEFAULT_HELM_VALUES_FILE="${HELM_CHART}/values.credentials.yaml"
HELM_VALUES_FILE="${HELM_VALUES_FILE:-}"
KUSTOMIZE_DIR="${KUSTOMIZE_DIR:-deploy/k8s}"
ENABLE_INGRESS="${ENABLE_INGRESS:-true}"
SKIP_BUILD="${SKIP_BUILD:-false}"
SKIP_IMAGE_TRANSFER="${SKIP_IMAGE_TRANSFER:-false}"
SECRET_NAME="${SECRET_NAME:-bosgenesis-k8s-data-ingestion-agent-secret}"

log() {
  printf '\n[%s] %s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" "$*"
}

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Required command not found: $1" >&2
    exit 127
  fi
}

adopt_helm_resource() {
  local kind="$1"
  local name="$2"

  if kubectl get "${kind}" "${name}" -n "${NAMESPACE}" >/dev/null 2>&1; then
    log "Adopting existing ${kind}/${name} into Helm release ${HELM_RELEASE}"
    kubectl label "${kind}" "${name}" \
      app.kubernetes.io/managed-by=Helm \
      -n "${NAMESPACE}" \
      --overwrite
    kubectl annotate "${kind}" "${name}" \
      meta.helm.sh/release-name="${HELM_RELEASE}" \
      meta.helm.sh/release-namespace="${NAMESPACE}" \
      -n "${NAMESPACE}" \
      --overwrite
  fi
}

adopt_existing_helm_resources() {
  if helm status "${HELM_RELEASE}" -n "${NAMESPACE}" >/dev/null 2>&1; then
    return
  fi

  if [ -n "${HELM_VALUES_FILE}" ] && [ -f "${HELM_VALUES_FILE}" ]; then
    parsed_secret_name="$(awk '
      /^[[:space:]]*secret:[[:space:]]*$/ { in_secret=1; next }
      /^[^[:space:]]/ { in_secret=0 }
      in_secret && /^[[:space:]]*name:[[:space:]]*/ {
        sub(/^[[:space:]]*name:[[:space:]]*/, "")
        gsub(/["'\''"]/, "")
        print
        exit
      }
    ' "${HELM_VALUES_FILE}")"
    if [ -n "${parsed_secret_name}" ]; then
      SECRET_NAME="${parsed_secret_name}"
    fi
  fi

  log "Checking for existing non-Helm resources to adopt"
  adopt_helm_resource serviceaccount "${DEPLOYMENT_NAME}"
  adopt_helm_resource configmap "${DEPLOYMENT_NAME}-config"
  adopt_helm_resource secret "${SECRET_NAME}"
  adopt_helm_resource service "${DEPLOYMENT_NAME}"
  adopt_helm_resource deployment "${DEPLOYMENT_NAME}"
  adopt_helm_resource ingress "${DEPLOYMENT_NAME}"
}

validate_helm_chart_files() {
  local helmignore_file="${HELM_CHART}/.helmignore"

  if [ -f "${helmignore_file}" ] && grep -F "**" "${helmignore_file}" >/dev/null 2>&1; then
    echo "Unsupported Helm ignore pattern found in ${helmignore_file}: double-star (**) is not supported by this Helm version." >&2
    echo "Use explicit single-level patterns such as templates/*.md instead." >&2
    exit 1
  fi
}

require_cmd kubectl
require_cmd ssh
require_cmd scp

if [ "${DEPLOY_METHOD}" = "helm" ]; then
  validate_helm_chart_files
fi

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
  ROLLOUT_TIMESTAMP="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
  log "Deploying with Helm release ${HELM_RELEASE}"
  if [ -z "${HELM_VALUES_FILE}" ] && [ -f "${DEFAULT_HELM_VALUES_FILE}" ]; then
    HELM_VALUES_FILE="${DEFAULT_HELM_VALUES_FILE}"
    log "Using Helm credentials values file ${HELM_VALUES_FILE}"
  fi
  adopt_existing_helm_resources
  helm_args=(
    upgrade
    --install
    "${HELM_RELEASE}"
    "${HELM_CHART}"
    --namespace "${NAMESPACE}"
    --set image.repository="${IMAGE_REPOSITORY}"
    --set image.tag="${IMAGE_TAG}"
    --set ingress.enabled="${ENABLE_INGRESS}"
    --set rolloutTimestamp="${ROLLOUT_TIMESTAMP}"
  )
  if [ -n "${HELM_VALUES_FILE}" ]; then
    helm_args+=(-f "${HELM_VALUES_FILE}")
  fi
  helm "${helm_args[@]}"
else
  log "Applying Kubernetes manifests from ${KUSTOMIZE_DIR}"
  kubectl apply -k "${KUSTOMIZE_DIR}"

  if [ "${ENABLE_INGRESS}" = "true" ]; then
    log "Ensuring ingress is applied"
    kubectl apply -f "${KUSTOMIZE_DIR}/ingress.yaml"
  else
    log "Ingress disabled; deleting ingress if present"
    kubectl delete ingress "${DEPLOYMENT_NAME}" -n "${NAMESPACE}" --ignore-not-found=true
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
