Tutorial
============

Linking setuptools with package version numbers
-----------------------------------------------

The following example shows how to link a package number stored in ``package/_version.py`` with setuptools:

.. code-block:: python

    import os
    import setuptools
    try:
        import pkg_utils
    except ImportError:
        import subprocess
        import sys
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "pkg_utils"])
        import pkg_utils

    # package name
    name = 'my_package'
    dirname = os.path.dirname(__file__)

    # get package metadata
    md = pkg_utils.get_package_metadata(dirname, name)

    # install package
    setuptools.setup(
        ...
        version=md.version,
    )


Linking setuptools with GitHub README.md files
----------------------------------------------

The following example shows how to link GutHub Markdown-formatted README.md files with setuptools which requires long descriptions in reStructuredText format. Note, this feature requires the pandoc option.

.. code-block:: python

    import os
    import setuptools
    try:
        import pkg_utils
    except ImportError:
        import subprocess
        import sys
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "pkg_utils"])
        import pkg_utils

    # package name
    name = 'my_package'
    dirname = os.path.dirname(__file__)

    # convert README.md to README.rst
    pkg_utils.convert_readme_md_to_rst(dirname)

    # get package metadata
    md = pkg_utils.get_package_metadata(dirname, name)

    # install package
    setuptools.setup(
        ...
        long_description=md.long_description,
    )


Linking setuptools with requirements
------------------------------------

The following example illustrates how to link setuptools with requirements.txt files:

.. code-block:: python

    import os
    import setuptools
    try:
        import pkg_utils
    except ImportError:
        import subprocess
        import sys
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "pkg_utils"])
        import pkg_utils

    # package name
    name = 'my_package'
    dirname = os.path.dirname(__file__)

    # get package metadata
    md = pkg_utils.get_package_metadata(dirname, name)

    # install package
    setuptools.setup(
        ...
        install_requires=md.install_requires,
        extras_require=md.extras_require,
        tests_require=md.tests_require,
        dependency_links=md.dependency_links,
    )

This extracts dependencies from the following files:

* ``requirements.txt``: dependencies
* ``requirements.optional.txt``: optional dependencies
* ``tests/requirement.txt``: dependencies to run the tests
* ``docs/requirement.txt``: dependencies to build the docummentation

The ``requirements.txt`` files should follow the `pip format <https://pip.pypa.io/en/stable/reference/pip_install/#requirements-file-format>`_::

    package_1
    package_2[package_2_option_2] >= 1.0.0; python_version >= "2.7.14"

The ``requirements.optional.txt`` should follow the same format, but with section headings to indicate the options::

    [my_option_1]
    package_1
    package_2[package_2_option_2] >= 1.0.0; python_version >= "2.7.14"

    [my_option_2]
    package_3
    package_4

In addition to the installation options described in ``requirements.optional.txt``, pkg_utils will create ``tests``, ``docs`` and ``all`` options to install the test, documentation, and all dependencies.

Restoring overridden console scripts during editable installations
------------------------------------------------------------------

The following example illustrates how to restore overridden console scripts during editable installations. This useful for generating console scripts for specific versions of Python.

.. code-block:: python

    import os
    import setuptools
    try:
        import pkg_utils
    except ImportError:
        import subprocess
        import sys
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "pkg_utils"])
        import pkg_utils

    # package name
    name = 'my_package'
    dirname = os.path.dirname(__file__)

    # read old console scripts
    console_scripts = pkg_utils.get_console_scripts(dirname, name)

    # install package
    setuptools.setup(...)

    # restore old console scripts
    pkg_utils.add_console_scripts(dirname, name, console_scripts)


Putting it all together
-----------------------

The following example shows how to use all of the features of this package:

.. code-block:: python

    import os
    import setuptools
    try:
        import pkg_utils
    except ImportError:
        import subprocess
        import sys
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "pkg_utils"])
        import pkg_utils

    # package name
    name = 'my_package'
    dirname = os.path.dirname(__file__)

    # get package metadata
    md = pkg_utils.get_package_metadata(dirname, name)

    # read old console scripts
    console_scripts = pkg_utils.get_console_scripts(dirname, name)

    # install package
    setuptools.setup(
        ...
        version=md.version,
        long_description=md.long_description,
        install_requires=md.install_requires,
        extras_require=md.extras_require,
        tests_require=md.tests_require,
        dependency_links=md.dependency_links,
    )

    # restore old console scripts
    pkg_utils.add_console_scripts(dirname, name, console_scripts)
