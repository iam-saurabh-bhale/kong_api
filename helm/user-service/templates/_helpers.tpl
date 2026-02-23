{{- define "user-service.name" -}}
user-service
{{- end }}

{{- define "user-service.fullname" -}}
{{ include "user-service.name" . }}
{{- end }}
