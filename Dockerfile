FROM docker:20.10.3-dind

RUN apk add --update \
    nodejs \
    build-base 

RUN mkdir /var/task
WORKDIR /var/task

ARG SERVERLESS_VERSION=latest
ENV SERVERLESS_VERSION $SERVERLESS_VERSION

RUN apk --no-cache add python3 python3-dev py-pip ca-certificates groff less bash make jq curl wget g++ zip git openssh && \
  pip3 --no-cache-dir install awscli && \
  update-ca-certificates

# make sure we're using python3 when sls invoke uses it
RUN rm -f /usr/bin/python && ln -s /usr/bin/python3 /usr/bin/python
RUN pip3 install pipenv 
RUN pip3 install awscli-local boto3 awscli localstack

RUN apk update && apk add --no-cache docker-cli

RUN wget -q -O /etc/apk/keys/sgerrand.rsa.pub https://alpine-pkgs.sgerrand.com/sgerrand.rsa.pub && \
  wget -q https://github.com/sgerrand/alpine-pkg-glibc/releases/download/2.25-r0/glibc-2.25-r0.apk && \
  apk add glibc-2.25-r0.apk && \
  rm -f glibc-2.25-r0.apk

RUN mkdir -p /tmp/yarn && \
  mkdir -p /opt/yarn/dist && \
  cd /tmp/yarn && \
  wget -q https://yarnpkg.com/latest.tar.gz && \
  tar zvxf latest.tar.gz && \
  find /tmp/yarn -maxdepth 2 -mindepth 2 -exec mv {} /opt/yarn/dist/ \; && \
  rm -rf /tmp/yarn

RUN ln -sf /opt/yarn/dist/bin/yarn /usr/local/bin/yarn && \
  ln -sf /opt/yarn/dist/bin/yarn /usr/local/bin/yarnpkg && \
  yarn --version

RUN yarn global add serverless@$SERVERLESS_VERSION

RUN yarn global add   \
  serverless-plugin-resource-tagging@1.0.11 \
  serverless-deployment-bucket@1.3.0 \
  serverless-localstack@0.4.28 \
  serverless-plugin-composed-vars@1.0.3 \
  serverless-plugin-include-dependencies@4.1.0 \
  serverless-python-requirements@5.1.0

# needed to avoid tabcompletion nag 
RUN sls config tabcompletion install
