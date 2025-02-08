FROM nginx:1.27.3-alpine3.20

RUN sed -i '/location \/ {/i \\tlocation = /metrics {\n\t\tstub_status;\n\t}\n' \
        /etc/nginx/conf.d/default.conf
