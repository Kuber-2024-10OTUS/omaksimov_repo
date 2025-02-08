# Репозиторий для выполнения домашних заданий курса "Инфраструктурная платформа на основе Kubernetes-2024-10"

## Домашнее задание №13. Диагностика и отладка в Kubernetes

Домашнее задание выполнено на `Linux fedora 6.12.10-200.fc41.x86_64`, `minikube v1.34.0 (docker)` с включенными аддонами default-storageclass, ingress, storage-provisioner.

1. Создан [манифест пода](./pod.yaml), создающий под с контейнером из образа `kyos0109/nginx-distroless` в неймспейсе `default`:
```bash
kubectl apply -f pod.yaml
```
2. Создан эфемерный отладочный контейнер c доступом к пространству имен PID основного контейнера пода:
```bash
kubectl debug nginx -it --image=alpine:latest --target=nginx
```
```
Targeting container "nginx". If you don't see processes from this container it may be because the container runtime doesn't support this feature.
Defaulting debug container name to debugger-6kq8s.
If you don't see a command prompt, try pressing enter.
/ # ps
PID   USER     TIME  COMMAND
    1 root      0:00 nginx: master process nginx -g daemon off;
    7 101       0:00 nginx: worker process
    8 root      0:00 /bin/sh
   14 root      0:00 ps
```
3. Отладочный контейнер имеет доступ к файловой системе основного контейнера  через симлинк на корневую директорию процесса основного контейнера `/proc/1/root`:
```
/ # ls -la /proc/1/root/etc/nginx/
total 40
drwxr-xr-x    1 root     root           182 Oct  5  2020 .
drwxr-xr-x    1 root     root            56 Feb  1 16:47 ..
drwxr-xr-x    1 root     root            24 Oct  5  2020 conf.d
-rw-r--r--    1 root     root          1007 Apr 21  2020 fastcgi_params
-rw-r--r--    1 root     root          2837 Apr 21  2020 koi-utf
-rw-r--r--    1 root     root          2223 Apr 21  2020 koi-win
-rw-r--r--    1 root     root          5231 Apr 21  2020 mime.types
lrwxrwxrwx    1 root     root            22 Apr 21  2020 modules -> /usr/lib/nginx/modules
-rw-r--r--    1 root     root           643 Apr 21  2020 nginx.conf
-rw-r--r--    1 root     root           636 Apr 21  2020 scgi_params
-rw-r--r--    1 root     root           664 Apr 21  2020 uwsgi_params
-rw-r--r--    1 root     root          3610 Apr 21  2020 win-utf
```
4. В отладочном контейнере запущен `tcpdump`, выполнены сетевые обращения к `nginx`:
```bash
apk add tcpdump
```
```bash
kubectl port-forward pod/nginx 8080:80
```
```bash
tcpdump -nn -i any -e port 80
```
```bash
curl 127.0.0.1:8080
```
```
tcpdump: WARNING: any: That device doesn't support promiscuous mode
(Promiscuous mode not supported on the "any" device)
tcpdump: verbose output suppressed, use -v[v]... for full protocol decode
listening on any, link-type LINUX_SLL2 (Linux cooked v2), snapshot length 262144 bytes
16:50:04.656540 lo    In  ifindex 1 00:00:00:00:00:00 ethertype IPv4 (0x0800), length 80: 127.0.0.1.60158 > 127.0.0.1.80: Flags [S], seq 4024524898, win 65495, options [mss 65495,sackOK,TS val 3457367752 ecr 0,nop,wscale 7], length 0
16:50:04.656550 lo    In  ifindex 1 00:00:00:00:00:00 ethertype IPv4 (0x0800), length 80: 127.0.0.1.80 > 127.0.0.1.60158: Flags [S.], seq 791456190, ack 4024524899, win 65483, options [mss 65495,sackOK,TS val 3457367752 ecr 3457367752,nop,wscale 7], length 0
16:50:04.656558 lo    In  ifindex 1 00:00:00:00:00:00 ethertype IPv4 (0x0800), length 72: 127.0.0.1.60158 > 127.0.0.1.80: Flags [.], ack 1, win 512, options [nop,nop,TS val 3457367752 ecr 3457367752], length 0
16:50:04.656593 lo    In  ifindex 1 00:00:00:00:00:00 ethertype IPv4 (0x0800), length 149: 127.0.0.1.60158 > 127.0.0.1.80: Flags [P.], seq 1:78, ack 1, win 512, options [nop,nop,TS val 3457367752 ecr 3457367752], length 77: HTTP: GET / HTTP/1.1
16:50:04.656598 lo    In  ifindex 1 00:00:00:00:00:00 ethertype IPv4 (0x0800), length 72: 127.0.0.1.80 > 127.0.0.1.60158: Flags [.], ack 78, win 511, options [nop,nop,TS val 3457367752 ecr 3457367752], length 0
16:50:04.656850 lo    In  ifindex 1 00:00:00:00:00:00 ethertype IPv4 (0x0800), length 310: 127.0.0.1.80 > 127.0.0.1.60158: Flags [P.], seq 1:239, ack 78, win 512, options [nop,nop,TS val 3457367752 ecr 3457367752], length 238: HTTP: HTTP/1.1 200 OK
16:50:04.656860 lo    In  ifindex 1 00:00:00:00:00:00 ethertype IPv4 (0x0800), length 72: 127.0.0.1.60158 > 127.0.0.1.80: Flags [.], ack 239, win 511, options [nop,nop,TS val 3457367752 ecr 3457367752], length 0
16:50:04.656896 lo    In  ifindex 1 00:00:00:00:00:00 ethertype IPv4 (0x0800), length 684: 127.0.0.1.80 > 127.0.0.1.60158: Flags [P.], seq 239:851, ack 78, win 512, options [nop,nop,TS val 3457367752 ecr 3457367752], length 612: HTTP
16:50:04.656903 lo    In  ifindex 1 00:00:00:00:00:00 ethertype IPv4 (0x0800), length 72: 127.0.0.1.60158 > 127.0.0.1.80: Flags [.], ack 851, win 507, options [nop,nop,TS val 3457367752 ecr 3457367752], length 0
16:50:04.657540 lo    In  ifindex 1 00:00:00:00:00:00 ethertype IPv4 (0x0800), length 72: 127.0.0.1.60158 > 127.0.0.1.80: Flags [F.], seq 78, ack 851, win 507, options [nop,nop,TS val 3457367753 ecr 3457367752], length 0
16:50:04.657583 lo    In  ifindex 1 00:00:00:00:00:00 ethertype IPv4 (0x0800), length 72: 127.0.0.1.80 > 127.0.0.1.60158: Flags [F.], seq 851, ack 79, win 512, options [nop,nop,TS val 3457367753 ecr 3457367753], length 0
16:50:04.657594 lo    In  ifindex 1 00:00:00:00:00:00 ethertype IPv4 (0x0800), length 72: 127.0.0.1.60158 > 127.0.0.1.80: Flags [.], ack 852, win 507, options [nop,nop,TS val 3457367753 ecr 3457367753], length 0
16:50:44.206965 lo    In  ifindex 1 00:00:00:00:00:00 ethertype IPv4 (0x0800), length 80: 127.0.0.1.33700 > 127.0.0.1.80: Flags [S], seq 1099162134, win 65495, options [mss 65495,sackOK,TS val 3457407303 ecr 0,nop,wscale 7], length 0
16:50:44.206976 lo    In  ifindex 1 00:00:00:00:00:00 ethertype IPv4 (0x0800), length 80: 127.0.0.1.80 > 127.0.0.1.33700: Flags [S.], seq 3985766476, ack 1099162135, win 65483, options [mss 65495,sackOK,TS val 3457407303 ecr 3457407303,nop,wscale 7], length 0
16:50:44.206985 lo    In  ifindex 1 00:00:00:00:00:00 ethertype IPv4 (0x0800), length 72: 127.0.0.1.33700 > 127.0.0.1.80: Flags [.], ack 1, win 512, options [nop,nop,TS val 3457407303 ecr 3457407303], length 0
16:50:44.207024 lo    In  ifindex 1 00:00:00:00:00:00 ethertype IPv4 (0x0800), length 149: 127.0.0.1.33700 > 127.0.0.1.80: Flags [P.], seq 1:78, ack 1, win 512, options [nop,nop,TS val 3457407303 ecr 3457407303], length 77: HTTP: GET / HTTP/1.1
16:50:44.207029 lo    In  ifindex 1 00:00:00:00:00:00 ethertype IPv4 (0x0800), length 72: 127.0.0.1.80 > 127.0.0.1.33700: Flags [.], ack 78, win 511, options [nop,nop,TS val 3457407303 ecr 3457407303], length 0
16:50:44.207115 lo    In  ifindex 1 00:00:00:00:00:00 ethertype IPv4 (0x0800), length 310: 127.0.0.1.80 > 127.0.0.1.33700: Flags [P.], seq 1:239, ack 78, win 512, options [nop,nop,TS val 3457407303 ecr 3457407303], length 238: HTTP: HTTP/1.1 200 OK
16:50:44.207125 lo    In  ifindex 1 00:00:00:00:00:00 ethertype IPv4 (0x0800), length 72: 127.0.0.1.33700 > 127.0.0.1.80: Flags [.], ack 239, win 511, options [nop,nop,TS val 3457407303 ecr 3457407303], length 0
16:50:44.207143 lo    In  ifindex 1 00:00:00:00:00:00 ethertype IPv4 (0x0800), length 684: 127.0.0.1.80 > 127.0.0.1.33700: Flags [P.], seq 239:851, ack 78, win 512, options [nop,nop,TS val 3457407303 ecr 3457407303], length 612: HTTP
16:50:44.207150 lo    In  ifindex 1 00:00:00:00:00:00 ethertype IPv4 (0x0800), length 72: 127.0.0.1.33700 > 127.0.0.1.80: Flags [.], ack 851, win 507, options [nop,nop,TS val 3457407303 ecr 3457407303], length 0
16:50:44.207794 lo    In  ifindex 1 00:00:00:00:00:00 ethertype IPv4 (0x0800), length 72: 127.0.0.1.33700 > 127.0.0.1.80: Flags [F.], seq 78, ack 851, win 507, options [nop,nop,TS val 3457407303 ecr 3457407303], length 0
16:50:44.207817 lo    In  ifindex 1 00:00:00:00:00:00 ethertype IPv4 (0x0800), length 72: 127.0.0.1.80 > 127.0.0.1.33700: Flags [F.], seq 851, ack 79, win 512, options [nop,nop,TS val 3457407303 ecr 3457407303], length 0
16:50:44.207828 lo    In  ifindex 1 00:00:00:00:00:00 ethertype IPv4 (0x0800), length 72: 127.0.0.1.33700 > 127.0.0.1.80: Flags [.], ack 852, win 507, options [nop,nop,TS val 3457407303 ecr 3457407303], length 0
```
5. Создан отладочный под для ноды:
```bash
kubectl get node
```
```
NAME       STATUS   ROLES           AGE   VERSION
minikube   Ready    control-plane   21h   v1.31.0
```
```bash
kubectl debug node/minikube -it --image=busybox
```
6. Контейнер отладочного пода запускается в пространствах имен ноды, файловая система ноды смонтирована в директорию `/host`:
```
Creating debugging pod node-debugger-minikube-qs552 with container debugger on node minikube.
If you don't see a command prompt, try pressing enter.
/ # ls -la 
total 4
drwxr-xr-x    1 root     root            22 Feb  1 16:51 .
drwxr-xr-x    1 root     root            22 Feb  1 16:51 ..
-rwxr-xr-x    1 root     root             0 Feb  1 16:51 .dockerenv
drwxr-xr-x    1 root     root          4774 Sep 26 21:31 bin
drwxr-xr-x    5 root     root           380 Feb  1 16:51 dev
drwxr-xr-x    1 root     root            56 Feb  1 16:51 etc
drwxr-xr-x    1 nobody   nobody           0 Sep 26 21:31 home
drwxr-xr-x    1 root     root            50 Jan 31 19:11 host
drwxr-xr-x    1 root     root           270 Sep 26 21:31 lib
lrwxrwxrwx    1 root     root             3 Sep 26 21:31 lib64 -> lib
dr-xr-xr-x  623 root     root             0 Feb  1 16:51 proc
drwx------    1 root     root            24 Feb  1 16:52 root
dr-xr-xr-x   13 root     root             0 Feb  1 15:40 sys
drwxrwxrwt    1 root     root             0 Sep 26 21:31 tmp
drwxr-xr-x    1 root     root            14 Sep 26 21:31 usr
drwxr-xr-x    1 root     root             6 Feb  1 16:51 var
```
```
/ # ls -la /host/
total 52
drwxr-xr-x    1 root     root            50 Jan 31 19:11 .
drwxr-xr-x    1 root     root            22 Feb  1 16:51 ..
-rwxr-xr-x    1 root     root             0 Jan 31 19:11 .dockerenv
-rw-r--r--    1 root     root          7890 Sep  3 16:30 CHANGELOG
-rw-r--r--    1 root     root          1093 Sep  3 16:36 Release.key
lrwxrwxrwx    1 root     root             7 Aug  8 14:03 bin -> usr/bin
drwxr-xr-x    1 root     root             0 Apr 18  2022 boot
drwxr-xr-x    1 root     root             0 Jan 31 19:11 data
drwxr-xr-x   17 root     root          4640 Feb  1 15:40 dev
-rw-r--r--    1 root     root          3817 Sep  3 16:35 docker.key
drwxr-xr-x    1 root     root           178 Feb  1 15:40 etc
drwxr-xr-x    1 root     root            12 Sep  3 16:37 home
-rw-r--r--    1 root     root            96 Sep  3 16:37 kic.txt
drwxr-xr-x    1 root     root            64 Jan 31 19:11 kind
lrwxrwxrwx    1 root     root             7 Aug  8 14:03 lib -> usr/lib
lrwxrwxrwx    1 root     root             9 Aug  8 14:03 lib32 -> usr/lib32
lrwxrwxrwx    1 root     root             9 Aug  8 14:03 lib64 -> usr/lib64
lrwxrwxrwx    1 root     root            10 Aug  8 14:03 libx32 -> usr/libx32
drwxr-xr-x    1 root     root             0 Aug  8 14:03 media
drwxr-xr-x    1 root     root             0 Aug  8 14:03 mnt
drwxr-xr-x    1 root     root            20 Jan 31 19:11 opt
dr-xr-xr-x  622 root     root             0 Feb  1 15:40 proc
drwx------    1 root     root            60 Jan 31 19:11 root
drwxr-xr-x   15 root     root           400 Feb  1 15:40 run
lrwxrwxrwx    1 root     root             8 Aug  8 14:03 sbin -> usr/sbin
drwxr-xr-x    1 root     root             0 Aug  8 14:03 srv
dr-xr-xr-x   13 root     root             0 Feb  1 15:40 sys
drwxrwxrwt    5 root     root           140 Feb  1 16:51 tmp
drwxr-xr-x    1 root     root            36 Aug  8 14:03 usr
drwxr-xr-x    1 root     root           160 Jan 31 19:11 var
-rw-r--r--    1 root     root           159 Sep  3 16:37 version.json
```
7. Получены логи контейнеров из пода nginx:
```bash
kubectl get po nginx -o json | jq .metadata.uid
```
```
"a51a2d3e-0fcd-4fd1-8d21-cd25716a5ba5"
```
```bash
tree  /host/var/log/pods/default_nginx_a51a2d3e-0fcd-4fd1-8d21-cd25716a5ba5/
/host/var/log/pods/default_nginx_a51a2d3e-0fcd-4fd1-8d21-cd25716a5ba5/
├── debugger-6kq8s
│   └── 0.log -> /var/lib/docker/containers/65dd251deb1ef032eef201eebca03e78693eae73d148ac4f8666567c06b9daad/65dd251deb1ef032eef201eebca03e78693eae73d148ac4f8666567c06b9daad-json.log
└── nginx
    └── 0.log -> /var/lib/docker/containers/64ac2e1ea2b0e3fa46f204d43fce06eb215e91b9ce7fae430c0085ba8fdcc0e3/64ac2e1ea2b0e3fa46f204d43fce06eb215e91b9ce7fae430c0085ba8fdcc0e3-json.log
```
```bash
kubectl get po nginx -o json | jq ".status.containerStatuses[].containerID"
```
```
"docker://64ac2e1ea2b0e3fa46f204d43fce06eb215e91b9ce7fae430c0085ba8fdcc0e3"
```
```bash
cat /host/var/lib/docker/containers/64ac2e1ea2b0e3fa46f204d43fce06eb215e91b9ce7fae430c0085ba8fdcc0e3/64ac2e1ea2b0e3fa46f204d43fce06eb215e91b9ce7fae430c0085ba8fdcc0e3-json.log 
{"log":"127.0.0.1 - - [02/Feb/2025:00:50:04 +0800] \"GET / HTTP/1.1\" 200 612 \"-\" \"curl/8.9.1\" \"-\"\n","stream":"stdout","time":"2025-02-01T16:50:04.657020497Z"}
{"log":"127.0.0.1 - - [02/Feb/2025:00:50:44 +0800] \"GET / HTTP/1.1\" 200 612 \"-\" \"curl/8.9.1\" \"-\"\n","stream":"stdout","time":"2025-02-01T16:50:44.207232388Z"}

```
```bash
kubectl get po nginx -o json | jq ".status.ephemeralContainerStatuses[].containerID"
```
```
"docker://65dd251deb1ef032eef201eebca03e78693eae73d148ac4f8666567c06b9daad"
```
```bash
cat /host/var/lib/docker/containers/65dd251deb1ef032eef201eebca03e78693eae73d148ac4f8666567c06b9daad/65dd251deb1ef032eef201eebca03e78693eae73d148ac4f8666567c06b9daad-json.log 
```
[Логи debugger контейнера](./debugger.log)

8. Задание со *. Для выполнения команды `strace` для процесса nginx в основном контейнере, процесс debug контейнера должен иметь capabilities `CAP_SYS_PTRACE`. Для их получения нужно при запуске debug контейнера выбрать соответствющий профиль с набором свойств: либо выбрать из списка `static` профилей (например, `general` или `sysadmin`), где они предопределены заранее, либо `custom` (`--custom=custom-profile.yaml`), где свой список capabilities определен в отдельном файле.
```bash 
kubectl debug nginx -it --image=alpine:latest --target=nginx --profile=sysadmin 
```
```bash
apk add strace
```
```
/ # ps
PID   USER     TIME  COMMAND
    1 root      0:00 nginx: master process nginx -g daemon off;
    7 101       0:00 nginx: worker process
   20 root      0:00 /bin/sh
   26 root      0:00 ps
```
```
/ # strace -p 1
strace: Process 1 attached
rt_sigsuspend([], 8
```
Поскольку master процесс `nginx` не обрабатывает запросы, выполнена команда strace для `worker` процесса, включен `port-forward` и выполнен запрос `curl'ом`. 
```
/ # strace -p 7
strace: Process 7 attached
epoll_wait(8, [{events=EPOLLIN, data={u32=2488864784, u64=140271825784848}}], 512, -1) = 1
accept4(6, {sa_family=AF_INET, sin_port=htons(40248), sin_addr=inet_addr("127.0.0.1")}, [112 => 16], SOCK_NONBLOCK) = 3
epoll_ctl(8, EPOLL_CTL_ADD, 3, {events=EPOLLIN|EPOLLRDHUP|EPOLLET, data={u32=2488865248, u64=140271825785312}}) = 0
epoll_wait(8, [{events=EPOLLIN, data={u32=2488865248, u64=140271825785312}}], 512, 60000) = 1
recvfrom(3, "GET / HTTP/1.1\r\nHost: 127.0.0.1:"..., 1024, 0, NULL, NULL) = 77
stat("/usr/share/nginx/html/index.html", {st_mode=S_IFREG|0644, st_size=612, ...}) = 0
openat(AT_FDCWD, "/usr/share/nginx/html/index.html", O_RDONLY|O_NONBLOCK) = 11
fstat(11, {st_mode=S_IFREG|0644, st_size=612, ...}) = 0
writev(3, [{iov_base="HTTP/1.1 200 OK\r\nServer: nginx/1"..., iov_len=238}], 1) = 238
sendfile(3, 11, [0] => [612], 612)      = 612
write(5, "127.0.0.1 - - [02/Feb/2025:01:08"..., 89) = 89
close(11)                               = 0
setsockopt(3, SOL_TCP, TCP_NODELAY, [1], 4) = 0
epoll_wait(8, [{events=EPOLLIN|EPOLLRDHUP, data={u32=2488865248, u64=140271825785312}}], 512, 65000) = 1
recvfrom(3, "", 1024, 0, NULL, NULL)    = 0
close(3)                                = 0
epoll_wait(8, 
```