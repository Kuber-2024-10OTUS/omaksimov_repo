# Репозиторий для выполнения домашних заданий курса "Инфраструктурная платформа на основе Kubernetes-2024-10" 

## Домашнее задание №14. Подходы к развертыванию и обновлению production-grade кластера

Домашнее задание выполнено в `Yandex Cloud`

1. Созданы 4 ВМ: 1 для master ноды, 3 для worker нод, а также бастион для доступа к ВМ кластера извне.
```bash
yc compute instance list
+----------------------+---------------------------+---------------+---------+-----------------+--------------+
|          ID          |           NAME            |    ZONE ID    | STATUS  |   EXTERNAL IP   | INTERNAL IP  |
+----------------------+---------------------------+---------------+---------+-----------------+--------------+
| -------------------- | cl1h6cabtcgniaco0v2f-oxax | ru-central1-b | RUNNING |                 | 10.233.20.20 |
| -------------------- | cl1h6cabtcgniaco0v2f-iciw | ru-central1-a | RUNNING |                 | 10.233.10.27 |
| -------------------- | k8s-cluster-bastion       | ru-central1-d | RUNNING |   <bastion_ip>  | 10.233.30.14 |
| -------------------- | cl1h6cabtcgniaco0v2f-yjyt | ru-central1-d | RUNNING |                 | 10.233.30.25 |
| -------------------- | cl1qmi9t2f6shckef2k0-ehic | ru-central1-d | RUNNING |                 | 10.233.30.13 |
+----------------------+---------------------------+---------------+---------+-----------------+--------------+

```
2. На ВМ выполнены подготовительные операции:
 - Отключен swap:
```bash
sudo sed -i '/ swap / s/^/#/' /etc/fstab
```
```bash
swapon -s
```
  - Разрешена маршрутизации между интерфейсами
```bash
echo -e "net.ipv4.ip_forward = 1" > /etc/sysctl.d/10-k8s.conf
```
```bash
sysctl -f /etc/sysctl.d/10-k8s.conf
```
```bash
sysctl net.ipv4.ip_forward
```
  - Настроена автозагрузка и запуск модулей ядра br_netfilter и overlay
```bash
printf "%s\n" "overlay" "br_netfilter" > /etc/modules-load.d/k8s.conf
```
```bash
lsmod | grep -i -E 'br_netfilter|overlay'
```
3. Установлены kubeadm, kubelet, kubect и container runtime для создания кластера kubernetes версии `1.31`

Установка `containerd`:
```bash
sudo apt-get update
```
```bash
sudo apt-get install -y apt-transport-https ca-certificates curl gpg
```
```bash
sudo install -m 0755 -d /etc/apt/keyrings
```
```bash
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
```
```bash
sudo chmod a+r /etc/apt/keyrings/docker.asc
```
```bash
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```
```bash
sudo apt-get update && sudo apt-get install containerd.io
```
```bash
mkdir /etc/containerd/
```
```bash
containerd config default > /etc/containerd/config.toml
```
```bash
sed -i 's/SystemdCgroup \= false/SystemdCgroup \= true/g' /etc/containerd/config.toml
```
```bash
sudo systemctl restart containerd
```
Установка `kubeadm`, `kubelet`, `kubectl`:
```bash
curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.31/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
```
```bash
echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.31/deb/ /' | sudo tee /etc/apt/sources.list.d/kubernetes.list
```
```bash
sudo apt-get update
```
```bash
sudo apt-get install -y kubelet kubeadm kubectl
```
```bash
sudo apt-mark hold kubelet kubeadm kubectl
```
```bash
sudo systemctl enable --now kubelet
```
4. На master ноде выполнен `kubeadm init`
```bash
sudo kubeadm init --pod-network-cidr 10.244.0.0/16
```
```bash
mkdir -p $HOME/.kube && \ 
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config && \
sudo chown $(id -u)\:$(id -g) $HOME/.kube/config
```
5. Установлен сетевой плагин `flannel`
```bash
kubectl create -f https://github.com/flannel-io/flannel/releases/latest/download/kube-flannel.yml
```
6. Worker ноды подключены к master ноде:
```bash
sudo kubeadm join 10.233.30.13:6443 --token <token> \
	--discovery-token-ca-cert-hash <cert_hash>
```
```bash
kubectl get nodes -o wide
NAME                        STATUS   ROLES           AGE     VERSION   INTERNAL-IP    EXTERNAL-IP   OS-IMAGE             KERNEL-VERSION     CONTAINER-RUNTIME
cl1h6cabtcgniaco0v2f-iciw   Ready    <none>          2m39s   v1.31.6   10.233.10.27   <none>        Ubuntu 24.04.1 LTS   6.8.0-50-generic   containerd://1.7.25
cl1h6cabtcgniaco0v2f-oxax   Ready    <none>          2m53s   v1.31.6   10.233.20.20   <none>        Ubuntu 24.04.1 LTS   6.8.0-50-generic   containerd://1.7.25
cl1h6cabtcgniaco0v2f-yjyt   Ready    <none>          2m34s   v1.31.6   10.233.30.25   <none>        Ubuntu 24.04.1 LTS   6.8.0-50-generic   containerd://1.7.25
cl1qmi9t2f6shckef2k0-ehic   Ready    control-plane   5m26s   v1.31.6   10.233.30.13   <none>        Ubuntu 24.04.1 LTS   6.8.0-50-generic   containerd://1.7.25
```
7. Выполнено обновление кластера до версии `1.32`
- На нодах кластера изменен репозиторий компонентов kubernetes на репозиторий версии компонентов `1.32`:
```bash
sudo sed -i 's/v1.31/v1.32/g' /etc/apt/sources.list.d/kubernetes.list
```
- Выбрана последняя патч версия kubeadm `1.32.2-1.1`:
```bash
sudo apt update && \
sudo apt-cache madison kubeadm
```
- Обновлена master нода `cl1qmi9t2f6shckef2k0-ehic`:
```bash
sudo apt-mark unhold kubeadm && \
sudo apt-get update && sudo apt-get install -y kubeadm='1.32.2-1.1' && \
sudo apt-mark hold kubeadm
```
```bash
kubeadm version

kubeadm version: &version.Info{Major:"1", Minor:"32", GitVersion:"v1.32.2", GitCommit:"67a30c0adcf52bd3f56ff0893ce19966be12991f", GitTreeState:"clean", BuildDate:"2025-02-12T21:24:52Z", GoVersion:"go1.23.6", Compiler:"gc", Platform:"linux/amd64"}
```
```bash
sudo kubeadm upgrade plan
```
```bash
sudo kubeadm upgrade apply v1.32.2
...
[upgrade] SUCCESS! A control plane node of your cluster was upgraded to "v1.32.2".
...
```
```bash
kubectl drain cl1qmi9t2f6shckef2k0-ehic --ignore-daemonsets
```
```bash
sudo apt-mark unhold kubelet kubectl && \
sudo apt-get update && sudo apt-get install -y kubelet='1.32.2-1.1' kubectl='1.32.2-1.1' && \
sudo apt-mark hold kubelet kubectl
```
```bash
sudo systemctl daemon-reload && \
sudo systemctl restart kubelet
```
```bash
kubectl uncordon cl1qmi9t2f6shckef2k0-ehic
```
- Обновлeны worker ноды `cl1h6cabtcgniaco0v2f-{iciw,oxax,yjyt}` (по одной):
```bash
sudo apt-mark unhold kubeadm && \
sudo apt-get update && sudo apt-get install -y kubeadm='1.32.2-1.1' && \
sudo apt-mark hold kubeadm
```
```bash
sudo kubeadm upgrade node
...
[upgrade] Backing up kubelet config file to /etc/kubernetes/tmp/kubeadm-kubelet-config3816334993/config.yaml
[kubelet-start] Writing kubelet configuration to file "/var/lib/kubelet/config.yaml"
[upgrade/kubelet-config] The kubelet configuration for this node was successfully upgraded!
...
```
```bash
kubectl drain cl1h6cabtcgniaco0v2f-{iciw,oxax,yjyt} --ignore-daemonsets
```
```bash
sudo apt-mark unhold kubelet kubectl && \
sudo apt-get update && sudo apt-get install -y kubelet='1.32.2-1.1' kubectl='1.32.2-1.1' && \
sudo apt-mark hold kubelet kubectl
```
```bash
sudo systemctl daemon-reload && \
sudo systemctl restart kubelet
```
```bash
kubectl uncordon cl1h6cabtcgniaco0v2f-{iciw,oxax,yjyt}
```
```bash
kubectl get nodes -o wide
NAME                        STATUS   ROLES           AGE    VERSION   INTERNAL-IP    EXTERNAL-IP   OS-IMAGE             KERNEL-VERSION     CONTAINER-RUNTIME
cl1h6cabtcgniaco0v2f-iciw   Ready    <none>          122m   v1.32.2   10.233.10.27   <none>        Ubuntu 24.04.1 LTS   6.8.0-50-generic   containerd://1.7.25
cl1h6cabtcgniaco0v2f-oxax   Ready    <none>          122m   v1.32.2   10.233.20.20   <none>        Ubuntu 24.04.1 LTS   6.8.0-50-generic   containerd://1.7.25
cl1h6cabtcgniaco0v2f-yjyt   Ready    <none>          122m   v1.32.2   10.233.30.25   <none>        Ubuntu 24.04.1 LTS   6.8.0-50-generic   containerd://1.7.25
cl1qmi9t2f6shckef2k0-ehic   Ready    control-plane   124m   v1.32.2   10.233.30.13   <none>        Ubuntu 24.04.1 LTS   6.8.0-50-generic   containerd://1.7.25
```
8. Для задания со * развернут HA кластер из 3-х master и 2-х worker нод с помощью `kubespray` c `nginx-proxy` на `worker` нодах для балансировки запросов к `master` нодам. Для доступа к ВМ извне также использовался бастион. `kubespray` также разворачивает `metrics-server` и `ingress controller` на `worker` нодах.
```bash
yc compute instance list
+----------------------+---------------------------+---------------+---------+----------------+--------------+
|          ID          |           NAME            |    ZONE ID    | STATUS  |  EXTERNAL IP   | INTERNAL IP  |
+----------------------+---------------------------+---------------+---------+----------------+--------------+
| -------------------- | cl18955bhe76unpgifc1-ynyf | ru-central1-b | RUNNING |                | 10.233.20.13 |
| -------------------- | cl16emmkbsrhh8v1cflm-ogar | ru-central1-b | RUNNING |                | 10.233.20.3  |
| -------------------- | cl16emmkbsrhh8v1cflm-utem | ru-central1-a | RUNNING |                | 10.233.10.3  |
| -------------------- | k8s-cluster-bastion       | ru-central1-d | RUNNING |  <bastion_ip>  | 10.233.30.16 |
| -------------------- | cl18955bhe76unpgifc1-ecok | ru-central1-d | RUNNING |                | 10.233.30.4  |
| -------------------- | cl16emmkbsrhh8v1cflm-ikex | ru-central1-d | RUNNING |                | 10.233.30.15 |
+----------------------+---------------------------+---------------+---------+----------------+--------------+
```
```bash
git clone https://github.com/kubernetes-sigs/kubespray.git
```
```bash
cd kubespray
```
```bash
source .venv/bin/activate
```
```bash
pip install -r requirements.txt
```
```bash
cp -r inventory/sample inventory/k8s-cluster
```
```bash
ansible-playbook -i ./inventory/k8s-cluster/inventory.ini -e @./inventory/k8s-cluster/extra_vars.yml cluster.yml -b
```
[Inventory](./ansible/inventory.ini) и [extra_vars](./ansible/extra_vars.yml) в директории `kubernetes-prod/ansible` репозитория. 
```bash
kubectl get nodes -o wide
NAME      STATUS   ROLES           AGE   VERSION   INTERNAL-IP    EXTERNAL-IP   OS-IMAGE             KERNEL-VERSION     CONTAINER-RUNTIME
master1   Ready    control-plane   95m   v1.32.2   10.233.20.3    <none>        Ubuntu 24.04.1 LTS   6.8.0-50-generic   containerd://2.0.3
master2   Ready    control-plane   94m   v1.32.2   10.233.10.3    <none>        Ubuntu 24.04.1 LTS   6.8.0-50-generic   containerd://2.0.3
master3   Ready    control-plane   94m   v1.32.2   10.233.30.15   <none>        Ubuntu 24.04.1 LTS   6.8.0-50-generic   containerd://2.0.3
worker1   Ready    <none>          93m   v1.32.2   10.233.20.13   <none>        Ubuntu 24.04.1 LTS   6.8.0-50-generic   containerd://2.0.3
worker2   Ready    <none>          93m   v1.32.2   10.233.30.4    <none>        Ubuntu 24.04.1 LTS   6.8.0-50-generic   containerd://2.0.3
```