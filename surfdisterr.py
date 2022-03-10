#!/usr/bin/env python

import os
import sys
from pathlib import Path
from argparse import ArgumentParser, Namespace, ArgumentDefaultsHelpFormatter
from importlib.metadata import Distribution
from typing import Optional, Generator
import subprocess as sp
from itertools import repeat
from concurrent.futures import Executor, ThreadPoolExecutor

from loguru import logger
from chris_plugin import chris_plugin, PathMapper

__pkg = Distribution.from_name(__package__)
__version__ = __pkg.version


DISPLAY_TITLE = r"""
       _                        __                         _ _     _
      | |                      / _|                       | (_)   | |
 _ __ | |______ ___ _   _ _ __| |_ __ _  ___ ___ ______ __| |_ ___| |_ __ _ _ __   ___ ___
| '_ \| |______/ __| | | | '__|  _/ _` |/ __/ _ \______/ _` | / __| __/ _` | '_ \ / __/ _ \
| |_) | |      \__ \ |_| | |  | || (_| | (_|  __/     | (_| | \__ \ || (_| | | | | (_|  __/
| .__/|_|      |___/\__,_|_|  |_| \__,_|\___\___|      \__,_|_|___/\__\__,_|_| |_|\___\___|
| |
|_|
"""

parser = ArgumentParser(description=' Distance error of a .obj mask mesh to a .mnc volume.',
                        formatter_class=ArgumentDefaultsHelpFormatter)
parser.add_argument('-V', '--version', action='version',
                    version=f'$(prog)s {__version__}')
parser.add_argument('-m', '--mask', default='**/*.mnc',
                    help='pattern for mask file names to include')
parser.add_argument('-s', '--surface', default='*.obj',
                    help='pattern for surface file names to include')
parser.add_argument('-q', '--quiet', action='store_true',
                    help='disable status messages')
# parser.add_argument('--no-fail', action='store_true', dest='no_fail',
#                     help='do not produce non-zero exit status on failures')
parser.add_argument('--keep-chamfer', action='store_true', dest='keep_chamfer',
                    help='keep the distance map intermediate file')
parser.add_argument('--chamfer-suffix', type=str, default='.chamfer.mnc', dest='chamfer_suffix',
                    help='chamfer file name suffix')


@chris_plugin(
    parser=parser,
    title='Surface Distance Error',
    category='Surface Extraction',
    min_memory_limit='100Mi',    # supported units: Mi, Gi
    min_cpu_limit='1000m',       # millicores, e.g. "1000m" = 1 CPU core
    min_gpu_limit=0              # set min_gpu_limit=1 to enable GPU
)
def main(options: Namespace, inputdir: Path, outputdir: Path):
    if options.quiet:
        logger.remove()
        logger.add(sys.stderr, level='WARNING')
    else:
        print(DISPLAY_TITLE, file=sys.stderr, flush=True)

    masks = []
    output_dirs = []
    for mask, output_dir in PathMapper(inputdir, outputdir, glob=options.mask, suffix=''):
        masks.append(mask)
        output_dirs.append(output_dir)

    nproc = len(os.sched_getaffinity(0))
    logger.debug('Using {} threads.', nproc)
    with ThreadPoolExecutor(max_workers=nproc) as pool:
        m = pool.map(
            surface_distance,
            masks,
            output_dirs,
            repeat(options.surface),
            repeat(options.chamfer_suffix),
            repeat(options.keep_chamfer),
            repeat(pool)
        )

        # more calls to pool are added by surface_distance to run volume_object_evaluate,
        # this for-loop no-op prevents the pool from shutting down before the subroutiens
        # to run volume_object_evaluate are executed.
        for _ in m:
            pass

    logger.debug('done')


def surface_distance(mask: Path, output_dir: Path, surface_glob: str, chamfer_suffix: str, keep_chamfer: bool,
                     pool: Executor):
    """
    Create a chamfer (distance map) for the mask and then use it to perform ``volume_object_evaluate``
    on all surfaces which are found for the mask.
    """
    output_dir.mkdir()
    chamfer = output_dir / Path(mask.name).with_suffix(chamfer_suffix)
    create_chamfer(mask, chamfer, 0)

    surfaces = tuple(mask.parent.glob(surface_glob))
    results = tuple(output_dir / s.relative_to(mask.parent).with_suffix('.dist.txt') for s in surfaces)

    for result_file in results:
        result_file.parent.mkdir(exist_ok=True, parents=True)

    pool.map(volume_object_evaluate, repeat(chamfer), surfaces, results)

    if not keep_chamfer:
        chamfer.unlink()


def sibling_surfaces(mask: Path, surface_glob: str) -> Generator[Path, None, None]:
    return mask.parent.glob(surface_glob)


def create_chamfer(mask: Path, chamfer: Path, label: Optional[int]):
    cmd: list[str] = ['chamfer.sh']
    if label != 0:
        cmd += ['-i', str(label)]
    cmd += [str(mask), str(chamfer)]
    sp.run(cmd, check=True)
    logger.info('Created chamfer for {}', mask)


def volume_object_evaluate(chamfer: Path, surface: Path, result: Path):
    cmd = ['volume_object_evaluate', '-linear', chamfer, surface, result]
    sp.run(cmd, check=True)
    logger.info(result)


if __name__ == '__main__':
    main()
