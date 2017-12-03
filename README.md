[![PyPI package](https://img.shields.io/pypi/v/setuptools_utils.svg)](https://pypi.python.org/pypi/setuptools_utils)
[![Documentation](https://readthedocs.org/projects/setuptools_utils/badge/?version=latest)](http://setuptools_utils.readthedocs.org)
[![Test results](https://circleci.com/gh/KarrLab/setuptools_utils.svg?style=shield)](https://circleci.com/gh/KarrLab/setuptools_utils)
[![Test coverage](https://coveralls.io/repos/github/KarrLab/setuptools_utils/badge.svg)](https://coveralls.io/github/KarrLab/setuptools_utils)
[![Code analysis](https://api.codeclimate.com/v1/badges/f61deab196a9dbf42555/maintainability)](https://codeclimate.com/github/KarrLab/setuptools_utils)
[![License](https://img.shields.io/github/license/KarrLab/setuptools_utils.svg)](LICENSE)
![Analytics](https://ga-beacon.appspot.com/UA-86759801-1/setuptools_utils/README.md?pixel)

# setuptools_utils

Utilities for linking setuptools with package version metadata, GitHub README.md files, requirements.txt files, and restoring overridden entry points during for editable installations.

## Installation

1. Install Python and pip:
    ```
    apt-get install python python-pip
    ```
2. Install this package:
    ```
    pip install git+git://github.com/KarrLab/setuptools_utils#egg=setuptools_utils
    ```
3. Optionally, install support for pandoc to link setuptools with GitHub markdown formatted README.md files:
    ```
    apt-get install pandoc
    pip install git+git://github.com/KarrLab/setuptools_utils#egg=setuptools_utils[pandoc]
    ```

## Documentation
Please see the [API documentation](http://setuptools_utils.readthedocs.io).

## License
The build utilities are released under the [MIT license](LICENSE).

## Development team
This package was developed by the [Karr Lab](http://www.karrlab.org) at the Icahn School of Medicine at Mount Sinai in New York, USA.

## Questions and comments
Please contact the [Karr Lab](http://www.karrlab.org) with any questions or comments.
