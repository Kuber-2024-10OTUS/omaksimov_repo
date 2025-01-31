# Репозиторий для выполнения домашних заданий курса "Инфраструктурная платформа на основе Kubernetes-2024-10" 

## Домашнее задание №11. Хранилище секретов для приложения. Vault.

Домашнее задание выполнено в `Managed Service for Kubernetes` в `Yandex Cloud`

```bash
kubectl get node

NAME                        STATUS   ROLES    AGE    VERSION
cl1euvf7vkksrequpdfh-efif   Ready    <none>   5m5s   v1.29.1
cl1euvf7vkksrequpdfh-ixaq   Ready    <none>   5m8s   v1.29.1
cl1euvf7vkksrequpdfh-ywid   Ready    <none>   5m8s   v1.29.1
```


1. Из хелм чарта установлен `consul` в неймспейс `consul` кластера:
```bash
wget https://github.com/hashicorp/consul-k8s/archive/refs/tags/v1.1.18.tar.gz
```
```bash
tar xzvf v1.1.18.tar.gz
```
```bash
helm upgrade consul --install --namespace consul --create-namespace --values ./values-consul.yaml ./consul-k8s-1.1.18/charts/consul
```
[Values файл values-consul.yaml](./values-consul.yaml)

2. Из хелм чарта установлен `vault` в неймспейс `vault` в кластера:
```bash
wget https://github.com/hashicorp/vault-helm/archive/refs/tags/v0.29.1.tar.gz
```
```bash
tar xzvf v0.29.1.tar.gz
```
```bash
helm upgrade vault --install --namespace vault --create-namespace --values ./values-vault.yaml ./vault-helm-0.29.1
```
[Values файл values-vault.yaml](./values-vault.yaml)

3. Хранилище инициализировано:
```bash
vault operator init -key-shares=1 -key-threshold=1
```
Ноды кластера vault распечатаны:
```bash
vault operator unseal <key>
```
```bash
vault login <token>
```
4. Включен secret engine `kv-v2` по префиксу пути `otus`
```bash
vault secrets enable -path=otus kv-v2
```
В нем создан секрет `otus/cred`:
```bash
vault kv put otus/cred username='otus' password='asajkjkahs'
```
```
/ $ vault kv get otus/cred
= Secret Path =
otus/data/cred

======= Metadata =======
Key                Value
---                -----
created_time       2025-01-30T20:11:51.79675056Z
custom_metadata    <nil>
deletion_time      n/a
destroyed          false
version            1

====== Data ======
Key         Value
---         -----
password    asajkjkahs
username    otus
```
5. В неймспейсе `vault` создан [сервис аккаунт vault-auth](./serviceAccount.yaml) и [ClusterRoleBinding](./ClusterRoleBinding.yaml) к роли `system:auth-delegator`.
```bash
kubectl apply -f serviceAccount.yaml -f ClusterRoleBinding.yaml
```
6. В кластере `vault` включена и настроена авторизация `auth/kubernetes`:
```bash
kubectl get secret/vault-auth-secret -n vault -o json | jq -r .data.token | base64 -d > ./token
```
<!-- ```bash
kubectl get secret/vault-auth-secret -n vault -o json | jq -r '.data."ca.crt"' | base64 -d > ./cert
``` -->
```bash
vault auth enable kubernetes
```
```bash
vault write auth/kubernetes/config \
    token_reviewer_jwt="<токен сервис аккаунта>" \
    kubernetes_host=https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_SERVICE_PORT \
    kubernetes_ca_cert=@/var/run/secrets/kubernetes.io/serviceaccount/ca.crt
```
7. Создана и применена [политика](./otus-policy.hcl) для просмотра созданных ранее секретов:
```bash
vault policy write otus-policy - <<EOF
path "otus/data/cred" {
   capabilities = ["read", "list"]
}
EOF
```
8. Создана роль `auth/kubernetes/role/otus`:
```bash
vault write auth/kubernetes/role/otus \
    bound_service_account_names=vault-auth \
    bound_service_account_namespaces=vault \
    policies=otus-policy \
    ttl=1h
```
9. Установлен `External Secrets Operator`:
```bash
helm repo add external-secrets https://charts.external-secrets.io
```
```bash
helm repo update external-secrets
```
```bash
helm install external-secrets external-secrets/external-secrets -n vault
```
10. Создан и применен манифест [SecretStore](./SecretStore.yaml):
```bash
kubectl apply -f SecretStore.yaml
```
11. Создан и применен манифест [ExternalSecret](./ExternalSecret.yaml)
```bash
kubectl apply -f ExternalSecret.yaml
```
12. В namespace `vault` был создан secret `otus-cred` с данными, ранее сохраненными в Hashicorp Vault:
```bash
kubectl get secret -n vault otus-cred
```
```
NAME        TYPE     DATA   AGE
otus-cred   Opaque   2      18s
```
```bash
kubectl get secret -n vault otus-cred -o json | jq .data
```
```
{
  "password": "YXNhamtqa2Focw==",
  "username": "b3R1cw=="
}
```
```bash
kubectl get secret -n vault otus-cred -o json | jq -r .data.password | base64 -d
```
```
asajkjkahs%
```
```bash
kubectl get secret -n vault otus-cred -o json | jq -r .data.username | base64 -d
```
```
otus%
```