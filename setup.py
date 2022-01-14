from os import path
from setuptools import setup

with open(path.join(path.dirname(path.abspath(__file__)), 'README.md')) as f:
    readme = f.read()

setup(
    name='surface_volume_distance',
    version='1.0.1',
    description='Calculate distance from .obj surface to .mnc volume',
    long_description=readme,
    author='Jennings Zhang',
    author_email='Jennings.Zhang@childrens.harvard.edu',
    url='https://github.com/FNNDSC/pl-surface-volume-distance',
    packages=['surface_volume_distance'],
    install_requires=['chrisapp'],
    license='MIT',
    zip_safe=False,
    python_requires='>=3.9',
    scripts=['scripts/chamfer.sh'],
    entry_points={
        'console_scripts': [
            'surface_volume_distance = surface_volume_distance.__main__:main'
        ]
    }
)
