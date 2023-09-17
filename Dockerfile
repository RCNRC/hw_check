FROM python:3.10

COPY ./requirements.txt /usr/src/hw_check/
RUN pip install --no-cache-dir -r /usr/src/hw_check/requirements.txt

WORKDIR /usr/src/hw_check

COPY hw_ckeck.py ./

CMD [ "python3", "./hw_ckeck.py" ]