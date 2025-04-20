FROM python:3.12

ENV FLASK_APP_PATH='/loverboxd'
ENV FLASK_APP_PORT=5000

WORKDIR ${FLASK_APP_PATH}

RUN sed -i -E 's/MinProtocol[=\ ]+.*/MinProtocol = TLSv1.0/g' /etc/ssl/openssl.cnf

RUN apt-get update && apt-get install -y \
  cron \
  gcc \
  musl-dev \
  openssl \
  ca-certificates \
  apt-transport-https \
  curl \
  gnupg-agent \
  software-properties-common \
  vim \
  && rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip install -r requirements.txt

EXPOSE ${FLASK_APP_PORT}

ENTRYPOINT ["./boot.sh"]