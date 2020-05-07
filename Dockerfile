FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY script.py ./

RUN sudo apt-get install nmap

CMD ["python","-u","script.py"]

# -u is for logs, see: https://stackoverflow.com/questions/29663459/python-app-does-not-print-anything-when-running-detached-in-docker