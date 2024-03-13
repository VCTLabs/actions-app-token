FROM python:3.9-alpine3.16

RUN apk --no-cache add git bash

ADD entrypoint.sh /
ADD token_getter.py /

RUN pip install --no-cache-dir \
    cryptography==42.0.5 \
    github3.py==4.0.1 \
    jwcrypto==1.5.6 \
    pyjwt==2.8.0

RUN chmod u+x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
