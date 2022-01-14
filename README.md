# Surface Distance from Volume

[![Version](https://img.shields.io/docker/v/fnndsc/pl-surface-volume-distance?sort=semver)](https://hub.docker.com/r/fnndsc/pl-surface-volume-distance)
[![MIT License](https://img.shields.io/github/license/fnndsc/pl-surface-volume-distance)](https://github.com/FNNDSC/pl-surface-volume-distance/blob/master/LICENSE)
[![Build](https://github.com/FNNDSC/pl-surface-volume-distance/actions/workflows/ci.yml/badge.svg)](https://github.com/FNNDSC/pl-surface-volume-distance/actions)

`pl-surface-volume-distance` is a _ChRIS ds_ plugin which calculates the
distance from every vertex of a surface mesh (`.obj`) to a volume mask
(binary `.mnc`) by projecting the values of a bidirectional radial distance
map (created using `mincchamfer`) onto the surface (using `volume_object_evaluate`).

## Quick Example

```shell
mkdir input output
mv mask.mnc surface_81920.obj input/
singularity exec docker://docker.io/fnndsc/pl-surface-volume-distance:1.0.0 surface_volume_distance input/ output/
```
