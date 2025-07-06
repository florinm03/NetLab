# https://quay.io/repository/frrouting/frr/manifest/sha256:d4cb742ae97e43a4ea7cad3fc1e9663365761792d31213f3752668d05cab3e1c
FROM quay.io/frrouting/frr@sha256:dcae82861c03a412028f9909cbb9a4f87cff73701fdb0589c9c8b131966ce667
RUN apk add --no-cache tcpdump
RUN apk add --no-cache frr-pythontools
COPY daemons /etc/frr/daemons
COPY vtysh.conf /etc/frr/vtysh.conf
COPY frr.conf /etc/frr/frr.conf