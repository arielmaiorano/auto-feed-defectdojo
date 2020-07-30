FROM kalilinux/kali-rolling

RUN apt-get update && apt-get install -y python3 python3-pip nmap nikto

RUN mkdir /opt/afdd
COPY afdd/requirements.txt /opt/afdd
WORKDIR /opt/afdd

RUN pip3 install -r requirements.txt

COPY afdd/main.py /opt/afdd

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9090"]

EXPOSE 9090/tcp

