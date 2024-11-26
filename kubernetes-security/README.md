# Репозиторий для выполнения домашних заданий курса "Инфраструктурная платформа на основе Kubernetes-2024-10" 

## Домашнее задание №5. Настройка сервисных аккаунтов и ограничение прав для них

Домашнее задание выполнено на `Linux fedora 6.11.7-300.fc41.x86_64`, `minikube v1.34.0 (docker)` с включенными аддонами default-storageclass, ingress, storage-provisioner.

1. Создан namespace `homework`. В namespace `homework` создан service account `monitoring` с доступом к эндпоинту `/metrics`. Поскольку `/metrics` это non-resource URL, не относящийся к namespace, для доступа к нему созданы `ClusterRole` и `ClusterRoleBinding`.

```
kubectl apply -f namespace.yaml -f serviceAccount.yaml -f clusterRole.yaml -f clusterRoleBinding.yaml
```

`serviceAccount.yaml`
```
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: monitoring
  namespace: homework
```
`clusterRole.yaml`
```
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: metrics-reader
rules:
  - nonResourceURLs:
      - "/metrics"
    verbs:
      - get
```
`clusterRoleBinding.yaml`
```
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: read-metrics
subjects:
- kind: ServiceAccount
  name: monitoring
  namespace: homework
roleRef:
  kind: ClusterRole
  name: metrics-reader
  apiGroup: rbac.authorization.k8s.io
```
2. В манифест `deployment.yaml` добавлен созданный service account.
```
kubectl apply -f deployment.yaml
```

```
...
    spec:
      serviceAccountName: monitoring
      automountServiceAccountToken: true
...
```

3. В namespace `homework` создан service account `cd`. В кластере изначально присутствует кластерная роль `admin`. Если кластерную роль привязать к аккаунту посредством RoleBinding, то действие кластерной роли будет распространяться на неймспейс, в котором создана RoleBinding. Поэтому для назначения роли `admin` сервисному аккаунту `cd` на неймспеймс `homework` достаточно создать в этом неймспейсе RoleBinding этой роли к сервисному аккаунту.
```
kubectl apply -f serviceAccount.yaml -f roleBinding.yaml
```

`serviceAccount.yaml`
```
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: cd
  namespace: homework
```

`roleBinding.yaml`
```
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: homework-admin
  namespace: homework
subjects:
- kind: ServiceAccount
  name: cd
  namespace: homework
roleRef:
  kind: ClusterRole
  name: admin
  apiGroup: rbac.authorization.k8s.io
```

4. Для создания `kubeconfig` создан постоянный токен для сервис аккаунта `cd`.

`secret.yaml`
```
kubectl apply -f secret.yaml
```
```
apiVersion: v1
kind: Secret
metadata:
  name: cd-token
  namespace: homework
  annotations:
    kubernetes.io/service-account.name: cd
type: kubernetes.io/service-account-token
```
```
# Извлечение токена для добавления в kubeconfig
kubectl get secret/cd-token -n homework -o json | jq -r .data.token | base64 -d > permanent_token
```

5. Создан файл `kubeconfig` с именем `homework-kubeconfig` для сервис аккаунта `cd`.

```
# Добавление параметров кластера в kubeconfig
kubectl config --kubeconfig=homework-kubeconfig set-cluster minikube --server=https://$(minikube ip):8443 --certificate-authority=$HOME/.minikube/ca.crt
...
Cluster "minikube" set.

# Добавление параметров пользователя в kubeconfig
kubectl config --kubeconfig=homework-kubeconfig set-credentials cd --token=$(cat ./permanent_token)
...
User "cd" set.

# Добавление параметров контекста в kubeconfig
kubectl config --kubeconfig=homework-kubeconfig set-context cd@minikube --cluster=minikube --namespace=homework --user=cd
...
Context "cd@minikube" created.

# Переключение на созданный контекст
kubectl config --kubeconfig=homework-kubeconfig use-context cd@minikube
...
Switched to context "cd@minikube".

# Просмотр полученного kubeconfig
kubectl config --kubeconfig=homework-kubeconfig view
```

`homework-kubeconfig`
```
apiVersion: v1
clusters:
- cluster:
    certificate-authority: /home/username/.minikube/ca.crt
    server: https://192.168.49.2:8443
  name: minikube
contexts:
- context:
    cluster: minikube
    namespace: homework
    user: cd
  name: cd@minikube
current-context: cd@minikube
kind: Config
preferences: {}
users:
- name: cd
  user:
    token: REDACTED
```
Проверка доступа в кластер с использованием созданного `kubeconfig`:

```
kubectl --kubeconfig=homework-kubeconfig get pod -n homework
...
NAME                                   READY   STATUS    RESTARTS   AGE
homework-deployment-767b98c486-gmdt8   1/1     Running   0          76s
homework-deployment-767b98c486-n57x6   1/1     Running   0          76s
homework-deployment-767b98c486-t7jjb   1/1     Running   0          76s
```

```
kubectl --kubeconfig=homework-kubeconfig get pod -n kube-system
...
Error from server (Forbidden): pods is forbidden: User "system:serviceaccount:homework:cd" cannot list resource "pods" in API group "" in the namespace "kube-system"
```

6. Сгенерирован токен для сервис аккаунта `cd` сроком действия 1 день и сохранен в файл `token`.

```
kubectl create token cd --namespace homework --duration=24h > token
``` 
Токен можно использовать в `kubeconfig`:

```
kubectl config --kubeconfig=homework-kubeconfig set-credentials cd --token=$(cat ./token)
```

7. Для задания со * исправлен init контейнер в `deployment.yaml` для обращения к эндпоинту кластера `/metrics`:

```
- name: init
  image: alpine:3.20
  command: ['/bin/sh']
  args: ['-c', 'echo "<html><body>Homework 5</body></html>" > /init/index.html; apk add curl; curl --cacert $CA_CERT --header "Authorization: Bearer $(cat $TOKEN)" -X GET $KUBE_API/metrics > /init/metrics.html']
  env:
  - name: KUBE_API
    value: "https://kubernetes.default.svc"
  - name: CA_CERT
    value: "/var/run/secrets/kubernetes.io/serviceaccount/ca.crt"
  - name: NAMESPACE
    value: "/var/run/secrets/kubernetes.io/serviceaccount/namespace"
  - name: TOKEN
    value: "/var/run/secrets/kubernetes.io/serviceaccount/token"
  volumeMounts:
  - mountPath: /init
    name: shared-volume
    subPath: homework
```
Проверка:

```
kubectl apply -f service.yaml -f ingress.yaml

curl http://homework.otus/metrics.html
```

Либо деплой всей работы одной командой:
```
kubectl apply -f namespace.yaml -f serviceAccount.yaml -f clusterRole.yaml -f clusterRoleBinding.yaml -f roleBinding.yaml -f secret.yaml -f deployment.yaml -f service.yaml -f ingress.yaml

curl http://homework.otus/metrics.html
```
