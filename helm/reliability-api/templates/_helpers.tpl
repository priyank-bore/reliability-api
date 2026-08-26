{{- define "reliability-api.fullname" -}}
{{- .Chart.Name -}}
{{- end -}}

{{- define "reliability-api.labels" -}}
app.kubernetes.io/name: {{ .Chart.Name }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}
