FROM fedora:latest

RUN dnf -y install \
        bind-utils \
        curl \
        iproute \
        iputils \
        less \
        man-db \
        man-pages \
        mtr \
        nmap \
        python3 \
        samba-client \
        traceroute \
    && dnf clean all

CMD ["bash"]
