FROM checkmk/check-mk-raw:2.0.0-latest
LABEL maintainer=henri@nagstamon.de

ARG DEBIAN_FRONTEND=noninteractive

RUN apt -y update && \
    apt -y install python3 \
                   python3-git

COPY build-entrypoint.sh build-modify-package.py /
RUN chmod +x /build-entrypoint.sh /build-modify-package.py

CMD /build-entrypoint.sh