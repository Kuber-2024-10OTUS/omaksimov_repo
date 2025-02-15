# Репозиторий для выполнения домашних заданий курса "Инфраструктурная платформа на основе Kubernetes-2024-10" 

## Домашнее задание №10. GitOps и инструменты поставки

Домашнее задание выполнено в `Managed Service for Kubernetes` в `Yandex Cloud`

```bash
kubectl get nodes
```
```
NAME                        STATUS   ROLES    AGE   VERSION
cl19a69v6tc451r51sh9-atul   Ready    <none>   12m   v1.30.1
cl19a69v6tc451r51sh9-ijeq   Ready    <none>   12m   v1.30.1
```

1. Создано 2 пула по 1 ноде:

 - для рабочей нагрузки
 - для инфраструктурных сервисов с `taint` `node-role=infra:NoSchedule` и `label` `node-role=infra`

```bash
kubectl label nodes cl19a69v6tc451r51sh9-atul node-role=infra
```
```bash
kubectl taint nodes cl19a69v6tc451r51sh9-atul node-role=infra:NoSchedule
```
```bash
kubectl get node -o wide --show-labels
```
```
NAME                        STATUS   ROLES    AGE   VERSION   INTERNAL-IP   EXTERNAL-IP       OS-IMAGE             KERNEL-VERSION      CONTAINER-RUNTIME     LABELS
cl19a69v6tc451r51sh9-atul   Ready    <none>   14m   v1.30.1   10.131.0.29   158.160.162.136   Ubuntu 20.04.6 LTS   5.4.0-196-generic   containerd://1.6.28   beta.kubernetes.io/arch=amd64,beta.kubernetes.io/instance-type=standard-v3,beta.kubernetes.io/os=linux,failure-domain.beta.kubernetes.io/zone=ru-central1-d,kubernetes.io/arch=amd64,kubernetes.io/hostname=cl19a69v6tc451r51sh9-atul,kubernetes.io/os=linux,node-role=infra,node.kubernetes.io/instance-type=standard-v3,node.kubernetes.io/kube-proxy-ds-ready=true,node.kubernetes.io/masq-agent-ds-ready=true,node.kubernetes.io/node-problem-detector-ds-ready=true,topology.kubernetes.io/zone=ru-central1-d,yandex.cloud/node-group-id=cat7go1n43p5g9jqad8r,yandex.cloud/pci-topology=k8s,yandex.cloud/preemptible=true
cl19a69v6tc451r51sh9-ijeq   Ready    <none>   14m   v1.30.1   10.131.0.33   158.160.132.27    Ubuntu 20.04.6 LTS   5.4.0-196-generic   containerd://1.6.28   beta.kubernetes.io/arch=amd64,beta.kubernetes.io/instance-type=standard-v3,beta.kubernetes.io/os=linux,failure-domain.beta.kubernetes.io/zone=ru-central1-d,kubernetes.io/arch=amd64,kubernetes.io/hostname=cl19a69v6tc451r51sh9-ijeq,kubernetes.io/os=linux,node.kubernetes.io/instance-type=standard-v3,node.kubernetes.io/kube-proxy-ds-ready=true,node.kubernetes.io/masq-agent-ds-ready=true,node.kubernetes.io/node-problem-detector-ds-ready=true,topology.kubernetes.io/zone=ru-central1-d,yandex.cloud/node-group-id=cat7go1n43p5g9jqad8r,yandex.cloud/pci-topology=k8s,yandex.cloud/preemptible=true
```
```bash
kubectl get nodes -o custom-columns=NAME:.metadata.name,TAINTS:.spec.taints
```
```
NAME                        TAINTS
cl19a69v6tc451r51sh9-atul   [map[effect:NoSchedule key:node-role value:infra]]
cl19a69v6tc451r51sh9-ijeq   <none>
```
2. В кластер установлен `Argo CD`:
```bash
helm repo add argo https://argoproj.github.io/argo-helm
```
```bash
helm repo update
```
```bash
helm upgrade argocd --install --namespace argocd --create-namespace argo/argo-cd --version 7.8.2 --values values-argocd.yaml
```
[values-argocd.yaml](./values-argocd.yaml)

3. В конфигмап `argocd-cm` добавлен пользователь `homework10`:
```bash
kubectl patch -n argocd cm argocd-cm --type=merge -p '{"data":{"accounts.homework10":"login"}}'
```
```bash
kubectl port-forward svc/argocd-server -n argocd 8080:443
```
```bash
argocd admin initial-password -n argocd
```
```bash
argocd login 127.0.0.1:8080 --username admin
```
```bash
argocd account update-password \
  --account homework10 \
  --current-password <current-admin-password> \
  --new-password <new-user-password>
```
```bash
argocd logout 127.0.0.1:8080
```
4. Создан ресурс `AppProject` [otus](./project.yaml) в неймспейсе `argocd`, в котором в качестве `sourceRepo` указан репозиторий курса с домашними заданиями, а `destinations` - неймспейсы `homework` и `homeworkhelm`:
```bash
kubectl apply -f project.yaml
```
5. Создан ресурс `Application` [kubernetes-networks](./app-networks.yaml) c `syncPolicy: manual` в неймспейсе `argocd` для развертывания манифестов из ветки `kubernetes-networks` репозитория с домашними заданиями в неймспейсе `homework`:
```bash
kubectl apply -f app-networks.yaml
```
6. Создан ресурс `Application` [kubernetes-templating](./app-templating.yaml) c `syncPolicy: automated` в неймспейсе `argocd` для развертывания хелм чарта из ветки `kubernetes-templating` репозитория с домашними заданиями в неймспейсе `homeworkhelm`:
```bash
kubectl apply -f app-templating.yaml
```
7. Applications были созданы в кластере:
```bash
argocd login 127.0.0.1:8080 --username homework10
```
```bash
argocd app list                               
NAME                          CLUSTER                         NAMESPACE     PROJECT  STATUS     HEALTH       SYNCPOLICY  CONDITIONS  REPO                                                     PATH                            TARGET
argocd/kubernetes-networks    https://kubernetes.default.svc  homework      otus     OutOfSync  Missing      Manual      <none>      https://github.com/Kuber-2024-10OTUS/omaksimov_repo.git  kubernetes-networks             kubernetes-networks
argocd/kubernetes-templating  https://kubernetes.default.svc  homeworkhelm  otus     Synced     Progressing  Auto-Prune  <none>      https://github.com/Kuber-2024-10OTUS/omaksimov_repo.git  kubernetes-templating/homework  kubernetes-templating
```
Application `argocd/kubernetes-templating` был развернут автоматически из-за `syncPolicy: automated`.

Application `argocd/kubernetes-networks` развернут вручную:
```bash
argocd app sync argocd/kubernetes-networks
```
```bash
argocd app list                                          
NAME                          CLUSTER                         NAMESPACE     PROJECT  STATUS  HEALTH   SYNCPOLICY  CONDITIONS  REPO                                                     PATH                            TARGET
argocd/kubernetes-networks    https://kubernetes.default.svc  homework      otus     Synced  Healthy  Manual      <none>      https://github.com/Kuber-2024-10OTUS/omaksimov_repo.git  kubernetes-networks             kubernetes-networks
argocd/kubernetes-templating  https://kubernetes.default.svc  homeworkhelm  otus     Synced  Healthy  Auto-Prune  <none>      https://github.com/Kuber-2024-10OTUS/omaksimov_repo.git  kubernetes-templating/homework  kubernetes-templating
```