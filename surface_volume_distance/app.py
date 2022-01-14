from chrisapp.base import ChrisApp
from argparse import ArgumentDefaultsHelpFormatter
from glob import glob
import sys
from os import path
from pathlib import Path
from tempfile import NamedTemporaryFile
from contextlib import contextmanager
from typing import Optional, Callable
import subprocess as sp


@contextmanager
def pretend_open(f: Path) -> Path:
    yield f


@contextmanager
def temp_file_manager(suffix='.mnc') -> Path:
    with NamedTemporaryFile(suffix=suffix, delete=True) as f:
        yield Path(f.name)


class App(ChrisApp):
    description             = 'Calculate distance from .obj surface to .mnc volume'
    PACKAGE                 = __package__
    TITLE                   = 'Surface Distance from Volume'
    CATEGORY                = 'Surface analysis'
    TYPE                    = 'ds'
    ICON                    = ''   # url of an icon image
    MIN_NUMBER_OF_WORKERS   = 1    # Override with the minimum number of workers as int
    MAX_NUMBER_OF_WORKERS   = 1    # Override with the maximum number of workers as int
    MIN_CPU_LIMIT           = 1000 # Override with millicore value as int (1000 millicores == 1 CPU core)
    MIN_MEMORY_LIMIT        = 200  # Override with memory MegaByte (MB) limit as int
    MIN_GPU_LIMIT           = 0    # Override with the minimum number of GPUs as int
    MAX_GPU_LIMIT           = 0    # Override with the maximum number of GPUs as int

    # Use this dictionary structure to provide key-value output descriptive information
    # that may be useful for the next downstream plugin. For example:
    #
    # {
    #   "finalOutputFile":  "final/file.out",
    #   "viewer":           "genericTextViewer",
    # }
    #
    # The above dictionary is saved when plugin is called with a ``--saveoutputmeta``
    # flag. Note also that all file paths are relative to the system specified
    # output directory.
    OUTPUT_META_DICT = {}

    def __init__(self):
        super().__init__()
        self.formatter_class = ArgumentDefaultsHelpFormatter

    def define_parameters(self):
        self.add_argument(
            '-m', '--mask',
            dest='mask',
            help='Glob for volume file name.',
            default='*.mnc',
            type=str,
            optional=True
        )
        self.add_argument(
            '-s', '--surface',
            dest='surface',
            help='Glob for surface file name.',
            default='*.obj',
            type=str,
            optional=True
        )
        self.add_argument(
            '-o', '--output',
            dest='output_filename',
            help='Output file name',
            default='distances.txt',
            type=str,
            optional=True
        )
        self.add_argument(
            '-c', '--chamfer',
            dest='chamfer_filename',
            help='If specified, save the chamfer distance map to a file.',
            default='',
            type=str,
            optional=True
        )
        self.add_argument(
            '-l', '--label',
            dest='label',
            help='If non-0, indicates the given volume is not a binary mask but '
                 'a segmentation volume where 1=CSF, 2=GM, 3=WM, and higher numbers '
                 'representing deeper subcortical layers. The integer value given by '
                 '--label is the compartment targeted by the surface.',
            default=0,
            type=int,
            optional=True
        )

    def run(self, options):
        get_input_file = self.curry_get_input_file(options.inputdir)
        mask = get_input_file(options.mask)
        surface = get_input_file(options.surface)
        output_dir = Path(options.outputdir)
        output = output_dir / options.output_filename

        if options.chamfer_filename:
            chamfer_context = pretend_open(output_dir / options.chamfer_filename)
        else:
            chamfer_context = temp_file_manager()

        with chamfer_context as chamfer:
            self.create_chamfer(mask, chamfer, options.label)
            self.volume_object_evaluate(chamfer, surface, output)

    @staticmethod
    def create_chamfer(mask: Path, chamfer: Path, label: Optional[int]):
        cmd: list[str] = ['chamfer.sh']
        if label != 0:
            cmd += ['-i', str(label)]
        cmd += [str(mask), str(chamfer)]
        sp.run(cmd, check=True)

    @staticmethod
    def volume_object_evaluate(chamfer: Path, surface: Path, result: Path):
        cmd = ['volume_object_evaluate', '-linear', chamfer, surface, result]
        cmd = [str(s) for s in cmd]
        sp.run(cmd, check=True)

    @staticmethod
    def __fail(msg: str, rc=1):
        print(msg)
        sys.exit(rc)

    @classmethod
    def curry_get_input_file(cls, inputdir) -> Callable[[str], Path]:
        def get_input_file(file_glob: str) -> Path:
            possible_filenames = glob(path.join(inputdir, file_glob))
            if len(possible_filenames) > 1:
                cls.__fail(f'More than one file found matching "{file_glob}": {possible_filenames}')
            if len(possible_filenames) == 0:
                cls.__fail(f'No input file found matching: {file_glob}')
            return Path(possible_filenames[0])
        return get_input_file

    def show_man_page(self):
        self.print_help()
