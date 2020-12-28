from setuptools import setup, find_packages
import os

package_root = os.path.abspath(os.path.dirname(__file__))

version = {}
with open(os.path.join(package_root, "src/version.py")) as fp:
    exec(fp.read(), version)
version = version["__version__"]

setup(
    packages=find_packages(),
    version=version
)
