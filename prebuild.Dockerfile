FROM python:3.9-alpine3.16

RUN pip install \
    cryptography==42.0.5 \
    github3.py==4.0.1 \
    jwcrypto==1.5.6 \
    pyjwt==2.8.0

COPY token_getter.py app/
COPY entrypoint.sh app/
RUN chmod u+x app/entrypoint.sh
WORKDIR app/

CMD /app/entrypoint.sh
