#!/usr/bin/env python

import os
import sys
from pathlib import Path
from argparse import ArgumentParser, Namespace, ArgumentDefaultsHelpFormatter
from importlib.metadata import Distribution
from typing import Iterator
import subprocess as sp
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

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
parser.add_argument('-o', '--output-suffix', default='.dist.txt', dest='output_suffix',
                    help='output file name suffix')
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

    logger.debug('Discovering input files...')
    subjects = [
        Subject(mask, output_dir, output_dir / Path(mask.name).with_suffix(options.chamfer_suffix))
        for mask, output_dir in PathMapper(inputdir, outputdir, glob=options.mask, suffix='')
    ]

    logger.debug('Creating output directories...')
    for subject in subjects:
        subject.output_dir.mkdir(parents=True)

    nproc = len(os.sched_getaffinity(0))
    logger.debug('Using {} threads.', nproc)
    with ThreadPoolExecutor(max_workers=nproc) as pool:
        m = pool.map(lambda s: s.create_chamfer(), subjects)
        collect_errors(m)

        tasks_per = (s.gather_tasks(options.surface, options.output_suffix) for s in subjects)
        all_tasks = (t for tasks_for_subject in tasks_per for t in tasks_for_subject)
        m = pool.map(lambda t: volume_object_evaluate(*t), all_tasks)
        collect_errors(m)

    logger.debug('done')


@dataclass(frozen=True)
class Subject:
    mask: Path
    output_dir: Path
    chamfer: Path

    def create_chamfer(self, label: int = 0) -> None:
        cmd: list[str] = ['chamfer.sh']
        if label != 0:
            cmd += ['-i', str(label)]
        cmd += [self.mask, self.chamfer]
        sp.run(cmd, check=True)
        logger.info('Created chamfer for {}', self.mask)

    def gather_tasks(self, surfaces_glob: str, output_suffix: str) -> Iterator[tuple[Path, Path, Path]]:
        """
        Find surface files which are siblings (in the same directory) as the mask,
        and yield the arguments to be passed to ``volume_object_evaluate``.
        """
        return (
            (
                self.chamfer,
                surface,
                self.output_dir / surface.relative_to(self.mask.parent).with_suffix(output_suffix)
            )
            for surface in self.mask.parent.glob(surfaces_glob)
        )


def collect_errors(__m: Iterator) -> None:
    for _ in __m:
        pass


def volume_object_evaluate(chamfer: Path, surface: Path, result: Path):
    result.parent.mkdir(exist_ok=True, parents=True)
    cmd = ['volume_object_evaluate', '-linear', chamfer, surface, result]
    sp.run(cmd, check=True)
    logger.info(result)


if __name__ == '__main__':
    main()
