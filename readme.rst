==================================================
Alyeska /al-ee-EHS-kah/ n. A Data Pipeline Toolkit
==================================================

.. Leave space for img.shields.io buttons

Alyeska, or *Aly* for short, is a Python toolkit to help manage data pipelines. Tools are broken out into modules with niche purposes:

1. ``compose`` is a workflow dependency management tool
2. ``locksmith`` helps authorize AWS sessions and Redshift connections
3. ``logging`` is another thin module that standardizes logging practices
4. ``redpandas`` supports less verbose pandas/redshift functionality
5. ``sqlagent`` supports SQL executation and runtime configuration

Extras
~~~~~~

License
^^^^^^^

This project is licensed under the MIT License - see the LICENSE_ file for details.

.. _LICENSE: https://github.com/Dynatrace/alyeska/blob/master/LICENSE

Contribute
^^^^^^^^^^

There are some devtools required to contribute to the repo. Create a development environment and install pre-commit to run hooks on your code.

.. code-block:: sh

    $ conda create -n alyeska-dev python=3.6
    $ conda activate alyeska-dev
    $ pip install -r requirements.dev.txt
    $ pre-commit install
    $ pre-commit autoupdate

Namesake
^^^^^^^^

The Alyeska Pipeline Service company maintains the Alaska pipeline; a 1, 200 km long pipeline connecting the oil-rich, subterranean earth in Alaska to port on the north pacific ocean.

