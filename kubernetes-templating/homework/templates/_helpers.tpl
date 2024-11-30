{{- define "homework.selectorLabels" -}}
app: {{ .Release.Name }}
{{- end }}

{{- define "homework.labels" -}}
{{ include "homework.selectorLabels" . }}
ChartName: {{ .Chart.Name | quote }}
{{- if .Chart.AppVersion }}
AppVersion: {{ .Chart.AppVersion | quote }}
{{- end }}
{{- if .Chart.Version }}
ChartVersion: {{ .Chart.Version | quote }}
{{- end }}
{{- end }}
