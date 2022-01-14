FROM docker.io/fnndsc/pybicpl:v0.2.0-2
LABEL maintainer="Jennings Zhang <Jennings.Zhang@childrens.harvard.edu>"

WORKDIR /usr/local/src/pl-surface-volume-distance

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN pip install .

CMD ["surface_volume_distance", "--help"]
