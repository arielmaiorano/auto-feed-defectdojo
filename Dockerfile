FROM kalilinux/kali-rolling

RUN apt-get update && apt-get install -y \
    curl \
    wget \
    sudo \
    python3 \
    python3-pip \
    nmap \
    zaproxy \
    nikto \
    wapiti \
    sslyze \
&& rm -rf /var/lib/apt/lists/*

RUN pip3 install drheader
RUN pip3 install zapcli
RUN pip install gvm-tools

RUN mkdir /opt/afdd
WORKDIR /opt/afdd
COPY afdd/requirements.txt /opt/afdd
RUN pip3 install -r requirements.txt
COPY afdd/main.py /opt/afdd
COPY afdd/openvas_scan.py /opt/afdd

EXPOSE 9090/tcp

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9090"]
