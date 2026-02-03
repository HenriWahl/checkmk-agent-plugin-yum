FROM rockylinux:8

COPY check-mk-agent*.rpm /tmp/

RUN dnf -y install iproute \
                   lsof \
                   procps-ng\
                   xinetd
RUN dnf -y install /tmp/*.rpm && \
    rm -f /tmp/check-mk-agent*.rpm

COPY check-mk-agent /etc/xinetd.d/check-mk-agent

EXPOSE 6556/tcp
CMD ["xinetd", "-dontfork", "-stayalive", "-pidfile", "/var/run/xinetd.pid"]