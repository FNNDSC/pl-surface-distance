from os import path
from setuptools import setup

with open(path.join(path.dirname(path.abspath(__file__)), 'README.md')) as f:
    readme = f.read()

setup(
    name='pl-surfdisterr',
    version='1.2.1',
    description=' Distance error of a .obj mask mesh to a .mnc volume.',
    long_description=readme,
    long_description_content_type='text/markdown',
    author='Jennings Zhang',
    author_email='Jennings.Zhang@childrens.harvard.edu',
    url='https://github.com/FNNDSC/pl-surfdisterr',
    py_modules=['surfdisterr'],
    install_requires=['chris_plugin'],
    license='MIT',
    python_requires='>=3.10.2',
    entry_points={
        'console_scripts': [
            'surfdisterr = surfdisterr:main'
        ]
    },
    scripts=['scripts/chamfer.sh'],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Scientific/Engineering :: Medical Science Apps.'
    ]
)
