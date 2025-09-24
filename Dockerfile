# Dockerfile per build APK MonumentRecognizer
FROM ubuntu:20.04

# Evita prompt interattivi
ENV DEBIAN_FRONTEND=noninteractive

# Installa dipendenze di sistema
RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-venv \
    git zip unzip wget curl \
    openjdk-8-jdk \
    build-essential \
    libssl-dev libffi-dev \
    libsqlite3-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libncursesw5-dev \
    xz-utils tk-dev \
    libxml2-dev libxslt1-dev \
    libjpeg-dev libpng-dev \
    autoconf libtool pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Configura Java
ENV JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64

# Installa Android SDK
ENV ANDROID_HOME=/opt/android-sdk
ENV PATH=${PATH}:${ANDROID_HOME}/cmdline-tools/latest/bin:${ANDROID_HOME}/platform-tools

RUN mkdir -p ${ANDROID_HOME} && \
    cd ${ANDROID_HOME} && \
    wget -q https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip && \
    unzip -q commandlinetools-linux-9477386_latest.zip && \
    rm commandlinetools-linux-9477386_latest.zip && \
    mkdir -p cmdline-tools/latest && \
    mv cmdline-tools/* cmdline-tools/latest/ && \
    yes | cmdline-tools/latest/bin/sdkmanager --licenses && \
    cmdline-tools/latest/bin/sdkmanager "platform-tools" "platforms;android-30" "build-tools;30.0.3" "ndk;21.4.7075529"

# Installa Python packages
RUN pip3 install --upgrade pip setuptools wheel && \
    pip3 install buildozer python-for-android kivy kivymd cython==0.29.33 \
                pillow requests folium matplotlib plotly pandas

# Crea working directory
WORKDIR /app

# Script di build
COPY . .

CMD ["bash", "-c", "source setup_docker_build.sh"]
