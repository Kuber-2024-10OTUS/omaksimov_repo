:# Репозиторий для выполнения домашних заданий курса "Инфраструктурная платформа на основе Kubernetes-2024-10" 

## Домашнее задание №7. Создание собственного CRD

Домашнее задание выполнено на `Linux fedora 6.11.7-300.fc41.x86_64`, `minikube v1.34.0 (docker)` с включенными аддонами default-storageclass, storage-provisioner.

1. Создан манифест объекта [CustomResourceDefinition](./CustomResourceDefinition.yaml) для создания custom resource'ов типа MySQL, с обязательными полями `Image`, `Database`, `Password`, `Storage_size` и правилами из валидации.
2. Созданы манифесты, описывающие:
- [Namespace](./Namespace.yaml) `mysql-operator`;
- [ServiceAccount](./ServiceAccount.yaml), [ClusterRole](./ClusterRole.yaml) и [ClusterRoleBinding](./ClusterRoleBinding.yaml) для полного доступа сервис аккаунта `mysql-operator-api-full-access` из неймспейса `mysql-operator` к api серверу;
3. Создан манифест [Deployment](./Deployment.yaml) для развертывания оператора `mysql-operator`, работающего от сервис аккаунта `mysql-operator-api-full-access`, в неймспейсе `mysql-operator`;
4. Создан [манифест](./CustomResource.yaml) кастомного объекта типа MySQL в неймспейсе `default`;
5. После применения манифестов:
```
kubectl apply -f Namespace.yaml -f ServiceAccount.yaml -f ClusterRole.yaml -f ClusterRoleBinding.yaml -f CustomResourceDefinition.yaml -f Deployment.yaml
```
В неймспейсе `mysql-operator` создается deployment `homework-mysql-operator` с образом `roflmaoinmysoul/mysql-operator:1.0.0`.

После применения манифеста `CustomResource.yaml`:
```
kubectl apply -f CustomResource.yaml
```
В неймспейсе `default` создается кастомный ресурс типа MySQL `mysql-custom-resource`, при его создании оператором создаются ресурсы: deployment, service, pvc, pv с параметрами из кастомного ресурса `mysql-custom-resource`.

```
kubectl get deploy 
NAME                    READY   UP-TO-DATE   AVAILABLE   AGE
mysql-custom-resource   1/1     1            1           56m
```
```
kubectl get svc   
NAME                    TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)    AGE
kubernetes              ClusterIP   10.96.0.1    <none>        443/TCP    71m
mysql-custom-resource   ClusterIP   None         <none>        3306/TCP   56m
```
```
kubectl get pvc
NAME                        STATUS   VOLUME                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
mysql-custom-resource-pvc   Bound    mysql-custom-resource-pv   150Mi      RWO            standard       <unset>                 57m
```
```
kubectl get pv 
NAME                       CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS   CLAIM                               STORAGECLASS   VOLUMEATTRIBUTESCLASS   REASON   AGE
mysql-custom-resource-pv   150Mi      RWO            Retain           Bound    default/mysql-custom-resource-pvc   standard       <unset>                          57m
```
```
mysql> SHOW DATABASES;
+--------------------+
| Database           |
+--------------------+
| homework-db        |
| information_schema |
| mysql              |
| performance_schema |
| sys                |
+--------------------+
5 rows in set (0.00 sec)
```
При удалении объекта типа MySQL удаляются все созданные для него ресурсы.
```
kubectl delete msl mysql-custom-resource
mysql.otus.homework "mysql-custom-resource" deleted
```
```
kubectl get deploy                      
No resources found in default namespace.
kubectl get svc                         
NAME         TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)   AGE
kubernetes   ClusterIP   10.96.0.1    <none>        443/TCP   81m
kubectl get pvc                         
No resources found in default namespace.
kubectl get pv                          
No resources found
```