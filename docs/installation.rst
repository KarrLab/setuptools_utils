Installation
============

Requirements
--------------------------

First, install `Python <https://www.python.org>`_ and `pip <https://pip.pypa.io>`_. The following command illustrates how to install Python and pip on Ubuntu Linux:

    .. code-block:: bash

        apt-get install python python-pip


Optional requirements
--------------------------

Second, optionally install pandoc to convert Markdown-formatted README files for GitHub into reStructuredText-formatted files for PyPI:

    .. code-block:: bash

        apt-get install pandoc


Installing this package
---------------------------

Use the following command to install this package from PyPI:

    .. code-block:: bash

        pip install pkg_utils

The latest version of this package can be installed from GitHub using this command:

    .. code-block:: bash

        pip install git+https://github.com/KarrLab/pkg_utils.git

Support for the pandoc can be installed using the following option:

    .. code-block:: bash

        pip install pkg_utils[pandoc]
        pip install git+https://github.com/KarrLab/pkg_utils.git[pandoc]
