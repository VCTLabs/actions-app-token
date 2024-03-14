FROM python:3.9-alpine3.16

RUN apk --no-cache add git bash

ADD entrypoint.sh /
ADD token_getter.py /

RUN pip install \
    cryptography==3.4.8 \
    github3.py==1.3.0 \
    jwcrypto==0.6.0 \
    pyjwt==1.7.1

RUN chmod u+x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
