# Репозиторий для выполнения домашних заданий курса "Инфраструктурная платформа на основе Kubernetes-2024-10" 

## Домашнее задание №6. Шаблонизация манифестов приложения, использование Helm. Установка community Helm charts.

Домашнее задание выполнено на `Linux fedora 6.11.7-300.fc41.x86_64`, `minikube v1.34.0 (docker)` с включенными аддонами default-storageclass, ingress, storage-provisioner.

Задание 1 (В директории `homework`).

Создан helm-chart для приложения из предыдущих домашних заданий.

- Имена объектов, контейнеров, используемые образы, хосты, порты, количество запускаемых реплик вынесены в параметры и задаются в [values.yaml](./homework/values.yaml)
- Репозиторий и тег образа задаются отдельными параметрами
- Пробы включаются параметром `nginx.containerProbes`
- В notes описано сообщение после установки релиза, отображающее адрес, по которому можно обратится к сервису
- Добавлен чарт-зависимость `bitnamicharts/postgresql`

Для проверки в директории `kubernetes-templating` необходимо выполнить команды:
```
helm dependencies update ./homework 
```
```
helm upgrade homework ./homework --install --namespace homework --create-namespace
```
```
Release "homework" does not exist. Installing it now.
NAME: homework
LAST DEPLOYED: Wed Dec  4 00:11:25 2024
NAMESPACE: homework
STATUS: deployed
REVISION: 1
TEST SUITE: None
NOTES:
You have successfully deployed "homework" helm chart!
Your release is named "homework".
You can now access deployed app here: http://homework.otus.
```

Задание 2 (В директории `kafka`)
- Создан файл [values-dev.yaml](./kafka/values-dev.yaml) для развертывания `kafka` из `bitnami` helm-чарта.
Для проверки в директории `kubernetes-templating/kafka` необходимо выполнить команду:
```
helm install kafka --namespace dev --create-namespace oci://registry-1.docker.io/bitnamicharts/kafka --version 31.0.0 -f values-dev.yaml
```
- Создан файл [values-prod.yaml](./kafka/values-prod.yaml) для развертывания `kafka` из `bitnami` helm-чарта.
Для проверки в директории `kubernetes-templating/kafka` необходимо выполнить команду:
```
helm install kafka --namespace prod --create-namespace oci://registry-1.docker.io/bitnamicharts/kafka --version 31.0.0 -f values-prod.yaml
```
- Создан [helmfile.yaml](./kafka/helmfile.yaml) для развертывания `kafka` из `bitnami` в `dev` и `prod` неймспейсы.
Для проверки в директории `kubernetes-templating/kafka` необходимо выполнить команды:
```
helmfile init
```
```
helmfile apply
```
```
Listing releases matching ^kafka$
kafka   dev             1               2024-12-04 00:31:40.127900941 +0300 MSK deployed        kafka-31.0.0    3.9.0      

kafka   prod            1               2024-12-04 00:31:40.127656462 +0300 MSK deployed        kafka-31.0.0    3.9.0      


UPDATED RELEASES:
NAME    NAMESPACE   CHART                 VERSION   DURATION
kafka   dev         bitnamicharts/kafka   31.0.0          1s
kafka   prod        bitnamicharts/kafka   31.0.0          1s
```