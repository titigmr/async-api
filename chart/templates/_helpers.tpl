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
Create image pull secret
*/}}
{{- define "helper.imagePullSecret" }}
{{- $registry := .registry -}}
{{- $username := .username -}}
{{- $password := .password -}}
{{- $email := .email -}}
{{- printf "{\"auths\":{\"%s\":{\"username\":\"%s\",\"password\":\"%s\",\"email\":\"%s\",\"auth\":\"%s\"}}}" $registry $username $password $email (printf "%s:%s" $username $password | b64enc) | b64enc }}
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
==========================================================================
DATABASE CONFIGURATION HELPERS
==========================================================================
Individual component helpers with intelligent fallback strategy
Priority: individual components > subchart defaults > error
*/}}
{{- define "chart.databaseHost" -}}
{{- if and .Values.database .Values.database.host -}}
{{- .Values.database.host -}}
{{- else if .Values.postgresql.enabled -}}
{{- include "chart.postgresql.fullname" . -}}
{{- else -}}
{{- fail "Database host required: either set database.host or enable postgresql subchart" -}}
{{- end -}}
{{- end -}}

{{- define "chart.databasePort" -}}
{{- if and .Values.database .Values.database.port -}}
{{- .Values.database.port -}}
{{- else if .Values.postgresql.enabled -}}
{{- .Values.postgresql.primary.service.ports.postgresql | default 5432 -}}
{{- else -}}
{{- 5432 -}}
{{- end -}}
{{- end -}}

{{- define "chart.databaseName" -}}
{{- if and .Values.database .Values.database.name -}}
{{- .Values.database.name -}}
{{- else if .Values.postgresql.enabled -}}
{{- .Values.postgresql.auth.database | default "postgres" -}}
{{- else -}}
{{- fail "Database name required: either set database.name or enable postgresql subchart" -}}
{{- end -}}
{{- end -}}

{{- define "chart.databaseUsername" -}}
{{- if and .Values.database .Values.database.username -}}
{{- .Values.database.username -}}
{{- else if .Values.postgresql.enabled -}}
{{- .Values.postgresql.auth.username | default "postgres" -}}
{{- else -}}
{{- fail "Database username required: either set database.username or enable postgresql subchart" -}}
{{- end -}}
{{- end -}}

{{- define "chart.databaseScheme" -}}
{{- .Values.database.scheme | default "postgresql+asyncpg" -}}
{{- end -}}

{{/*
==========================================================================
BROKER CONFIGURATION HELPERS
==========================================================================
Individual component helpers with intelligent fallback strategy
*/}}
{{- define "chart.brokerHost" -}}
{{- if and .Values.broker .Values.broker.host -}}
{{- .Values.broker.host -}}
{{- else if .Values.rabbitmq.enabled -}}
{{- include "chart.rabbitmq.fullname" . -}}
{{- else -}}
{{- fail "Broker host required: either set broker.host or enable rabbitmq subchart" -}}
{{- end -}}
{{- end -}}

{{- define "chart.brokerPort" -}}
{{- if and .Values.broker .Values.broker.port -}}
{{- .Values.broker.port -}}
{{- else if .Values.rabbitmq.enabled -}}
{{- .Values.rabbitmq.service.ports.amqp | default 5672 -}}
{{- else -}}
{{- 5672 -}}
{{- end -}}
{{- end -}}

{{- define "chart.brokerUsername" -}}
{{- if and .Values.broker .Values.broker.username -}}
{{- .Values.broker.username -}}
{{- else if .Values.rabbitmq.enabled -}}
{{- .Values.rabbitmq.auth.username | default "user" -}}
{{- else -}}
{{- fail "Broker username required: either set broker.username or enable rabbitmq subchart" -}}
{{- end -}}
{{- end -}}

{{- define "chart.brokerVhost" -}}
{{- if and .Values.broker .Values.broker.vhost -}}
{{- .Values.broker.vhost -}}
{{- else -}}
{{- "/" -}}
{{- end -}}
{{- end -}}

{{- define "chart.brokerScheme" -}}
{{- .Values.broker.scheme | default "amqp" -}}
{{- end -}}

{{/*
==========================================================================
PASSWORD AND SECRET MANAGEMENT HELPERS
==========================================================================
Intelligent secret name and key resolution with fallback strategy
*/}}
{{/*
Get database password secret name (existing secret or generated one)
*/}}
{{- define "chart.databasePasswordSecretName" -}}
{{- .Values.database.passwordFromSecret.name | default (printf "%s-passwords" (include "helper.fullname" .)) -}}
{{- end -}}

{{/*
Get database password secret key
*/}}
{{- define "chart.databasePasswordSecretKey" -}}
{{- .Values.database.passwordFromSecret.key | default "db-password" -}}
{{- end -}}

{{/*
Get broker password secret name (existing secret or generated one)
*/}}
{{- define "chart.brokerPasswordSecretName" -}}
{{- .Values.broker.passwordFromSecret.name | default (printf "%s-passwords" (include "helper.fullname" .)) -}}
{{- end -}}

{{/*
Get broker password secret key
*/}}
{{- define "chart.brokerPasswordSecretKey" -}}
{{- .Values.broker.passwordFromSecret.key | default "broker-password" -}}
{{- end -}}

{{/*
Get database password value (direct or from subchart)
*/}}
{{- define "chart.databasePassword" -}}
{{- .Values.database.password | default .Values.postgresql.auth.password | default "asynctask123" -}}
{{- end -}}

{{/*
Get broker password value (direct or from subchart)
*/}}
{{- define "chart.brokerPassword" -}}
{{- .Values.broker.password | default .Values.rabbitmq.auth.password | default "kalo" -}}
{{- end -}}

{{/*
==========================================================================
SUBCHART SERVICE NAME CONSTRUCTION
==========================================================================
Service name construction helpers that mimic subchart naming logic
*/}}
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
==========================================================================
KEDA AUTOSCALING HELPERS
==========================================================================
KEDA-specific helpers for autoscaling configuration
*/}}
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
{{- include "chart.brokerPassword" . -}}
{{- end -}}
