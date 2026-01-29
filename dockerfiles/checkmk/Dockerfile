ARG CHECKMK_VERSION=2.4.0p19

FROM checkmk/check-mk-cloud:${CHECKMK_VERSION}
LABEL maintainer=henri@nagstamon.de

ARG DEBIAN_FRONTEND=noninteractive
ARG CMK_PASSWORD=cmkadmin
ARG CMK_SITE_ID=cmk

# python3 and git needed for modify-extension.py
RUN apt -y update && \
    apt -y install less \
                   python3 \
                   python3-git \
                   vim

# scripts used need to be executable
COPY dockerfiles/checkmk/modify-extension.py /usr/local/bin
RUN chmod +x /usr/local/bin/modify-extension.py

# Create site 'cmk'
RUN omd create --admin-password "${CMK_PASSWORD}" "${CMK_SITE_ID}"
# seems to avoid crying about tmpfs in container being not allowd
RUN omd config cmk set TMPFS off
# configure to be available for local debugging
RUN omd config cmk set APACHE_TCP_ADDR 0.0.0.0
