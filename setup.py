# install requirements
import pip
pip_version = tuple(pip.__version__.split('.'))
if pip_version >= ('19', '3', '0'):
    import pip._internal.main as pip_main
elif pip_version >= ('19', '0', '0'):
    import pip._internal as pip_main

try:
    import configparser
except:
    pip_main.main(['install', 'configparser'])
try:
    import glob2
except:
    pip_main.main(['install', 'glob2'])
try:
    import requirements
except:
    pip_main.main(['install', 'requirements_parser'])

# import
import os
import setuptools
import pkg_utils

# package name
name = 'pkg_utils'
dirname = os.path.dirname(__file__)

# convert README.md to README.rst
pkg_utils.convert_readme_md_to_rst(dirname)

# get package metadata
md = pkg_utils.get_package_metadata(dirname, name)

# install package
setuptools.setup(
    name=name,
    version=md.version,
    description=("Utilities for linking setuptools with version metadata, "
                 "README files, requirements files, and restoring overridden entry points"),
    long_description=md.long_description,
    url="https://github.com/KarrLab/" + name,
    download_url='https://github.com/KarrLab/' + name,
    author="Karr Lab",
    author_email="info@karrlab.org",
    license="MIT",
    keywords='setuptools, pip, requirements, GitHub, pandoc',
    packages=setuptools.find_packages(exclude=['tests', 'tests.*']),
    package_data=md.package_data,
    install_requires=md.install_requires,
    extras_require=md.extras_require,
    tests_require=md.tests_require,
    dependency_links=md.dependency_links,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering :: Mathematics',
    ],
)
