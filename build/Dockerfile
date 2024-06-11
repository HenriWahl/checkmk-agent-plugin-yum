FROM checkmk/check-mk-raw:2.2.0-latest
LABEL maintainer=henri@nagstamon.de

ARG DEBIAN_FRONTEND=noninteractive

# need to add backports for newer git - otherwise python3 git module won't work
RUN echo "deb http://deb.debian.org/debian buster-backports main" > /etc/apt/sources.list.d/buster-backports.list

# python3 and git needed for build-modify-extension.py
RUN apt -y update && \
    apt -y install python3 \
                   python3-git

# need to add backports for newer git - otherwise python3 git module won't work
RUN apt -y install -t buster-backports git

# scripts used need to be executable
COPY build/build-entrypoint.sh build/build-modify-extension.py /
RUN chmod +x /build-entrypoint.sh /build-modify-extension.py

# run after original docker-entrypoint.sh
CMD /build-entrypoint.sh
