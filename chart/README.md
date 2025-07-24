# taskapi

![Version: 0.1.0](https://img.shields.io/badge/Version-0.1.0-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square) ![AppVersion: 0.1.0](https://img.shields.io/badge/AppVersion-0.1.0-informational?style=flat-square)

A Helm chart to deploy taskapi.

## Values

### General

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| extraObjects | list | `[]` | Add extra specs dynamically to this chart. |
| fullnameOverride | string | `""` | String to fully override the default application name. |
| nameOverride | string | `""` | Provide a name in place of the default application name. |

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
| api.containerPort | int | `8080` | Api container port. |
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
| api.statefulset | bool | `false` | Should the app run as a StatefulSet instead of a Deployment. |
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
| api.image.repository | string | `"docker.io/debian"` | Repository to use for the app. |
| api.image.tag | string | `""` | Tag to use for the app. Overrides the image tag whose default is the chart appVersion. |

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
| api.probes.healthcheck.path | string | `"/"` | Api container healthcheck endpoint. |
| api.probes.healthcheck.port | int | `8080` | Port to use for healthcheck (defaults to container port if not set) |
| api.probes.livenessProbe.enabled | bool | `true` | Whether or not enable the probe. |
| api.probes.livenessProbe.failureThreshold | int | `3` | Minimum consecutive failures for the probe to be considered failed after having succeeded. |
| api.probes.livenessProbe.initialDelaySeconds | int | `30` | Number of seconds after the container has started before probe is initiated. |
| api.probes.livenessProbe.periodSeconds | int | `30` | How often (in seconds) to perform the probe. |
| api.probes.livenessProbe.successThreshold | int | `1` | Minimum consecutive successes for the probe to be considered successful after having failed. |
| api.probes.livenessProbe.timeoutSeconds | int | `5` | Number of seconds after which the probe times out. |
| api.probes.readinessProbe.enabled | bool | `true` | Whether or not enable the probe. |
| api.probes.readinessProbe.failureThreshold | int | `2` | Minimum consecutive failures for the probe to be considered failed after having succeeded. |
| api.probes.readinessProbe.initialDelaySeconds | int | `10` | Number of seconds after the container has started before probe is initiated. |
| api.probes.readinessProbe.periodSeconds | int | `10` | How often (in seconds) to perform the probe. |
| api.probes.readinessProbe.successThreshold | int | `2` | Minimum consecutive successes for the probe to be considered successful after having failed. |
| api.probes.readinessProbe.timeoutSeconds | int | `5` | Number of seconds after which the probe times out. |
| api.probes.startupProbe.enabled | bool | `true` | Whether or not enable the probe. |
| api.probes.startupProbe.failureThreshold | int | `10` | Minimum consecutive failures for the probe to be considered failed after having succeeded. |
| api.probes.startupProbe.initialDelaySeconds | int | `0` | Number of seconds after the container has started before probe is initiated. |
| api.probes.startupProbe.periodSeconds | int | `10` | How often (in seconds) to perform the probe. |
| api.probes.startupProbe.successThreshold | int | `1` | Minimum consecutive successes for the probe to be considered successful after having failed. |
| api.probes.startupProbe.timeoutSeconds | int | `5` | Number of seconds after which the probe times out. |

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
| api.service.port | int | `80` | Port used by the service. |
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

### Worker

#### General

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| worker.affinity | object | `{}` | Affinity used for app pod. |
| worker.args | list | `[]` | Worker container command args. |
| worker.command | list | `[]` | Worker container command. |
| worker.containerPort | int | `8080` | Worker container port. |
| worker.env | object | `{}` | Worker container env variables, it will be injected into a configmap and loaded into the container. |
| worker.envFrom | list | `[]` | Worker container env variables loaded from configmap or secret reference. |
| worker.extraContainers | list | `[]` | Extra containers to add to the app pod as sidecars. |
| worker.extraPorts | list | `[]` | Worker extra container ports. |
| worker.hostAliases | list | `[]` | Host aliases that will be injected at pod-level into /etc/hosts. |
| worker.imagePullSecrets | list | `[]` | Image credentials configuration. |
| worker.initContainers | list | `[]` | Init containers to add to the app pod. |
| worker.nodeSelector | object | `{}` | Default node selector for app. |
| worker.podAnnotations | object | `{}` | Annotations for the app deployed pods. |
| worker.podLabels | object | `{}` | Labels for the app deployed pods. |
| worker.podSecurityContext | object | `{}` | Toggle and define pod-level security context. |
| worker.replicaCount | int | `1` | The number of application controller pods to run. |
| worker.revisionHistoryLimit | int | `10` | Revision history limit for the app. |
| worker.secrets | object | `{}` | Worker container env secrets, it will be injected into a secret and loaded into the container. |
| worker.securityContext | object | `{}` | Toggle and define container-level security context. |
| worker.statefulset | bool | `false` | Should the app run as a StatefulSet instead of a Deployment. |
| worker.tolerations | list | `[]` | Default tolerations for app. |
| worker.volumeClaims | list | `[]` | List of volumeClaims to add. |
| worker.volumeMounts | list | `[]` | List of mounts to add (normally used with `volumes` or `volumeClaims`). |
| worker.volumes | list | `[]` | List of volumes to add. |

#### Autoscaling

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| worker.autoscaling.enabled | bool | `false` | Enable Horizontal Pod Autoscaler for the app. |
| worker.autoscaling.maxReplicas | int | `3` | Maximum number of replicas for the app. |
| worker.autoscaling.minReplicas | int | `1` | Minimum number of replicas for the app. |
| worker.autoscaling.targetCPUUtilizationPercentage | int | `80` | Average CPU utilization percentage for the app. |
| worker.autoscaling.targetMemoryUtilizationPercentage | int | `80` | Average memory utilization percentage for the app. |

#### Image

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| worker.image.pullPolicy | string | `"IfNotPresent"` | Image pull policy for the app. |
| worker.image.repository | string | `"docker.io/debian"` | Repository to use for the app. |
| worker.image.tag | string | `""` | Tag to use for the app. Overrides the image tag whose default is the chart appVersion. |

#### Ingress

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| worker.ingress.annotations | object | `{}` | Additional ingress annotations. |
| worker.ingress.className | string | `""` | Defines which ingress controller will implement the resource. |
| worker.ingress.enabled | bool | `true` | Whether or not ingress should be enabled. |
| worker.ingress.hosts[0].backend.portNumber | string | `nil` | Port used by the backend service linked to the host record (leave null to use the app service port). |
| worker.ingress.hosts[0].backend.serviceName | string | `""` | Name of the backend service linked to the host record (leave empty to use the app service). |
| worker.ingress.hosts[0].name | string | `"domain.local"` | Name of the host record. |
| worker.ingress.hosts[0].path | string | `"/"` | Path of the host record to manage routing. |
| worker.ingress.hosts[0].pathType | string | `"Prefix"` | Path type of the host record. |
| worker.ingress.labels | object | `{}` | Additional ingress labels. |
| worker.ingress.tls | list | `[]` | Enable TLS configuration. |

#### Metrics

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| worker.metrics.enabled | bool | `false` | Deploy metrics service. |
| worker.metrics.service.annotations | object | `{}` | Metrics service annotations. |
| worker.metrics.service.labels | object | `{}` | Metrics service labels. |
| worker.metrics.service.port | int | `8080` | Metrics service port. |
| worker.metrics.service.targetPort | int | `8080` | Metrics service target port. |
| worker.metrics.serviceMonitor.annotations | object | `{}` | Prometheus ServiceMonitor annotations. |
| worker.metrics.serviceMonitor.enabled | bool | `false` | Enable a prometheus ServiceMonitor. |
| worker.metrics.serviceMonitor.endpoints[0].basicAuth.password | string | `""` | The secret in the service monitor namespace that contains the password for authentication. |
| worker.metrics.serviceMonitor.endpoints[0].basicAuth.username | string | `""` | The secret in the service monitor namespace that contains the username for authentication. |
| worker.metrics.serviceMonitor.endpoints[0].bearerTokenSecret.key | string | `""` | Secret key to mount to read bearer token for scraping targets. The secret needs to be in the same namespace as the service monitor and accessible by the Prometheus Operator. |
| worker.metrics.serviceMonitor.endpoints[0].bearerTokenSecret.name | string | `""` | Secret name to mount to read bearer token for scraping targets. The secret needs to be in the same namespace as the service monitor and accessible by the Prometheus Operator. |
| worker.metrics.serviceMonitor.endpoints[0].honorLabels | bool | `false` | When true, honorLabels preserves the metric’s labels when they collide with the target’s labels. |
| worker.metrics.serviceMonitor.endpoints[0].interval | string | `"30s"` | Prometheus ServiceMonitor interval. |
| worker.metrics.serviceMonitor.endpoints[0].metricRelabelings | list | `[]` | Prometheus MetricRelabelConfigs to apply to samples before ingestion. |
| worker.metrics.serviceMonitor.endpoints[0].path | string | `"/metrics"` | Path used by the Prometheus ServiceMonitor to scrape metrics. |
| worker.metrics.serviceMonitor.endpoints[0].relabelings | list | `[]` | Prometheus RelabelConfigs to apply to samples before scraping. |
| worker.metrics.serviceMonitor.endpoints[0].scheme | string | `""` | Prometheus ServiceMonitor scheme. |
| worker.metrics.serviceMonitor.endpoints[0].scrapeTimeout | string | `"10s"` | Prometheus ServiceMonitor scrapeTimeout. If empty, Prometheus uses the global scrape timeout unless it is less than the target's scrape interval value in which the latter is used. |
| worker.metrics.serviceMonitor.endpoints[0].selector | object | `{}` | Prometheus ServiceMonitor selector. |
| worker.metrics.serviceMonitor.endpoints[0].tlsConfig | object | `{}` | Prometheus ServiceMonitor tlsConfig. |
| worker.metrics.serviceMonitor.labels | object | `{}` | Prometheus ServiceMonitor labels. |

#### NetworkPolicy

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| worker.networkPolicy.create | bool | `false` | Create NetworkPolicy object for the app. |
| worker.networkPolicy.egress | list | `[]` | Egress rules for the NetworkPolicy object. |
| worker.networkPolicy.ingress | list | `[]` | Ingress rules for the NetworkPolicy object. |
| worker.networkPolicy.policyTypes | list | `["Ingress"]` | Policy types used in the NetworkPolicy object. |

#### Pdb

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| worker.pdb.annotations | object | `{}` | Annotations to be added to app pdb. |
| worker.pdb.enabled | bool | `false` | Deploy a PodDisruptionBudget for the app |
| worker.pdb.labels | object | `{}` | Labels to be added to app pdb. |
| worker.pdb.maxUnavailable | string | `""` | Number of pods that are unavailable after eviction as number or percentage (eg.: 50%). Has higher precedence over `worker.pdb.minAvailable`. |
| worker.pdb.minAvailable | string | `""` (defaults to 0 if not specified) | Number of pods that are available after eviction as number or percentage (eg.: 50%). |

#### Probes

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| worker.probes.healthcheck.path | string | `"/"` | Worker container healthcheck endpoint. |
| worker.probes.healthcheck.port | int | `8080` | Port to use for healthcheck (defaults to container port if not set) |
| worker.probes.livenessProbe.enabled | bool | `true` | Whether or not enable the probe. |
| worker.probes.livenessProbe.failureThreshold | int | `3` | Minimum consecutive failures for the probe to be considered failed after having succeeded. |
| worker.probes.livenessProbe.initialDelaySeconds | int | `30` | Number of seconds after the container has started before probe is initiated. |
| worker.probes.livenessProbe.periodSeconds | int | `30` | How often (in seconds) to perform the probe. |
| worker.probes.livenessProbe.successThreshold | int | `1` | Minimum consecutive successes for the probe to be considered successful after having failed. |
| worker.probes.livenessProbe.timeoutSeconds | int | `5` | Number of seconds after which the probe times out. |
| worker.probes.readinessProbe.enabled | bool | `true` | Whether or not enable the probe. |
| worker.probes.readinessProbe.failureThreshold | int | `2` | Minimum consecutive failures for the probe to be considered failed after having succeeded. |
| worker.probes.readinessProbe.initialDelaySeconds | int | `10` | Number of seconds after the container has started before probe is initiated. |
| worker.probes.readinessProbe.periodSeconds | int | `10` | How often (in seconds) to perform the probe. |
| worker.probes.readinessProbe.successThreshold | int | `2` | Minimum consecutive successes for the probe to be considered successful after having failed. |
| worker.probes.readinessProbe.timeoutSeconds | int | `5` | Number of seconds after which the probe times out. |
| worker.probes.startupProbe.enabled | bool | `true` | Whether or not enable the probe. |
| worker.probes.startupProbe.failureThreshold | int | `10` | Minimum consecutive failures for the probe to be considered failed after having succeeded. |
| worker.probes.startupProbe.initialDelaySeconds | int | `0` | Number of seconds after the container has started before probe is initiated. |
| worker.probes.startupProbe.periodSeconds | int | `10` | How often (in seconds) to perform the probe. |
| worker.probes.startupProbe.successThreshold | int | `1` | Minimum consecutive successes for the probe to be considered successful after having failed. |
| worker.probes.startupProbe.timeoutSeconds | int | `5` | Number of seconds after which the probe times out. |

#### Resources

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| worker.resources.limits.cpu | string | `"500m"` | CPU limit for the app. |
| worker.resources.limits.memory | string | `"2Gi"` | Memory limit for the app. |
| worker.resources.requests.cpu | string | `"100m"` | CPU request for the app. |
| worker.resources.requests.memory | string | `"256Mi"` | Memory request for the app. |

#### Service

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| worker.service.extraPorts | list | `[]` | Extra service ports. |
| worker.service.nodePort | int | `31000` | Port used when type is `NodePort` to expose the service on the given node port. |
| worker.service.port | int | `80` | Port used by the service. |
| worker.service.portName | string | `"http"` | Port name used by the service. |
| worker.service.protocol | string | `"TCP"` | Protocol used by the service. |
| worker.service.type | string | `"ClusterIP"` | Type of service to create for the app. |

#### ServiceAccount

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| worker.serviceAccount.annotations | object | `{}` | Annotations applied to created service account. |
| worker.serviceAccount.automountServiceAccountToken | bool | `false` | Should the service account access token be automount in the pod. |
| worker.serviceAccount.clusterRole.create | bool | `false` | Should the clusterRole be created. |
| worker.serviceAccount.clusterRole.rules | list | `[]` | ClusterRole rules associated with the service account. |
| worker.serviceAccount.create | bool | `false` | Create a service account. |
| worker.serviceAccount.enabled | bool | `false` | Enable the service account. |
| worker.serviceAccount.name | string | `""` | Service account name. |
| worker.serviceAccount.role.create | bool | `false` | Should the role be created. |
| worker.serviceAccount.role.rules | list | `[]` | Role rules associated with the service account. |

#### Strategy

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| worker.strategy.rollingUpdate.maxSurge | int | `1` | The maximum number of pods that can be scheduled above the desired number of pods. |
| worker.strategy.rollingUpdate.maxUnavailable | int | `1` | The maximum number of pods that can be unavailable during the update process. |
| worker.strategy.type | string | `"RollingUpdate"` | Strategy type used to replace old Pods by new ones, can be `Recreate` or `RollingUpdate`. |

## Sources

**Source code:**

----------------------------------------------
Autogenerated from chart metadata using [helm-docs v1.14.2](https://github.com/norwoodj/helm-docs/releases/v1.14.2)
