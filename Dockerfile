FROM osgeo/gdal:ubuntu-small-3.6.3

WORKDIR /app

COPY . /app

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6 python3-pip -y

RUN python -m pip install --upgrade pip && \
    pip install .
# RUN pip install azure-storage-blob==12.20.0 \
#     gdal==3.6.3 numpy==1.26.4 opencv-python==4.10.0.84 python-dotenv==1.0.1 \
#     pymongo==4.10.1 rasterio==1.4.3 scikit-image==0.25.1 shapely==2.0.6 pytz==2024.2


CMD ["bash", "-c", "echo 'Started container'; ls -l src; python src/main.py"]