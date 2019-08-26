#!/usr/bin/env python3
from setuptools import setup, find_packages

version = {}
with open("./alyeska/__init__.py", "r") as ifile:
    exec(ifile.read(), version)

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="alyeska",
    version=version["__version__"],
    description="Alyeska /al-ee-EHS-kah/ n. A Data Pipeline Toolkit",
    long_description=open("readme.rst").read(),
    url="https://github.com/Dynatrace/alyeska",
    author="Nick Vogt",
    author_email="nick.vogt@dynatrace.com",
    packages=find_packages(exclude=["tests"]),
    entry_points={
        "console_scripts": [
            "authmfa = alyeska.locksmith.authmfa:main",
            "compose-sh = alyeska.compose.compose_sh:main",
        ]
    },
    install_requires=requirements,
    test_suite="tests",
    tests_require="pytest",
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)
