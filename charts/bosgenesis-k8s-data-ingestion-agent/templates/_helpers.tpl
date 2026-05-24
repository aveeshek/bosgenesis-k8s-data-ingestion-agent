{{- define "data-ingestion-agent.name" -}}
bosgenesis-k8s-data-ingestion-agent
{{- end -}}

{{- define "data-ingestion-agent.namespace" -}}
{{- .Values.namespaceOverride | default .Release.Namespace -}}
{{- end -}}

{{- define "data-ingestion-agent.labels" -}}
app.kubernetes.io/name: {{ include "data-ingestion-agent.name" . }}
app.kubernetes.io/part-of: bosgenesis
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version }}
{{- end -}}

