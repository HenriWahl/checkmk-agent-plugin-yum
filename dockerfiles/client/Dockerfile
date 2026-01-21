FROM debian:13-slim

COPY check-mk-agent*.deb /tmp/

RUN apt -y update && \
    apt -y install bind9-host\
                   docker-cli \
                   iproute2 \
                   xinetd
RUN apt install -y /tmp/*.deb && rm -f /tmp/check-mk-agent*.deb

COPY check-mk-agent /etc/xinetd.d/check-mk-agent

EXPOSE 6556/tcp
CMD ["xinetd", "-dontfork", "-stayalive", "-pidfile", "/var/run/xinetd.pid"]