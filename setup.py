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
    description="""CI Alyeska For maintaining the CI data warehouse""",
    long_description=open("readme.md").read(),
    url="https://bitbucket.lab.dynatrace.org/projects/DONE/repos/ci-alyeska/",
    author="Nick Vogt",
    author_email="nick.vogt@dynatrace.com",
    license="Dynatrace",
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
)
