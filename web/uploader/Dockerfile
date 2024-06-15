ARG UBUNTU_VERSION=22.04

FROM ubuntu:${UBUNTU_VERSION}

ARG PYTHON_VERSION=3.11
ARG PIP_VERSION=23.0.1

EXPOSE 8080
ENV LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8 LANGUAGE=en_US.UTF-8 PYTHONHASHSEED=42
COPY requirements.txt /etc/requirements.txt

RUN set -x \
    && sed -i -e 's/archive.ubuntu.com/mirror.yandex.ru/' /etc/apt/sources.list \
    && export DEBIAN_FRONTEND=noninteractive \
    && apt-get update -qq \
    && apt-get upgrade -qq \
    \
    && apt-get install -qq --no-install-recommends software-properties-common \
    && apt-get update -qq \
    \
    && apt-get install -qq --no-install-recommends \
        gnupg \
        ca-certificates \
        cron \
        gettext \
        libxslt1.1 \
        locales \
        openssl \
        python${PYTHON_VERSION} \
        python3-pip \
        python3-setuptools \
        run-one \
        syslog-ng-core \
        logrotate \
        libssl3

RUN set -x \
    && add-apt-repository ppa:alex-p/tesseract-ocr-devel -y \
    && apt-get update -qq \
    && apt-get install -qq \
        tesseract-ocr \
        ghostscript \
        ocrmypdf \
        unpaper


RUN set -x \
    # pip requirements.txt
    && BUILD_DEPS="\
        build-essential \
        libxml2-dev \
        python${PYTHON_VERSION}-dev \
        libssl-dev \
        wget \
    " \
    && apt-get install -qq --no-install-recommends ${BUILD_DEPS} \
    && ln -sf /usr/bin/python${PYTHON_VERSION} /usr/bin/python3 \
    && python3 -m pip install --no-cache-dir -U pip==${PIP_VERSION} \
    && python3 -m pip install --no-cache-dir -r /etc/requirements.txt \
    \
    # autoremove deletes chardet lib now
    && apt-mark manual python3-chardet \
    # cleaning up
    && apt-get autoremove -y ${BUILD_DEPS} \
    && dpkg --purge libpython2.7-minimal python2.7-minimal python-minimal python3-pip \
    && rm -rf /usr/share/doc/ \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* \
    && echo 'install done'

WORKDIR /var/www/

COPY .. .

COPY kbd.traineddata /usr/share/tesseract-ocr/5/tessdata/kbd.traineddata

ARG GIT_BRANCH=master
ARG GIT_COMMIT=local_commit
ARG VERSION=local_build
ARG SOURCE=local_source
ARG PIPELINE_ID=local

ENV GIT_BRANCH=$GIT_BRANCH \
    GIT_COMMIT=$GIT_COMMIT \
    VERSION=$VERSION \
    SOURCE=$SOURCE \
    PIPELINE_ID=$PIPELINE_ID \
    PORT=$PORT

ENV PYTHONUNBUFFERED=1

CMD ["python3", "app.py"]