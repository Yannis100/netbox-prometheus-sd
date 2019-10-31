FROM python:3.7-alpine
LABEL maintainer="noc@kollegienet.dk"

COPY . /app
WORKDIR /app

RUN apk add --update --no-cache g++ libc-dev libxslt-dev
RUN pip install -r requirements.txt
COPY netbox-prometheus-sd.py ./netbox-prometheus-sd
RUN chmod +x ./netbox-prometheus-sd
RUN mkdir /output

CMD while true; do (./netbox-prometheus-sd "$NETBOX_URL" "$NETBOX_TOKEN" "/output/${OUTPUT_FILE-netbox.json}"; sleep $INTERVAL); done