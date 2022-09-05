FROM ubuntu:20.04

COPY ./analyzers /app/analyzers
COPY ./classifier_assets /app/classifier_assets
COPY ./templates /app/templates
COPY ./CommitClassifier.py /app/
COPY ./Compliance.py /app/
COPY ./DataManager.py /app/
COPY ./driver.py /app/
COPY ./GlobalConfigs.py /app/
COPY ./GraphKit.py /app/
COPY ./Grouper.py /app/
COPY ./RepoBrewer.py /app/
COPY ./RepoDriller.py /app/
COPY ./Reporter.py /app/
COPY ./requirements.txt /app/
COPY ./utils.py /app/

RUN apt-get update \
    && apt-get install -y default-jre \
    && apt-get install -y python3 \
    && apt-get install -y python3-pip \
    && apt-get install -y git \
    && pip3 install -r /app/requirements.txt \
    && chmod 777 /app/ \
    && mkdir -m 777 /app/tmp/ \
    && python3 /app/driver.py --resolve-owaspdc \
    && chmod +x /app/analyzers/resources/dependency-check/bin/dependency-check.sh

WORKDIR /app/
ENTRYPOINT ["python3", "driver.py"]