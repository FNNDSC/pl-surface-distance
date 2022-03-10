# Surface Distance Error

[![Version](https://img.shields.io/docker/v/fnndsc/pl-surface-distance?sort=semver)](https://hub.docker.com/r/fnndsc/pl-surface-distance)
[![MIT License](https://img.shields.io/github/license/fnndsc/pl-surface-distance)](https://github.com/FNNDSC/pl-surface-distance/blob/main/LICENSE)
[![ci](https://github.com/FNNDSC/pl-surface-distance/actions/workflows/ci.yml/badge.svg)](https://github.com/FNNDSC/pl-surface-distance/actions/workflows/ci.yml)

## Abstract

`pl-surface-distance` is a [_ChRIS_](https://chrisproject.org/)
_ds_ plugin which calculates the distance error of surfaces (`.obj`)
from masks (`.mnc`). It is for assessing the accuracy of surface
extraction and deformation algorithms.

`pl-surface-distance` can operate on multiple data files in its
input directory. For every mask in its input directory:
for every surface in the directory of the mask, compute the
distance from every vertex of the surface to the mask.

Under the hood, `pl-surface-distance` is a script which calls
`mincchamfer` and `volume_object_evaluate`.

## Installation

`pl-surface-distance` is a _[ChRIS](https://chrisproject.org/) plugin_, meaning it can
run from either within _ChRIS_ or the command-line.

[![Get it from chrisstore.co](https://ipfs.babymri.org/ipfs/QmaQM9dUAYFjLVn3PpNTrpbKVavvSTxNLE5BocRCW1UoXG/light.png)](https://chrisstore.co/plugin/pl-surface-distance)

## Local Usage

To get started with local command-line usage, use [Apptainer](https://apptainer.org/)
(a.k.a. Singularity) to run `pl-surface-distance` as a container:

```shell
singularity exec docker://fnndsc/pl-mask-distance surfdisterr input/ output/
```

To print its available options, run:

```shell
singularity exec docker://fnndsc/pl-mask-distance surfdisterr --help
```

## Examples

`surfdisterr` requires two positional arguments: a directory containing
input data, and a directory where to create output data.
First, create the input directory and move input data into it.

```shell
mkdir incoming/ outgoing/
mv some.dat other.dat incoming/
singularity exec docker://fnndsc/pl-mask-distance:latest surfdisterr [--args] incoming/ outgoing/
```

## Development

Instructions for developers.

### Building

Build a local container image:

```shell
docker build -t localhost/fnndsc/pl-mask-distance .
```

### Get JSON Representation

Run [`chris_plugin_info`](https://github.com/FNNDSC/chris_plugin#usage)
to produce a JSON description of this plugin, which can be uploaded to a _ChRIS Store_.

```shell
docker run --rm localhost/fnndsc/pl-mask-distance chris_plugin_info > chris_plugin_info.json
```

### Local Test Run

Mount the source code `app.py` into a container to test changes without rebuild.

```shell
docker run --rm -it --userns=host -u $(id -u):$(id -g) \
    -v $PWD/surfdisterr.py:/usr/local/lib/python3.10/site-packages/surfdisterr.py:ro \
    -v $PWD/in:/incoming:ro -v $PWD/out:/outgoing:rw -w /outgoing \
    localhost/fnndsc/pl-mask-distance surfdisterr /incoming /outgoing
```
