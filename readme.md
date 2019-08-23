# Alyeska /al-ee-EHS-kah/ n. A Data Pipeline Toolkit

Alyeska, or _Aly_ for short, is a Python toolkit to help manage data pipelines. Tools are broken out into modules with niche purposes:

1. `compose` is a workflow dependency management tool

1. `locksmith` helps authorize AWS sessions and Redshift connections

1. `logging` is another thin module that standardizes logging practices

1. `redpandas` supports less verbose pandas/redshift functionality

1. `sqlagent` supports SQL executation and runtime configuration

## Contribute

There are some devtools required to contribute to the repo. Create a development environment and install pre-commit to run hooks on your code.

``` 
$ conda create -n alyeska-dev python=3.6
$ conda activate alyeska-dev
$ pip install -r requirements.dev.txt
$ pre-commit install
$ pre-commit autoupdate
```

## Namesake

The Alyeska Pipeline Service company maintains the Alaska pipeline; a 1, 200 km long pipeline connecting the oil-rich, subterranean earth in Alaska to port on the north pacific ocean.

