FROM checkmk/check-mk-cloud:2.4.0p19
LABEL maintainer=henri@nagstamon.de

ARG DEBIAN_FRONTEND=noninteractive

# python3 and git needed for build-modify-extension.py
RUN apt -y update && \
    apt -y install git \
                   python3 \
                   python3-git

# scripts used need to be executable
COPY build/build-entrypoint.sh build/build-modify-extension.py /
RUN chmod +x /build-entrypoint.sh /build-modify-extension.py

# run after original docker-entrypoint.sh
CMD /build-entrypoint.sh
