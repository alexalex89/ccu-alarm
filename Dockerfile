FROM python:3.9.7-alpine3.14

WORKDIR /usr/src/app

ENV CCU_URL="https://homematic-raspi/addons/xmlapi"

COPY requirements.txt ./
RUN apk add --update --no-cache g++ gcc libxslt-dev
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./ccu_alarm.py" ]