FROM osgeo/gdal:ubuntu-small-3.6.3

WORKDIR /app

COPY . /app

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6 python3-pip -y

RUN python -m pip install --upgrade pip && \
    pip install .


CMD ["bash", "-c", "echo 'Started container!!!!!!!'; ls -l src; python src/main.py"]