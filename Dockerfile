FROM docker.io/fnndsc/mni-conda-base:civet2.1.1-python3.10.2

LABEL org.opencontainers.image.authors="FNNDSC <dev@babyMRI.org>" \
      org.opencontainers.image.title="pl-surface-distance" \
      org.opencontainers.image.description=" Distance error of a .obj surface mesh to a .mnc volume. "

WORKDIR /usr/local/src/pl-surface-distance

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN pip install .

CMD ["surfdisterr", "--help"]
