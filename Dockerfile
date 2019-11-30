FROM python:3.7-alpine
WORKDIR /code

ADD requirements/ /code/requirements

RUN apk add --no-cache --virtual .build-deps \
    build-base openssl-dev pkgconfig libffi-dev \
    cups-dev jpeg-dev && \
    # libc6-compat is needed for running session-manager-plugin
    apk add --no-cache libc6-compat && \
    pip install --no-cache-dir -r /code/requirements/requirements.txt && \
    apk del .build-deps

COPY . ./
RUN pip install -e .
RUN aws-gate bootstrap

ENTRYPOINT ["aws-gate"]
CMD ["--help"]