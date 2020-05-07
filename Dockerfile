FROM python

COPY requirements.txt ./
COPY script.py ./

RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "./script.py" ]
