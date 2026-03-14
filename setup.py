from setuptools import setup
from build_ext import get_extension

setup(ext_modules=[get_extension()])
