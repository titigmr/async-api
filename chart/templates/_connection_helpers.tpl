{{/*
Database service name construction (mimics PostgreSQL subchart logic)
*/}}
{{- define "chart.databaseServiceName" -}}
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
Broker service name construction (mimics RabbitMQ subchart logic)
*/}}
{{- define "chart.brokerServiceName" -}}
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
Database Host
*/}}
{{- define "chart.databaseHost" -}}
{{- if .Values.database.host -}}
{{- .Values.database.host -}}
{{- else if .Values.postgresql.enabled -}}
{{- include "chart.databaseServiceName" . -}}
{{- else -}}
{{- required "database.host is required when postgresql.enabled=false" .Values.database.host -}}
{{- end -}}
{{- end -}}

{{/*
Database Port
*/}}
{{- define "chart.databasePort" -}}
{{- .Values.database.port | default 5432 -}}
{{- end -}}

{{/*
Database User
*/}}
{{- define "chart.databaseUser" -}}
{{- if .Values.database.username -}}
{{- .Values.database.username -}}
{{- else if .Values.postgresql.enabled -}}
{{- .Values.postgresql.auth.username -}}
{{- else -}}
{{- required "database.username is required when postgresql.enabled=false" .Values.database.username -}}
{{- end -}}
{{- end -}}

{{/*
Database Password
*/}}
{{- define "chart.databasePassword" -}}
{{- if .Values.database.password -}}
{{- .Values.database.password -}}
{{- else if .Values.postgresql.enabled -}}
{{- .Values.postgresql.auth.password -}}
{{- else -}}
{{- required "database.password is required when postgresql.enabled=false" .Values.database.password -}}
{{- end -}}
{{- end -}}

{{/*
Database Name
*/}}
{{- define "chart.databaseName" -}}
{{- if .Values.database.database -}}
{{- .Values.database.database -}}
{{- else if .Values.postgresql.enabled -}}
{{- .Values.postgresql.auth.database -}}
{{- else -}}
{{- required "database.database is required when postgresql.enabled=false" .Values.database.database -}}
{{- end -}}
{{- end -}}

{{/*
Priority: url > fromSecret > components > defaults from postgresql subchart
*/}}
{{- define "chart.databaseUrl" -}}
{{- if .Values.database.url -}}
{{- .Values.database.url -}}
{{- else -}}
{{- $scheme := .Values.database.scheme | default "postgresql+asyncpg" -}}
{{- $host := "" -}}
{{- $port := .Values.database.port | default 5432 -}}
{{- $db := "" -}}
{{- $user := "" -}}
{{- $pass := "" -}}

{{/* Use provided components or defaults from postgresql subchart */}}
{{- if .Values.postgresql.enabled -}}
{{- $host = .Values.database.host | default (include "chart.databaseServiceName" .) -}}
{{- $db = .Values.database.database | default .Values.postgresql.auth.database -}}
{{- $user = .Values.database.username | default .Values.postgresql.auth.username -}}
{{- $pass = .Values.database.password | default .Values.postgresql.auth.password -}}
{{- else -}}
{{/* External database - all components must be provided */}}
{{- $host = .Values.database.host | required "database.host is required when postgresql.enabled=false" -}}
{{- $db = .Values.database.database | required "database.database is required when postgresql.enabled=false" -}}
{{- $user = .Values.database.username | required "database.username is required when postgresql.enabled=false" -}}
{{- $pass = .Values.database.password | required "database.password is required when postgresql.enabled=false" -}}
{{- end -}}

{{- printf "%s://%s:%s@%s:%v/%s" $scheme $user $pass $host $port $db -}}
{{- end -}}
{{- end -}}

{{/*
Broker URL construction with intelligent fallbacks
Priority: url > fromSecret > components > defaults from rabbitmq subchart
*/}}
{{- define "chart.brokerUrl" -}}
{{- if .Values.broker.url -}}
{{- .Values.broker.url -}}
{{- else -}}
{{- $scheme := .Values.broker.scheme | default "amqp" -}}
{{- $host := "" -}}
{{- $port := .Values.broker.port | default 5672 -}}
{{- $user := "" -}}
{{- $pass := "" -}}
{{- $vhost := .Values.broker.vhost | default "/" -}}

{{/* Use provided components or defaults from rabbitmq subchart */}}
{{- if .Values.rabbitmq.enabled -}}
{{- $host = .Values.broker.host | default (include "chart.brokerServiceName" .) -}}
{{- $user = .Values.broker.username | default .Values.rabbitmq.auth.username -}}
{{- $pass = .Values.broker.password | default .Values.rabbitmq.auth.password -}}
{{- else -}}
{{/* External broker - all components must be provided */}}
{{- $host = .Values.broker.host | required "broker.host is required when rabbitmq.enabled=false" -}}
{{- $user = .Values.broker.username | required "broker.username is required when rabbitmq.enabled=false" -}}
{{- $pass = .Values.broker.password | required "broker.password is required when rabbitmq.enabled=false" -}}
{{- end -}}

{{- printf "%s://%s:%s@%s:%v%s" $scheme $user $pass $host $port $vhost -}}
{{- end -}}
{{- end -}}
