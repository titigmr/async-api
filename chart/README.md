# task

![Version: 0.1.0](https://img.shields.io/badge/Version-0.1.0-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square) ![AppVersion: 0.1.0](https://img.shields.io/badge/AppVersion-0.1.0-informational?style=flat-square)

A Helm chart to deploy Task Manager Api.

## Requirements

| Repository | Name | Version |
|------------|------|---------|
| <https://charts.bitnami.com/bitnami> | postgresql | >16.6.3 |
| <https://charts.bitnami.com/bitnami> | rabbitmq | >=16.0.11 |

## Values

### General

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| extraObjects | list | `[]` | Add extra specs dynamically to this chart. |
| fullnameOverride | string | `""` | String to fully override the default application name. |
| nameOverride | string | `""` | Provide a name in place of the default application name. |
| workers[0] | object | `{"deploymentSpec":{"affinity":{},"env":[{"name":"IN_QUEUE_NAME","value":"example_queue_in"},{"name":"OUT_QUEUE_NAME","value":"example_queue_out"},{"name":"LOG_LEVEL","value":"INFO"},{"name":"HEALTH_CHECK_ENABLED","value":"true"}],"envFromConfigMap":[],"envFromSecret":[],"extraAnnotations":{},"extraLabels":{},"image":{"pullPolicy":"IfNotPresent","repository":"github.com/titigmr/consumer","tag":"v0.1.0"},"imagePullSecrets":[],"nodeSelector":{},"podAnnotations":{},"podLabels":{},"podSecurityContext":{},"ports":{"health":8080},"probes":{"livenessProbe":{"failureThreshold":3,"httpGet":{"path":"/health","port":8080},"initialDelaySeconds":30,"periodSeconds":30,"successThreshold":1,"timeoutSeconds":5},"readinessProbe":{"failureThreshold":3,"httpGet":{"path":"/ready","port":8080},"initialDelaySeconds":5,"periodSeconds":10,"successThreshold":1,"timeoutSeconds":5},"startupProbe":{"failureThreshold":30,"httpGet":{"path":"/health","port":8080},"initialDelaySeconds":10,"periodSeconds":10,"successThreshold":1,"timeoutSeconds":5}},"replicas":1,"resources":{"limits":{"cpu":"500m","memory":"512Mi"},"requests":{"cpu":"100m","memory":"128Mi"}},"securityContext":{"fsGroup":1000,"runAsNonRoot":true,"runAsUser":1000},"serviceAccountName":"","tolerations":[],"topologySpreadConstraints":[]},"enabled":true,"extraConfigMap":[],"extraSecret":[],"extraVolumes":[],"jobSpec":{},"kedaAutoscaler":{"behavior":{"scaleDown":{"policies":[{"periodSeconds":60,"type":"Percent","value":50}],"stabilizationWindowSeconds":300},"scaleUp":{"policies":[{"periodSeconds":15,"type":"Percent","value":100},{"periodSeconds":15,"type":"Pods","value":4}],"selectPolicy":"Max","stabilizationWindowSeconds":0}},"cooldownPeriod":300,"enabled":true,"fallback":{"failureThreshold":3,"replicas":2},"idleReplicaCount":0,"maxReplicaCount":10,"minReplicaCount":1,"pollingInterval":30,"rabbitmq":{"queueLength":"5","queueName":"example_queue_in"}},"metrics":{"enabled":false,"path":"/metrics","port":8080,"serviceMonitor":{"annotations":{},"enabled":true,"interval":"30s","labels":{}}},"name":"example","role":{"create":true,"rules":[{"apiGroups":[""],"resources":["pods","configmaps","secrets"],"verbs":["get","list","watch"]}]},"type":"deployment"}` | Example worker demonstrating deployment with KEDA autoscaling |
| workers[1] | object | `{"deploymentSpec":{},"enabled":false,"extraConfigMap":[],"extraSecret":[],"extraVolumes":[],"jobSpec":{"activeDeadlineSeconds":3600,"backoffLimit":3,"env":[{"name":"IN_QUEUE_NAME","value":"job-tasks"},{"name":"OUT_QUEUE_NAME","value":"job-responses"},{"name":"WORKER_TYPE","value":"job-worker"},{"name":"LOG_LEVEL","value":"INFO"}],"envFromConfigMap":[],"envFromSecret":[],"image":{"pullPolicy":"IfNotPresent","repository":"your-registry/job-worker","tag":"latest"},"resources":{"limits":{"cpu":"1000m","memory":"1Gi"},"requests":{"cpu":"200m","memory":"256Mi"}},"securityContext":{"fsGroup":1000,"runAsNonRoot":true,"runAsUser":1000},"ttlSecondsAfterFinished":100},"kedaAutoscaler":{"behavior":{"scaleDown":{"policies":[{"periodSeconds":60,"type":"Pods","value":1}],"stabilizationWindowSeconds":60},"scaleUp":{"policies":[{"periodSeconds":30,"type":"Pods","value":2}],"stabilizationWindowSeconds":0}},"cooldownPeriod":120,"enabled":true,"fallback":{"failureThreshold":2,"replicas":1},"idleReplicaCount":0,"maxReplicaCount":5,"minReplicaCount":0,"pollingInterval":15,"rabbitmq":{"queueLength":"2","queueName":"job-tasks"},"scaleTargetApiVersion":"batch/v1","scaleTargetKind":"Job"},"metrics":{"enabled":false,"path":"/metrics","port":8080,"serviceMonitor":{"annotations":{},"enabled":true,"interval":"30s","labels":{"job-type":"batch-processor"}}},"name":"job-worker","role":{"create":true,"rules":[{"apiGroups":["batch"],"resources":["jobs"],"verbs":["get","list","watch","create","delete"]},{"apiGroups":[""],"resources":["pods","configmaps","secrets"],"verbs":["get","list","watch"]}]},"type":"job"}` | Example job worker with event-driven scaling |

### Global

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| global.env | object | `{}` | Map of environment variables to inject into all containers. |
| global.secrets | object | `{}` | Map of environment variables to inject into all containers. |

### Api

#### General

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| api.affinity | object | `{}` | Affinity used for app pod. |
| api.args | list | `[]` | Api container command args. |
| api.command | list | `[]` | Api container command. |
| api.config | string | `nil` |  |
| api.containerPort | int | `8000` | Api container port. |
| api.env | object | `{}` | Api container env variables, it will be injected into a configmap and loaded into the container. |
| api.envFrom | list | `[]` | Api container env variables loaded from configmap or secret reference. |
| api.extraContainers | list | `[]` | Extra containers to add to the app pod as sidecars. |
| api.extraPorts | list | `[]` | Api extra container ports. |
| api.hostAliases | list | `[]` | Host aliases that will be injected at pod-level into /etc/hosts. |
| api.imagePullSecrets | list | `[]` | Image credentials configuration. |
| api.initContainers | list | `[]` | Init containers to add to the app pod. |
| api.nodeSelector | object | `{}` | Default node selector for app. |
| api.podAnnotations | object | `{}` | Annotations for the app deployed pods. |
| api.podLabels | object | `{}` | Labels for the app deployed pods. |
| api.podSecurityContext | object | `{}` | Toggle and define pod-level security context. |
| api.replicaCount | int | `1` | The number of application controller pods to run. |
| api.revisionHistoryLimit | int | `10` | Revision history limit for the app. |
| api.secrets | object | `{}` | Api container env secrets, it will be injected into a secret and loaded into the container. |
| api.securityContext | object | `{}` | Toggle and define container-level security context. |
| api.tolerations | list | `[]` | Default tolerations for app. |
| api.volumeClaims | list | `[]` | List of volumeClaims to add. |
| api.volumeMounts | list | `[]` | List of mounts to add (normally used with `volumes` or `volumeClaims`). |
| api.volumes | list | `[]` | List of volumes to add. |

#### Autoscaling

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| api.autoscaling.enabled | bool | `false` | Enable Horizontal Pod Autoscaler for the app. |
| api.autoscaling.maxReplicas | int | `3` | Maximum number of replicas for the app. |
| api.autoscaling.minReplicas | int | `1` | Minimum number of replicas for the app. |
| api.autoscaling.targetCPUUtilizationPercentage | int | `80` | Average CPU utilization percentage for the app. |
| api.autoscaling.targetMemoryUtilizationPercentage | int | `80` | Average memory utilization percentage for the app. |

#### Image

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| api.image.pullPolicy | string | `"IfNotPresent"` | Image pull policy for the app. |
| api.image.repository | string | `"github.com/titigmr/asyncapi"` | Repository to use for the app. |
| api.image.tag | string | `"v0.1.0"` | Tag to use for the app. Overrides the image tag whose default is the chart appVersion. |

#### Ingress

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| api.ingress.annotations | object | `{}` | Additional ingress annotations. |
| api.ingress.className | string | `""` | Defines which ingress controller will implement the resource. |
| api.ingress.enabled | bool | `true` | Whether or not ingress should be enabled. |
| api.ingress.hosts[0].backend.portNumber | string | `nil` | Port used by the backend service linked to the host record (leave null to use the app service port). |
| api.ingress.hosts[0].backend.serviceName | string | `""` | Name of the backend service linked to the host record (leave empty to use the app service). |
| api.ingress.hosts[0].name | string | `"domain.local"` | Name of the host record. |
| api.ingress.hosts[0].path | string | `"/"` | Path of the host record to manage routing. |
| api.ingress.hosts[0].pathType | string | `"Prefix"` | Path type of the host record. |
| api.ingress.labels | object | `{}` | Additional ingress labels. |
| api.ingress.tls | list | `[]` | Enable TLS configuration. |

#### Listener

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| api.listener.args | list | `[]` | Listener container command args. |
| api.listener.command | list | `[]` |  |
| api.listener.env | object | `{}` |  |
| api.listener.probes.livenessProbe.failureThreshold | int | `3` |  |
| api.listener.probes.livenessProbe.httpGet.path | string | `"/health"` |  |
| api.listener.probes.livenessProbe.httpGet.port | int | `8081` |  |
| api.listener.probes.livenessProbe.initialDelaySeconds | int | `30` |  |
| api.listener.probes.livenessProbe.periodSeconds | int | `10` |  |
| api.listener.probes.livenessProbe.timeoutSeconds | int | `5` |  |
| api.listener.probes.readinessProbe.failureThreshold | int | `3` |  |
| api.listener.probes.readinessProbe.httpGet.path | string | `"/ready"` |  |
| api.listener.probes.readinessProbe.httpGet.port | int | `8081` |  |
| api.listener.probes.readinessProbe.initialDelaySeconds | int | `10` |  |
| api.listener.probes.readinessProbe.periodSeconds | int | `5` |  |
| api.listener.probes.readinessProbe.timeoutSeconds | int | `5` |  |

#### Metrics

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| api.metrics.enabled | bool | `false` | Deploy metrics service. |
| api.metrics.service.annotations | object | `{}` | Metrics service annotations. |
| api.metrics.service.labels | object | `{}` | Metrics service labels. |
| api.metrics.service.port | int | `8080` | Metrics service port. |
| api.metrics.service.targetPort | int | `8080` | Metrics service target port. |
| api.metrics.serviceMonitor.annotations | object | `{}` | Prometheus ServiceMonitor annotations. |
| api.metrics.serviceMonitor.enabled | bool | `false` | Enable a prometheus ServiceMonitor. |
| api.metrics.serviceMonitor.endpoints[0].basicAuth.password | string | `""` | The secret in the service monitor namespace that contains the password for authentication. |
| api.metrics.serviceMonitor.endpoints[0].basicAuth.username | string | `""` | The secret in the service monitor namespace that contains the username for authentication. |
| api.metrics.serviceMonitor.endpoints[0].bearerTokenSecret.key | string | `""` | Secret key to mount to read bearer token for scraping targets. The secret needs to be in the same namespace as the service monitor and accessible by the Prometheus Operator. |
| api.metrics.serviceMonitor.endpoints[0].bearerTokenSecret.name | string | `""` | Secret name to mount to read bearer token for scraping targets. The secret needs to be in the same namespace as the service monitor and accessible by the Prometheus Operator. |
| api.metrics.serviceMonitor.endpoints[0].honorLabels | bool | `false` | When true, honorLabels preserves the metric’s labels when they collide with the target’s labels. |
| api.metrics.serviceMonitor.endpoints[0].interval | string | `"30s"` | Prometheus ServiceMonitor interval. |
| api.metrics.serviceMonitor.endpoints[0].metricRelabelings | list | `[]` | Prometheus MetricRelabelConfigs to apply to samples before ingestion. |
| api.metrics.serviceMonitor.endpoints[0].path | string | `"/metrics"` | Path used by the Prometheus ServiceMonitor to scrape metrics. |
| api.metrics.serviceMonitor.endpoints[0].relabelings | list | `[]` | Prometheus RelabelConfigs to apply to samples before scraping. |
| api.metrics.serviceMonitor.endpoints[0].scheme | string | `""` | Prometheus ServiceMonitor scheme. |
| api.metrics.serviceMonitor.endpoints[0].scrapeTimeout | string | `"10s"` | Prometheus ServiceMonitor scrapeTimeout. If empty, Prometheus uses the global scrape timeout unless it is less than the target's scrape interval value in which the latter is used. |
| api.metrics.serviceMonitor.endpoints[0].selector | object | `{}` | Prometheus ServiceMonitor selector. |
| api.metrics.serviceMonitor.endpoints[0].tlsConfig | object | `{}` | Prometheus ServiceMonitor tlsConfig. |
| api.metrics.serviceMonitor.labels | object | `{}` | Prometheus ServiceMonitor labels. |

#### NetworkPolicy

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| api.networkPolicy.create | bool | `false` | Create NetworkPolicy object for the app. |
| api.networkPolicy.egress | list | `[]` | Egress rules for the NetworkPolicy object. |
| api.networkPolicy.ingress | list | `[]` | Ingress rules for the NetworkPolicy object. |
| api.networkPolicy.policyTypes | list | `["Ingress"]` | Policy types used in the NetworkPolicy object. |

#### Pdb

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| api.pdb.annotations | object | `{}` | Annotations to be added to app pdb. |
| api.pdb.enabled | bool | `false` | Deploy a PodDisruptionBudget for the app |
| api.pdb.labels | object | `{}` | Labels to be added to app pdb. |
| api.pdb.maxUnavailable | string | `""` | Number of pods that are unavailable after eviction as number or percentage (eg.: 50%). Has higher precedence over `api.pdb.minAvailable`. |
| api.pdb.minAvailable | string | `""` (defaults to 0 if not specified) | Number of pods that are available after eviction as number or percentage (eg.: 50%). |

#### Probes

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| api.probes.livenessProbe | object | `{"failureThreshold":3,"httpGet":{"path":"/internal/health","port":8000},"initialDelaySeconds":30,"periodSeconds":30,"successThreshold":1,"timeoutSeconds":5}` | Liveness probe configuration for the API container |
| api.probes.readinessProbe | object | `{"failureThreshold":3,"httpGet":{"path":"/internal/ready","port":8000},"initialDelaySeconds":5,"periodSeconds":10,"successThreshold":1,"timeoutSeconds":5}` | Readiness probe configuration for the API container |

#### Resources

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| api.resources.limits.cpu | string | `"500m"` | CPU limit for the app. |
| api.resources.limits.memory | string | `"2Gi"` | Memory limit for the app. |
| api.resources.requests.cpu | string | `"100m"` | CPU request for the app. |
| api.resources.requests.memory | string | `"256Mi"` | Memory request for the app. |

#### Service

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| api.service.extraPorts | list | `[]` | Extra service ports. |
| api.service.nodePort | int | `31000` | Port used when type is `NodePort` to expose the service on the given node port. |
| api.service.port | int | `8080` | Port used by the service. |
| api.service.portName | string | `"http"` | Port name used by the service. |
| api.service.protocol | string | `"TCP"` | Protocol used by the service. |
| api.service.type | string | `"ClusterIP"` | Type of service to create for the app. |

#### ServiceAccount

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| api.serviceAccount.annotations | object | `{}` | Annotations applied to created service account. |
| api.serviceAccount.automountServiceAccountToken | bool | `false` | Should the service account access token be automount in the pod. |
| api.serviceAccount.clusterRole.create | bool | `false` | Should the clusterRole be created. |
| api.serviceAccount.clusterRole.rules | list | `[]` | ClusterRole rules associated with the service account. |
| api.serviceAccount.create | bool | `false` | Create a service account. |
| api.serviceAccount.enabled | bool | `false` | Enable the service account. |
| api.serviceAccount.name | string | `""` | Service account name. |
| api.serviceAccount.role.create | bool | `false` | Should the role be created. |
| api.serviceAccount.role.rules | list | `[]` | Role rules associated with the service account. |

#### Strategy

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| api.strategy.rollingUpdate.maxSurge | int | `1` | The maximum number of pods that can be scheduled above the desired number of pods. |
| api.strategy.rollingUpdate.maxUnavailable | int | `1` | The maximum number of pods that can be unavailable during the update process. |
| api.strategy.type | string | `"RollingUpdate"` | Strategy type used to replace old Pods by new ones, can be `Recreate` or `RollingUpdate`. |

### Broker

#### General

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| broker.components | object | `{"host":"","password":"","port":5672,"scheme":"amqp","username":"","vhost":"/"}` | Broker components (creates secret with BROKER_HOST, BROKER_PORT, etc.) |
| broker.url | string | `""` | Broker connection URL (creates secret with BROKER_URL) Example: "amqp://user:pass@host:5672/vhost" |
| broker.urlFromSecret | object | `{}` | Use existing secret for broker url (highest priority - no secret creation) |

#### Components

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| broker.components.host | string | `""` | Broker host |
| broker.components.password | string | `""` | Broker password |
| broker.components.port | int | `5672` | Broker port |
| broker.components.scheme | string | `"amqp"` | Broker scheme for URL construction |
| broker.components.username | string | `""` | Broker username |
| broker.components.vhost | string | `"/"` | Virtual host for broker URL construction |

### Config

#### General

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| config.clients | object | `{"content":[{"authorizations":[{"quotas":100,"service":"example"},{"service":"example2"}],"client_id":"client1"}],"fromSecret":{}}` | Clients configuration file content or existing secret reference |
| config.mountPath | string | `"/app/config"` | Mount path for configuration files in containers |
| config.schemas | object | `{"files":[{"content":"{\n  \"$schema\": \"http://json-schema.org/draft-07/schema#\",\n  \"type\": \"object\",\n  \"properties\": {\n    \"sleep\": {\n      \"type\": \"integer\",\n      \"description\": \"Durée d'attente en secondes\"\n    },\n    \"mustSucceed\": {\n      \"type\": \"boolean\",\n      \"description\": \"Indique si la tâche doit réussir\"\n    }\n  },\n  \"required\": [\"sleep\"],\n  \"additionalProperties\": false\n}\n","name":"example.json"}],"fromSecret":{}}` | JSON Schema files configuration |
| config.services | object | `{"content":[{"in_queue":"example_queue_in","json_schema":"./config/schemas/example.json","name":"example","out_queue":"example_queue_out","quotas":1000},{"name":"example2"}],"fromSecret":{}}` | Services configuration file content or existing secret reference |

#### Clients

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| config.clients.content | list | `[{"authorizations":[{"quotas":100,"service":"example"},{"service":"example2"}],"client_id":"client1"}]` | If provided, will create a ConfigMap with this content |
| config.clients.fromSecret | object | `{}` | Use existing secret for clients configuration (optional) |

#### Schemas

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| config.schemas.files | list | `[{"content":"{\n  \"$schema\": \"http://json-schema.org/draft-07/schema#\",\n  \"type\": \"object\",\n  \"properties\": {\n    \"sleep\": {\n      \"type\": \"integer\",\n      \"description\": \"Durée d'attente en secondes\"\n    },\n    \"mustSucceed\": {\n      \"type\": \"boolean\",\n      \"description\": \"Indique si la tâche doit réussir\"\n    }\n  },\n  \"required\": [\"sleep\"],\n  \"additionalProperties\": false\n}\n","name":"example.json"}]` | Each entry will create a file in /app/config/schemas/ |
| config.schemas.fromSecret | object | `{}` | Alternative: Use existing secret for schemas |

#### Services

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| config.services.content | list | `[{"in_queue":"example_queue_in","json_schema":"./config/schemas/example.json","name":"example","out_queue":"example_queue_out","quotas":1000},{"name":"example2"}]` | If provided, will create a ConfigMap with this content |
| config.services.fromSecret | object | `{}` | Use existing secret for services configuration (optional) |

### Database

#### General

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| database.components | object | `{"host":"","name":"","password":"","port":5432,"scheme":"postgresql+asyncpg","username":""}` | Database components (creates secret with DB_HOST, DB_PORT, etc.) |
| database.url | string | `""` | Database connection URL (creates secret with DATABASE_URL) Example: "postgresql+asyncpg://user:pass@host:5432/dbname" |
| database.urlFromSecret | object | `{}` | Use existing secret for database url (highest priority - no secret creation) |

#### Components

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| database.components.host | string | `""` | Database host |
| database.components.name | string | `""` | Database name |
| database.components.password | string | `""` | Database password |
| database.components.port | int | `5432` | Database port |
| database.components.scheme | string | `"postgresql+asyncpg"` | Database scheme for URL construction |
| database.components.username | string | `""` | Database username |

### Postgresql

#### General

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| postgresql.architecture | string | `"standalone"` | PostgreSQL architecture |
| postgresql.auth | object | `{"database":"asynctask","existingSecret":"","password":"changeme123","postgresPassword":"postgres","postgresUser":"postgres","username":"asynctask"}` | PostgreSQL authentication configuration |
| postgresql.enabled | bool | `true` | Enable PostgreSQL subchart |
| postgresql.metrics | object | `{"enabled":false,"serviceMonitor":{"enabled":false}}` | PostgreSQL metrics configuration |
| postgresql.primary | object | `{"persistence":{"accessModes":["ReadWriteOnce"],"enabled":true,"size":"8Gi","storageClass":""},"resources":{"limits":{"cpu":"500m","memory":"512Mi"},"requests":{"cpu":"250m","memory":"256Mi"}},"service":{"ports":{"postgresql":5432},"type":"ClusterIP"}}` | PostgreSQL primary configuration |

#### Auth

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| postgresql.auth.database | string | `"asynctask"` | PostgreSQL database name |
| postgresql.auth.existingSecret | string | `""` | Use existing secret for PostgreSQL passwords |
| postgresql.auth.password | string | `"changeme123"` | PostgreSQL password for application user |
| postgresql.auth.postgresPassword | string | `"postgres"` | PostgreSQL root password (use existing secret or auto-generate) |
| postgresql.auth.postgresUser | string | `"postgres"` | PostgreSQL root user |
| postgresql.auth.username | string | `"asynctask"` | PostgreSQL username for application |

#### Metrics

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| postgresql.metrics.enabled | bool | `false` | Enable PostgreSQL metrics |
| postgresql.metrics.serviceMonitor | object | `{"enabled":false}` | PostgreSQL metrics service monitor |
| postgresql.metrics.serviceMonitor.enabled | bool | `false` | Enable PostgreSQL metrics service monitor |

#### Primary

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| postgresql.primary.persistence | object | `{"accessModes":["ReadWriteOnce"],"enabled":true,"size":"8Gi","storageClass":""}` | PostgreSQL primary persistence configuration |
| postgresql.primary.persistence.accessModes | list | `["ReadWriteOnce"]` | PostgreSQL primary persistence access modes |
| postgresql.primary.persistence.enabled | bool | `true` | Enable PostgreSQL primary persistence using PVC |
| postgresql.primary.persistence.size | string | `"8Gi"` | PostgreSQL primary persistence size |
| postgresql.primary.persistence.storageClass | string | `""` | PostgreSQL primary persistence storage class |
| postgresql.primary.resources | object | `{"limits":{"cpu":"500m","memory":"512Mi"},"requests":{"cpu":"250m","memory":"256Mi"}}` | PostgreSQL primary resources |
| postgresql.primary.resources.limits | object | `{"cpu":"500m","memory":"512Mi"}` | PostgreSQL primary resource limits |
| postgresql.primary.resources.requests | object | `{"cpu":"250m","memory":"256Mi"}` | PostgreSQL primary resource requests |
| postgresql.primary.service | object | `{"ports":{"postgresql":5432},"type":"ClusterIP"}` | PostgreSQL primary service configuration |
| postgresql.primary.service.ports | object | `{"postgresql":5432}` | PostgreSQL primary service port |
| postgresql.primary.service.type | string | `"ClusterIP"` | PostgreSQL primary service type |

### Rabbitmq

#### General

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| rabbitmq.auth | object | `{"erlangCookie":"secretcookie","existingErlangSecret":"","existingPasswordSecret":"","password":"changeme123","username":"asynctask"}` | RabbitMQ authentication configuration |
| rabbitmq.clustering | object | `{"addressType":"hostname","enabled":false,"replicaCount":1}` | RabbitMQ clustering configuration |
| rabbitmq.enabled | bool | `true` | Enable RabbitMQ subchart |
| rabbitmq.management | object | `{"enabled":true}` | RabbitMQ management plugin configuration |
| rabbitmq.metrics | object | `{"enabled":false,"serviceMonitor":{"enabled":false}}` | RabbitMQ metrics configuration |
| rabbitmq.persistence | object | `{"accessMode":"ReadWriteOnce","enabled":true,"size":"8Gi","storageClass":""}` | RabbitMQ persistence configuration |
| rabbitmq.resources | object | `{"limits":{"cpu":"500m","memory":"512Mi"},"requests":{"cpu":"250m","memory":"256Mi"}}` | RabbitMQ resources |
| rabbitmq.service | object | `{"ports":{"amqp":5672,"manager":15672},"type":"ClusterIP"}` | RabbitMQ service configuration |

#### Auth

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| rabbitmq.auth.erlangCookie | string | `"secretcookie"` | RabbitMQ erlang cookie |
| rabbitmq.auth.existingErlangSecret | string | `""` | Use existing secret for RabbitMQ erlang cookie |
| rabbitmq.auth.existingPasswordSecret | string | `""` | Use existing secret for RabbitMQ passwords |
| rabbitmq.auth.password | string | `"changeme123"` | RabbitMQ root password |
| rabbitmq.auth.username | string | `"asynctask"` | RabbitMQ root username |

#### Clustering

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| rabbitmq.clustering.addressType | string | `"hostname"` | RabbitMQ cluster formation discovery |
| rabbitmq.clustering.enabled | bool | `false` | Enable RabbitMQ clustering |
| rabbitmq.clustering.replicaCount | int | `1` | RabbitMQ cluster node count |

#### Management

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| rabbitmq.management.enabled | bool | `true` | Enable RabbitMQ management plugin |

#### Metrics

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| rabbitmq.metrics.enabled | bool | `false` | Enable RabbitMQ metrics |
| rabbitmq.metrics.serviceMonitor | object | `{"enabled":false}` | RabbitMQ metrics service monitor |
| rabbitmq.metrics.serviceMonitor.enabled | bool | `false` | Enable RabbitMQ metrics service monitor |

#### Persistence

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| rabbitmq.persistence.accessMode | string | `"ReadWriteOnce"` | RabbitMQ persistence access mode |
| rabbitmq.persistence.enabled | bool | `true` | Enable RabbitMQ persistence using PVC |
| rabbitmq.persistence.size | string | `"8Gi"` | RabbitMQ persistence size |
| rabbitmq.persistence.storageClass | string | `""` | RabbitMQ persistence storage class |

#### Resources

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| rabbitmq.resources.limits | object | `{"cpu":"500m","memory":"512Mi"}` | RabbitMQ resource limits |
| rabbitmq.resources.requests | object | `{"cpu":"250m","memory":"256Mi"}` | RabbitMQ resource requests |

#### Service

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| rabbitmq.service.ports | object | `{"amqp":5672,"manager":15672}` | RabbitMQ service ports |
| rabbitmq.service.ports.amqp | int | `5672` | RabbitMQ AMQP port |
| rabbitmq.service.ports.manager | int | `15672` | RabbitMQ management UI port |
| rabbitmq.service.type | string | `"ClusterIP"` | RabbitMQ service type |

### Workers[0]

#### General

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| workers[0].deploymentSpec | object | `{"affinity":{},"env":[{"name":"IN_QUEUE_NAME","value":"example_queue_in"},{"name":"OUT_QUEUE_NAME","value":"example_queue_out"},{"name":"LOG_LEVEL","value":"INFO"},{"name":"HEALTH_CHECK_ENABLED","value":"true"}],"envFromConfigMap":[],"envFromSecret":[],"extraAnnotations":{},"extraLabels":{},"image":{"pullPolicy":"IfNotPresent","repository":"github.com/titigmr/consumer","tag":"v0.1.0"},"imagePullSecrets":[],"nodeSelector":{},"podAnnotations":{},"podLabels":{},"podSecurityContext":{},"ports":{"health":8080},"probes":{"livenessProbe":{"failureThreshold":3,"httpGet":{"path":"/health","port":8080},"initialDelaySeconds":30,"periodSeconds":30,"successThreshold":1,"timeoutSeconds":5},"readinessProbe":{"failureThreshold":3,"httpGet":{"path":"/ready","port":8080},"initialDelaySeconds":5,"periodSeconds":10,"successThreshold":1,"timeoutSeconds":5},"startupProbe":{"failureThreshold":30,"httpGet":{"path":"/health","port":8080},"initialDelaySeconds":10,"periodSeconds":10,"successThreshold":1,"timeoutSeconds":5}},"replicas":1,"resources":{"limits":{"cpu":"500m","memory":"512Mi"},"requests":{"cpu":"100m","memory":"128Mi"}},"securityContext":{"fsGroup":1000,"runAsNonRoot":true,"runAsUser":1000},"serviceAccountName":"","tolerations":[],"topologySpreadConstraints":[]}` | Deployment-specific configuration (only used when type=deployment) |
| workers[0].enabled | bool | `true` | Enable/disable this worker |
| workers[0].extraConfigMap | list | `[]` | Additional ConfigMaps to create |
| workers[0].extraSecret | list | `[]` | Additional secrets to create |
| workers[0].extraVolumes | list | `[]` | Additional volumes to mount |
| workers[0].jobSpec | object | `{}` | Job-specific configuration (only used when type=job) |
| workers[0].kedaAutoscaler | object | `{"behavior":{"scaleDown":{"policies":[{"periodSeconds":60,"type":"Percent","value":50}],"stabilizationWindowSeconds":300},"scaleUp":{"policies":[{"periodSeconds":15,"type":"Percent","value":100},{"periodSeconds":15,"type":"Pods","value":4}],"selectPolicy":"Max","stabilizationWindowSeconds":0}},"cooldownPeriod":300,"enabled":true,"fallback":{"failureThreshold":3,"replicas":2},"idleReplicaCount":0,"maxReplicaCount":10,"minReplicaCount":1,"pollingInterval":30,"rabbitmq":{"queueLength":"5","queueName":"example_queue_in"}}` | KEDA autoscaler configuration |
| workers[0].metrics | object | `{"enabled":false,"path":"/metrics","port":8080,"serviceMonitor":{"annotations":{},"enabled":true,"interval":"30s","labels":{}}}` | Prometheus metrics configuration |
| workers[0].name | string | `"example"` | Worker name (used for labeling and naming resources) |
| workers[0].role | object | `{"create":true,"rules":[{"apiGroups":[""],"resources":["pods","configmaps","secrets"],"verbs":["get","list","watch"]}]}` | RBAC configuration |
| workers[0].type | string | `"deployment"` | Worker type: 'deployment' for long-running processes, 'job' for one-time tasks |

#### DeploymentSpec

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| workers[0].deploymentSpec.affinity | object | `{}` | Affinity rules |
| workers[0].deploymentSpec.env | list | `[{"name":"IN_QUEUE_NAME","value":"example_queue_in"},{"name":"OUT_QUEUE_NAME","value":"example_queue_out"},{"name":"LOG_LEVEL","value":"INFO"},{"name":"HEALTH_CHECK_ENABLED","value":"true"}]` | Environment variables as key-value pairs |
| workers[0].deploymentSpec.envFromConfigMap | list | `[]` | Environment variables from config maps |
| workers[0].deploymentSpec.envFromSecret | list | `[]` | Environment variables from secrets (database and broker URLs will be injected automatically) |
| workers[0].deploymentSpec.extraAnnotations | object | `{}` | Extra annotations for worker pods |
| workers[0].deploymentSpec.extraLabels | object | `{}` | Extra labels for worker pods |
| workers[0].deploymentSpec.image | object | `{"pullPolicy":"IfNotPresent","repository":"github.com/titigmr/consumer","tag":"v0.1.0"}` | Container image configuration |
| workers[0].deploymentSpec.image.pullPolicy | string | `"IfNotPresent"` | Image pull policy |
| workers[0].deploymentSpec.image.repository | string | `"github.com/titigmr/consumer"` | Image repository |
| workers[0].deploymentSpec.image.tag | string | `"v0.1.0"` | Image tag |
| workers[0].deploymentSpec.imagePullSecrets | list | `[]` | Image pull secrets for the worker |
| workers[0].deploymentSpec.nodeSelector | object | `{}` | Node selector |
| workers[0].deploymentSpec.podAnnotations | object | `{}` | Pod annotations |
| workers[0].deploymentSpec.podLabels | object | `{}` | Pod labels |
| workers[0].deploymentSpec.podSecurityContext | object | `{}` | Pod security context |
| workers[0].deploymentSpec.ports | object | `{"health":8080}` | Container ports configuration |
| workers[0].deploymentSpec.ports.health | int | `8080` | Health check port (used for probes and health service) |
| workers[0].deploymentSpec.probes | object | `{"livenessProbe":{"failureThreshold":3,"httpGet":{"path":"/health","port":8080},"initialDelaySeconds":30,"periodSeconds":30,"successThreshold":1,"timeoutSeconds":5},"readinessProbe":{"failureThreshold":3,"httpGet":{"path":"/ready","port":8080},"initialDelaySeconds":5,"periodSeconds":10,"successThreshold":1,"timeoutSeconds":5},"startupProbe":{"failureThreshold":30,"httpGet":{"path":"/health","port":8080},"initialDelaySeconds":10,"periodSeconds":10,"successThreshold":1,"timeoutSeconds":5}}` | Health check probes configuration |
| workers[0].deploymentSpec.probes.livenessProbe | object | `{"failureThreshold":3,"httpGet":{"path":"/health","port":8080},"initialDelaySeconds":30,"periodSeconds":30,"successThreshold":1,"timeoutSeconds":5}` | Liveness probe configuration |
| workers[0].deploymentSpec.probes.readinessProbe | object | `{"failureThreshold":3,"httpGet":{"path":"/ready","port":8080},"initialDelaySeconds":5,"periodSeconds":10,"successThreshold":1,"timeoutSeconds":5}` | Readiness probe configuration |
| workers[0].deploymentSpec.probes.startupProbe | object | `{"failureThreshold":30,"httpGet":{"path":"/health","port":8080},"initialDelaySeconds":10,"periodSeconds":10,"successThreshold":1,"timeoutSeconds":5}` | Startup probe configuration |
| workers[0].deploymentSpec.replicas | int | `1` | Number of replicas (ignored if KEDA autoscaling is enabled) |
| workers[0].deploymentSpec.resources | object | `{"limits":{"cpu":"500m","memory":"512Mi"},"requests":{"cpu":"100m","memory":"128Mi"}}` | Resource limits and requests |
| workers[0].deploymentSpec.resources.limits.cpu | string | `"500m"` | CPU limit |
| workers[0].deploymentSpec.resources.limits.memory | string | `"512Mi"` | Memory limit |
| workers[0].deploymentSpec.resources.requests.cpu | string | `"100m"` | CPU request |
| workers[0].deploymentSpec.resources.requests.memory | string | `"128Mi"` | Memory request |
| workers[0].deploymentSpec.securityContext | object | `{"fsGroup":1000,"runAsNonRoot":true,"runAsUser":1000}` | Container security context |
| workers[0].deploymentSpec.serviceAccountName | string | `""` | Service account name for the worker pods |
| workers[0].deploymentSpec.tolerations | list | `[]` | Tolerations |
| workers[0].deploymentSpec.topologySpreadConstraints | list | `[]` | Topology spread constraints |

#### KedaAutoscaler

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| workers[0].kedaAutoscaler.behavior | object | `{"scaleDown":{"policies":[{"periodSeconds":60,"type":"Percent","value":50}],"stabilizationWindowSeconds":300},"scaleUp":{"policies":[{"periodSeconds":15,"type":"Percent","value":100},{"periodSeconds":15,"type":"Pods","value":4}],"selectPolicy":"Max","stabilizationWindowSeconds":0}}` | Advanced scaling behavior configuration |
| workers[0].kedaAutoscaler.behavior.scaleDown.stabilizationWindowSeconds | int | `300` | Stabilization window for scale down |
| workers[0].kedaAutoscaler.behavior.scaleUp.stabilizationWindowSeconds | int | `0` | Stabilization window for scale up |
| workers[0].kedaAutoscaler.cooldownPeriod | int | `300` | Cooldown period in seconds |
| workers[0].kedaAutoscaler.enabled | bool | `true` | Enable KEDA autoscaling |
| workers[0].kedaAutoscaler.fallback | object | `{"failureThreshold":3,"replicas":2}` | Fallback configuration when KEDA fails |
| workers[0].kedaAutoscaler.fallback.failureThreshold | int | `3` | Number of failures before fallback |
| workers[0].kedaAutoscaler.fallback.replicas | int | `2` | Number of replicas during fallback |
| workers[0].kedaAutoscaler.idleReplicaCount | int | `0` | Number of replicas when no workload (0 to scale to zero) |
| workers[0].kedaAutoscaler.maxReplicaCount | int | `10` | Maximum number of replicas |
| workers[0].kedaAutoscaler.minReplicaCount | int | `1` | Minimum number of replicas |
| workers[0].kedaAutoscaler.pollingInterval | int | `30` | Polling interval in seconds |
| workers[0].kedaAutoscaler.rabbitmq | object | `{"queueLength":"5","queueName":"example_queue_in"}` | RabbitMQ trigger configuration for KEDA |
| workers[0].kedaAutoscaler.rabbitmq.queueLength | string | `"5"` | Target queue length to trigger scaling |
| workers[0].kedaAutoscaler.rabbitmq.queueName | string | `"example_queue_in"` | Queue name to monitor |

#### Metrics

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| workers[0].metrics.enabled | bool | `false` | Enable metrics endpoint |
| workers[0].metrics.path | string | `"/metrics"` | Metrics endpoint path |
| workers[0].metrics.port | int | `8080` | Metrics port |
| workers[0].metrics.serviceMonitor | object | `{"annotations":{},"enabled":true,"interval":"30s","labels":{}}` | ServiceMonitor configuration for Prometheus Operator |
| workers[0].metrics.serviceMonitor.annotations | object | `{}` | Additional annotations for ServiceMonitor |
| workers[0].metrics.serviceMonitor.enabled | bool | `true` | Create ServiceMonitor for Prometheus |
| workers[0].metrics.serviceMonitor.interval | string | `"30s"` | Scrape interval |
| workers[0].metrics.serviceMonitor.labels | object | `{}` | Additional labels for ServiceMonitor |

#### Role

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| workers[0].role.create | bool | `true` | Create ServiceAccount and RBAC resources |
| workers[0].role.rules | list | `[{"apiGroups":[""],"resources":["pods","configmaps","secrets"],"verbs":["get","list","watch"]}]` | RBAC rules for the worker |

### Workers[1]

#### General

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| workers[1].deploymentSpec | object | `{}` | Deployment configuration (not used for jobs) |
| workers[1].enabled | bool | `false` | Enable this worker |
| workers[1].extraConfigMap | list | `[]` | Additional ConfigMaps |
| workers[1].extraSecret | list | `[]` | Additional secrets |
| workers[1].extraVolumes | list | `[]` | Additional volumes |
| workers[1].jobSpec | object | `{"activeDeadlineSeconds":3600,"backoffLimit":3,"env":[{"name":"IN_QUEUE_NAME","value":"job-tasks"},{"name":"OUT_QUEUE_NAME","value":"job-responses"},{"name":"WORKER_TYPE","value":"job-worker"},{"name":"LOG_LEVEL","value":"INFO"}],"envFromConfigMap":[],"envFromSecret":[],"image":{"pullPolicy":"IfNotPresent","repository":"your-registry/job-worker","tag":"latest"},"resources":{"limits":{"cpu":"1000m","memory":"1Gi"},"requests":{"cpu":"200m","memory":"256Mi"}},"securityContext":{"fsGroup":1000,"runAsNonRoot":true,"runAsUser":1000},"ttlSecondsAfterFinished":100}` | Job-specific configuration |
| workers[1].kedaAutoscaler | object | `{"behavior":{"scaleDown":{"policies":[{"periodSeconds":60,"type":"Pods","value":1}],"stabilizationWindowSeconds":60},"scaleUp":{"policies":[{"periodSeconds":30,"type":"Pods","value":2}],"stabilizationWindowSeconds":0}},"cooldownPeriod":120,"enabled":true,"fallback":{"failureThreshold":2,"replicas":1},"idleReplicaCount":0,"maxReplicaCount":5,"minReplicaCount":0,"pollingInterval":15,"rabbitmq":{"queueLength":"2","queueName":"job-tasks"},"scaleTargetApiVersion":"batch/v1","scaleTargetKind":"Job"}` | KEDA configuration for job scaling |
| workers[1].metrics | object | `{"enabled":false,"path":"/metrics","port":8080,"serviceMonitor":{"annotations":{},"enabled":true,"interval":"30s","labels":{"job-type":"batch-processor"}}}` | Metrics configuration |
| workers[1].name | string | `"job-worker"` | Worker name |
| workers[1].role | object | `{"create":true,"rules":[{"apiGroups":["batch"],"resources":["jobs"],"verbs":["get","list","watch","create","delete"]},{"apiGroups":[""],"resources":["pods","configmaps","secrets"],"verbs":["get","list","watch"]}]}` | RBAC configuration |
| workers[1].type | string | `"job"` | Worker type |

#### JobSpec

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| workers[1].jobSpec.activeDeadlineSeconds | int | `3600` | Maximum job duration in seconds |
| workers[1].jobSpec.backoffLimit | int | `3` | Job execution parameters |
| workers[1].jobSpec.env | list | `[{"name":"IN_QUEUE_NAME","value":"job-tasks"},{"name":"OUT_QUEUE_NAME","value":"job-responses"},{"name":"WORKER_TYPE","value":"job-worker"},{"name":"LOG_LEVEL","value":"INFO"}]` | Environment variables |
| workers[1].jobSpec.envFromConfigMap | list | `[]` | Environment variables from config maps |
| workers[1].jobSpec.envFromSecret | list | `[]` | Environment variables from secrets |
| workers[1].jobSpec.image | object | `{"pullPolicy":"IfNotPresent","repository":"your-registry/job-worker","tag":"latest"}` | Container image configuration |
| workers[1].jobSpec.resources | object | `{"limits":{"cpu":"1000m","memory":"1Gi"},"requests":{"cpu":"200m","memory":"256Mi"}}` | Resource configuration |
| workers[1].jobSpec.securityContext | object | `{"fsGroup":1000,"runAsNonRoot":true,"runAsUser":1000}` | Security context |
| workers[1].jobSpec.ttlSecondsAfterFinished | int | `100` | Time to keep completed jobs (seconds) |

## Maintainers

| Name | Email | Url |
| ---- | ------ | --- |
| titigmr |  | <https://github.com/titigmr> |

## Sources

**Source code:**

* <https://github.com/titigmr/async-api>

----------------------------------------------
Autogenerated from chart metadata using [helm-docs v1.14.2](https://github.com/norwoodj/helm-docs/releases/v1.14.2)
