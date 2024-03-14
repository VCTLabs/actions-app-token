FROM python:3.9-alpine3.16

RUN apk --no-cache add git bash

ADD entrypoint.sh /
ADD token_getter.py /
ADD requirements.txt /

RUN pip install --no-cache-dir -r /requirements.txt

RUN chmod u+x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
