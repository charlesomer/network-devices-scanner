FROM python

WORKDIR /usr/src/app

RUN apt-get update
RUN apt-get install nmap -y
RUN pip install --no-cache-dir -r requirements.txt

COPY requirements.txt ./

COPY script.py ./

CMD ["python","-u","script.py"]

# -u is for logs, see: https://stackoverflow.com/questions/29663459/python-app-does-not-print-anything-when-running-detached-in-docker