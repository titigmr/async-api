{{/*
Expand the name of the chart.
*/}}
{{- define "helper.name" -}}
{{- (.Values.nameOverride | default .Chart.Name) | trunc 63 | trimSuffix "-" }}
{{- end }}


{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "helper.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := .Values.nameOverride | default .Chart.Name }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- (printf "%s-%s" .Release.Name $name) | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}


{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "helper.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}


{{/*
Create container environment variables from configmap
*/}}
{{- define "helper.env" -}}
{{ range $key, $val := .env }}
{{ $key }}: {{ $val | quote }}
{{- end }}
{{- end }}


{{/*
Create container environment variables from secret
*/}}
{{- define "helper.secret" -}}
{{ range $key, $val := .secrets }}
{{ $key }}: {{ $val | b64enc | quote }}
{{- end }}
{{- end }}


{{/*
Define a file checksum to trigger rollout on configmap of secret change
*/}}
{{- define "helper.checksum" -}}
{{- $ := index . 0 }}
{{- $path := index . 1 }}
{{- $resourceType := include (print $.Template.BasePath $path) $ | fromYaml -}}
{{- if $resourceType -}}
checksum-{{ $resourceType.kind | lower }}-{{ $resourceType.metadata.name }}: {{ $resourceType.data | toYaml | sha256sum }}
{{- end -}}
{{- end -}}

{{/*
Worker checksum helper - generates checksums for worker ConfigMaps and Secrets
Parameters:
- $root: The root context
- $workerName: The name of the worker
*/}}
{{- define "helper.workerChecksum" -}}
{{- $ := .root }}
{{- $workerName := .workerName }}
{{- range $.Values.workers }}
{{- if eq .name $workerName }}
{{- if .extraConfigMap }}
{{- range .extraConfigMap }}
checksum-configmap-{{ printf "%s-%s" (include "helper.fullname" $) .name }}: {{ .data | toYaml | sha256sum }}
{{- end }}
{{- end }}
{{- if .extraSecret }}
{{- range .extraSecret }}
checksum-secret-{{ printf "%s-%s" (include "helper.fullname" $) .name }}: {{ .data | toYaml | sha256sum }}
{{- end }}
{{- end }}
{{- end }}
{{- end }}
{{- end -}}


{{/*
Common labels
*/}}
{{- define "helper.commonLabels" -}}
helm.sh/chart: {{ include "helper.chart" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Generic selector labels
Parameters:
- $root: The root context
- $componentName: The name of the component for which the selector labels are being generated
*/}}
{{- define "helper.selectorLabels" -}}
{{- $root := .root | default $ -}}
{{- $componentName := .componentName | default "app" -}}
app.kubernetes.io/name: {{ printf "%s-%s" (include "helper.fullname" $root) $componentName | trunc 63 | trimSuffix "-" }}
app.kubernetes.io/instance: {{ $root.Release.Name | trunc 63 | trimSuffix "-" }}
{{- end -}}

{{/*
Generic app labels
Parameters:
- $root: The root context
- $componentName: The name of the component for which the selector labels are being generated
*/}}
{{- define "helper.labels" -}}
{{- $root := .root -}}
{{- $componentName := .componentName | default "app" -}}
{{ include "helper.commonLabels" $root }}
{{ include "helper.selectorLabels" (dict "root" $root "componentName" $componentName) }}
{{- end -}}


{{/*
Get database environment configuration type based on priority
Returns: "urlFromSecret", "url", "components", "postgresql"
*/}}
{{- define "chart.databaseEnvType" -}}
{{- if .Values.database.urlFromSecret.name -}}
urlFromSecret
{{- else if .Values.database.url -}}
url
{{- else if or .Values.database.components.host .Values.database.components.name .Values.database.components.username .Values.database.components.password -}}
components
{{- else if .Values.postgresql.enabled -}}
postgresql
{{- else -}}
{{- fail "Database configuration required: either set database.urlFromSecret, database.url, database.components, or enable postgresql subchart" -}}
{{- end -}}
{{- end -}}

{{/*
Get database secret name based on configuration type
*/}}
{{- define "chart.databaseSecretName" -}}
{{- $envType := include "chart.databaseEnvType" . -}}
{{- if eq $envType "urlFromSecret" -}}
{{- .Values.database.urlFromSecret.name -}}
{{- else if eq $envType "postgresql" -}}
{{- if .Values.postgresql.auth.password -}}
{{- printf "%s-database" (include "helper.fullname" .) -}}
{{- else -}}
{{- include "chart.postgresql.fullname" . -}}
{{- end -}}
{{- else -}}
{{- printf "%s-database" (include "helper.fullname" .) -}}
{{- end -}}
{{- end -}}

{{/*
Get broker environment configuration type based on priority
Returns: "urlFromSecret", "url", "components", "rabbitmq"
*/}}
{{- define "chart.brokerEnvType" -}}
{{- if .Values.broker.urlFromSecret.name -}}
urlFromSecret
{{- else if .Values.broker.url -}}
url
{{- else if or .Values.broker.components.host .Values.broker.components.username .Values.broker.components.password -}}
components
{{- else if .Values.rabbitmq.enabled -}}
rabbitmq
{{- else -}}
{{- fail "Broker configuration required: either set broker.urlFromSecret, broker.url, broker.components, or enable rabbitmq subchart" -}}
{{- end -}}
{{- end -}}

{{/*
==========================================================================
BACKWARD COMPATIBILITY HELPERS
==========================================================================
These helpers are kept for backward compatibility with existing templates
*/}}

{{/*
Helper to get the broker configuration
*/}}

{{- define "chart.brokerHost" -}}
{{- if .Values.broker.components.host -}}
{{- .Values.broker.components.host -}}
{{- else if .Values.rabbitmq.enabled -}}
{{- include "chart.rabbitmq.fullname" . -}}
{{- else -}}
{{- fail "Broker host required" -}}
{{- end -}}
{{- end -}}

{{- define "chart.brokerPort" -}}
{{- if .Values.broker.components.port -}}
{{- .Values.broker.components.port -}}
{{- else if .Values.rabbitmq.enabled -}}
{{- .Values.rabbitmq.service.ports.amqp | default 5672 -}}
{{- else -}}
{{- 5672 -}}
{{- end -}}
{{- end -}}

{{- define "chart.brokerUsername" -}}
{{- if .Values.broker.components.username -}}
{{- .Values.broker.components.username -}}
{{- else if .Values.rabbitmq.enabled -}}
{{- .Values.rabbitmq.auth.username | default "user" -}}
{{- else -}}
{{- fail "Broker username required" -}}
{{- end -}}
{{- end -}}

{{- define "chart.brokerVhost" -}}
{{- if .Values.broker.components.vhost -}}
{{- .Values.broker.components.vhost -}}
{{- else -}}
{{- "/" -}}
{{- end -}}
{{- end -}}

{{- define "chart.brokerScheme" -}}
{{- .Values.broker.components.scheme | default "amqp" -}}
{{- end -}}


{{/*
PostgreSQL service name construction (mimics subchart logic)
*/}}
{{- define "chart.postgresql.fullname" -}}
{{- if .Values.postgresql.fullnameOverride -}}
{{- .Values.postgresql.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- $name := .Values.postgresql.nameOverride | default "postgresql" -}}
{{- if contains $name .Release.Name -}}
{{- .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}
{{- end -}}

{{/*
RabbitMQ service name construction
*/}}
{{- define "chart.rabbitmq.fullname" -}}
{{- if .Values.rabbitmq.fullnameOverride -}}
{{- .Values.rabbitmq.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- $name := .Values.rabbitmq.nameOverride | default "rabbitmq" -}}
{{- if contains $name .Release.Name -}}
{{- .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}
{{- end -}}


{{/*
Get RabbitMQ address for KEDA (host:port format)
*/}}
{{- define "chart.kedaRabbitmqAddress" -}}
{{- printf "%s:%v" (include "chart.brokerHost" .) (include "chart.brokerPort" .) -}}
{{- end -}}

{{/*
Get RabbitMQ username for KEDA
*/}}
{{- define "chart.kedaRabbitmqUsername" -}}
{{- include "chart.brokerUsername" . -}}
{{- end -}}

{{/*
Get RabbitMQ password for KEDA
*/}}
{{- define "chart.kedaRabbitmqPassword" -}}
{{- if .Values.broker.components.password -}}
{{- .Values.broker.components.password -}}
{{- else if .Values.rabbitmq.enabled -}}
{{- .Values.rabbitmq.auth.password | default "kalo" -}}
{{- else -}}
{{- fail "Broker password required for KEDA" -}}
{{- end -}}
{{- end -}}
