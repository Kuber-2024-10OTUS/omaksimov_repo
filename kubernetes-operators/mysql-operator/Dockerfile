FROM python:3.12-alpine3.21

RUN apk upgrade && \
    adduser -u 10001 -D -s /sbin/nologin mysql_operator

USER mysql_operator

WORKDIR /opt/mysql_operator

COPY ./src .

RUN pip install --no-cache-dir -r requirements.txt  && \
    rm -f requirements.txt

ENTRYPOINT [ "/usr/local/bin/python3" ]
CMD [ "-m", "kopf", "run", "mysql_operator.py", "-A", "--verbose" ]