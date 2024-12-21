# Репозиторий для выполнения домашних заданий курса "Инфраструктурная платформа на основе Kubernetes-2024-10"

## Домашнее задание №8. Мониторинг приложения в кластере

Домашнее задание выполнено на `Linux fedora 6.12.4-200.fc41.x86_64`, `minikube v1.34.0 (docker)` с включенными аддонами default-storageclass, ingress, storage-provisioner.

1. Создан образ nginx c дополнительным location `/metics` ([Dockerfile](./Dockerfile)). Образ доступен на Docker Hub:
```
docker pull omaximov/metrics:nginx
```

2. Установлен `prometheus-operator` в кластер:
```
helm install prometheus-operator --namespace monitoring --create-namespace oci://registry-1.docker.io/bitnamicharts/kube-prometheus
```
3. Созданы [deployment](./deployment.yaml) и [service](./service.yaml) для развертывания образа nginx, созданного в п.1.
 В поде 2 контейнера, один из которых `nginx-exporter`, настроенный для сбора метрик nginx из контейнера `nginx` в том же поде:
```
- name: nginx-exporter
  image: nginx/nginx-prometheus-exporter:1.4.0
  ports:
  - name: nginx-exporter
    containerPort: 9113
  command: ['/usr/bin/nginx-prometheus-exporter']
  args: ['--nginx.scrape-uri=http://localhost:80/metrics']
```
```
kubectl apply -f namespace.yaml -f deployment.yaml -f service.yaml
```
4. Создан манифест [serviceMonitor](./serviceMonitor.yaml) для сбора prometheus'ом метрик с подов, на которые указывает созданный в п.3 сервис.
```
kubectl apply -f serviceMonitor.yaml
```
Для проверки необходимо из веб интерфейса `prometheus` запросить значение какой-либо метрики, снимаемой из развернутого nginx:
```
nginx_connections_accepted
nginx_connections_active
nginx_connections_handled
nginx_connections_reading
nginx_connections_waiting
nginx_connections_writing
nginx_exporter_build_info
nginx_http_requests_total
nginx_up
```
```
kubectl port-forward -n monitoring StatefulSet/prometheus-prometheus-operator-kube-p-prometheus 9090:9090
```
Либо, при помощи curl:
```
curl http://localhost:9090/api/v1/query\?query={nginx_connections_accepted} | jq
```
```
curl http://localhost:9090/api/v1/query\?query\=\{nginx_up\} | jq 
```