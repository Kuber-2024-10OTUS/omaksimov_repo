# Репозиторий для выполнения домашних заданий курса "Инфраструктурная платформа на основе Kubernetes-2024-10" 

## Домашнее задание №12. Установка и использование CSI драйвера

Домашнее задание выполнено в `Managed Service for Kubernetes` в `Yandex Cloud`

```bash
kubectl get node

NAME                        STATUS   ROLES    AGE   VERSION
cl1g9c50r6l4ccs2reg5-eqod   Ready    <none>   85s   v1.29.1
```

1. Создан бакет в S3 object storage Yandex cloud.
```bash
yc storage bucket list  
+-------------------+----------------------+------------+-----------------------+---------------------+
|       NAME        |      FOLDER ID       |  MAX SIZE  | DEFAULT STORAGE CLASS |     CREATED AT      |
+-------------------+----------------------+------------+-----------------------+---------------------+
|    some-bucket    | -------------------- | 1073741824 | STANDARD              | 2025-02-03 18:09:58 |
+-------------------+----------------------+------------+-----------------------+---------------------+
```
2. Создан сервис аккаунт с правами `storage.editor` и статический ключ для него.
3. Создан [секрет](./secret.yaml) со статическим ключом и его id.
4. Создан [storageClass](./storageClass.yaml)
5. Из репозитория `yandex-cloud/k8s-csi-s3` установлен S3 CSI драйвер.
```bash
git clone https://github.com/yandex-cloud/k8s-csi-s3.git
```
```bash
kubectl apply -f secret.yaml && \
kubectl apply -f k8s-csi-s3/deploy/kubernetes/provisioner.yaml && \
kubectl apply -f k8s-csi-s3/deploy/kubernetes/driver.yaml && \
kubectl apply -f k8s-csi-s3/deploy/kubernetes/csi-s3.yaml && \
kubectl apply -f storageClass.yaml
```
6. Создан и применен манифест [persistentVolumeClaim](./pvc.yaml) с ранее созданным storageClass для динамического создания persistentVolume.
```bash
kubectl apply -f pvc.yaml
```
```bash
kubectl get pvc -n default csi-s3-pvc-dynamic  
NAME                 STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   VOLUMEATTRIBUTESCLASS   AGE
csi-s3-pvc-dynamic   Bound    pvc-0e8035ae-00ac-47ff-be7e-5e70c5dc3f70   100Mi      RWX            csi-s3         <unset>                 6m9s
```
```bash
s3cmd ls s3://some-bucket
DIR  s3://some-bucket/pvc-0e8035ae-00ac-47ff-be7e-5e70c5dc3f70/
```
7. Создан [манифест pod](./pod.yaml), использующий созданный PVC в качестве volume, смонтированного в `/mnt/s3`:
```bash
kubectl apply -f pod.yaml
```
```bash
kubectl exec -it csi-s3-test-alpine -- touch /mnt/s3/test.txt
```
```bash
s3cmd ls s3://some-bucket/pvc-0e8035ae-00ac-47ff-be7e-5e70c5dc3f70/
2025-02-03 19:29       DIROBJ  s3://some-bucket/pvc-0e8035ae-00ac-47ff-be7e-5e70c5dc3f70/
2025-02-03 19:52            0  s3://some-bucket/pvc-0e8035ae-00ac-47ff-be7e-5e70c5dc3f70/test.txt
```