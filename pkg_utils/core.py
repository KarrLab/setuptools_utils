""" Utilities for linking setuptools with package version metadata, 
GitHub README.md files, requirements.txt files, and restoring overridden
entry points during for editable installations.

:Author: Jonathan Karr <jonrkarr@gmail.com>
:Date: 2017-12-03
:Copyright: 2017, Karr Lab
:License: MIT
"""

import configparser
import glob2
import os
import re
import requirements.parser
import subprocess
import sys


try:
    import pypandoc
except ImportError:  # pragma: no cover
    pypandoc = None  # pragma: no cover


class PackageMetadata(object):
    """ Metadata about a package

    Attributes:
        name (:obj:`str`)
        description (:obj:`str`): short description
        long_description (:obj:`str`): long description, e.g. from ``README.rst``
        version (:obj:`str`): version, e.g. from ``package/_version.py``
        install_requires (:obj:`list` of :obj:`str`): dependencies, e.g. from ``requirements.txt``
        extras_require (:obj:`dict` of :obj:`list` of :obj:`str`): optional dependencies, e.g. from ``requirements.optional.txt``
        tests_require (:obj:`list` of :obj:`str`): test dependencies, e.g. from ``tests/requirements.txt``
        dependency_links (:obj:`list` of :obj:`str`): documentation dependencies, e.g. from ``docs/requirements.txt``
    """

    def __init__(self):
        self.name = ''
        self.description = ''
        self.long_description = ''
        self.version = ''
        self.package_data = {}
        self.install_requires = []
        self.extras_require = {}
        self.tests_require = []
        self.dependency_links = []


def get_package_metadata(dirname, package_name, package_data_filename_patterns=None):
    """ Get meta data about a package

    Args:
        dirname (:obj:`str`): path to the package
        package_name (:obj:`str`): package name
        package_data_filename_patterns (:obj:`dict`, optional): package name, optionally with glob patterns in the filenames

    Returns:
        :obj:`PackageMetadata`: meta data

    Raises:
        :obj:`ValueError:` if test or documentation dependencies are defined in `requirements.optional.txt`
    """
    md = PackageMetadata()

    # get long description
    md.long_description = get_long_description(dirname)

    # get version
    md.version = get_version(dirname, package_name)

    # get data files
    md.package_data = expand_package_data_filename_patterns(
        dirname, package_data_filename_patterns=package_data_filename_patterns)

    # get dependencies
    md.install_requires, md.extras_require, md.tests_require, md.dependency_links = get_dependencies(
        dirname)

    return md


def convert_readme_md_to_rst(dirname):
    """ Convert the README.md to README.rst

    Args:
        dirname (:obj:`str`): path to the package
    """
    if pypandoc and os.path.isfile(os.path.join(dirname, 'README.md')):
        pypandoc.convert_file(os.path.join(dirname, 'README.md'), 'rst',
                              format='md', outputfile=os.path.join(dirname, 'README.rst'))


def get_long_description(dirname):
    """ Get the long description of a package from its README.rst file

    Args:
        dirname (:obj:`str`): path to the package

    Returns:
        :obj:`str`: long description
    """
    if os.path.isfile(os.path.join(dirname, 'README.rst')):
        with open(os.path.join(dirname, 'README.rst'), 'r') as file:
            return file.read()
    else:
        return ''


def get_version(dirname, package_name):
    """ Get the version a package from its version file (``package/_version.py``)

    Args:
        dirname (:obj:`str`): path to the package
        package_name (:obj:`str`): package name

    Returns:
        :obj:`str`: version
    """
    # get version from _version.py file
    filename = os.path.join(dirname, package_name, "_version.py")
    if os.path.isfile(filename):
        verstrline = open(filename, "rt").read()
        VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
        mo = re.search(VSRE, verstrline, re.M)
        if mo:
            version = mo.group(1)
            return version


def expand_package_data_filename_patterns(dirname, package_data_filename_patterns=None):
    """ Expand the package data filenames

    Args:
        :obj:`dict`: package data
    """
    package_data_filename_patterns = package_data_filename_patterns or {}
    package_data = {}
    for module, filename_patterns in package_data_filename_patterns.items():
        module_filenames = []

        for filename_pattern in filename_patterns:
            for filename in glob2.iglob(os.path.join(dirname, module, filename_pattern), include_hidden=True, recursive=True):
                if os.path.isfile(filename):
                    module_filenames.append(os.path.relpath(
                        filename, os.path.join(dirname, module)))

        package_data[module] = sorted(set(module_filenames))
    return package_data


def get_dependencies(dirname, include_uri=False, include_extras=True, include_specs=True, include_markers=True):
    """ Parse required and optional dependencies from requirements.txt files

    Args:
        dirname (:obj:`str`): path to the package
        include_uri (:obj:`bool`, optional): if :obj:`True`, include URI in the dependencies list
        include_extras (:obj:`bool`, optional): if :obj:`True`, include extras in the dependencies list
        include_specs (:obj:`bool`, optional): if :obj:`True`, include specifications in the dependencies list
        include_markers (:obj:`bool`, optional): if :obj:`True`, include markers in the dependencies list

    Returns:
        :obj:`list` of :obj:`str`: requirements
        :obj:`list` of :obj:`str`: extra/optional requirements
        :obj:`list` of :obj:`str`: test requirements
        :obj:`list` of :obj:`str`: dependency links
    """
    dependency_links = []

    install_requires, tmp = parse_requirements_file(
        os.path.join(dirname, 'requirements.txt'),
        include_uri=include_uri, include_extras=include_extras,
        include_specs=include_specs, include_markers=include_markers)
    dependency_links += tmp

    extras_require, tmp = parse_optional_requirements_file(
        os.path.join(dirname, 'requirements.optional.txt'),
        include_uri=include_uri, include_extras=include_extras,
        include_specs=include_specs, include_markers=include_markers)
    dependency_links += tmp

    tests_require, tmp = parse_requirements_file(
        os.path.join(dirname, 'tests/requirements.txt'),
        include_uri=include_uri, include_extras=include_extras,
        include_specs=include_specs, include_markers=include_markers)
    dependency_links += tmp

    docs_require, tmp = parse_requirements_file(
        os.path.join(dirname, 'docs/requirements.txt'),
        include_uri=include_uri, include_extras=include_extras,
        include_specs=include_specs, include_markers=include_markers)
    dependency_links += tmp

    if 'tests' in extras_require and extras_require['tests']:
        raise ValueError(
            'Test dependencies should be defined in `tests/requirements`')
    if 'docs' in extras_require and extras_require['docs']:
        raise ValueError(
            'Documentation dependencies should be defined in `docs/requirements`')

    extras_require['tests'] = tests_require
    extras_require['docs'] = docs_require

    all_reqs = []
    for reqs in extras_require.values():
        all_reqs += reqs
    extras_require['all'] = all_reqs

    install_requires = set(install_requires)
    for option in extras_require:
        extras_require[option] = set(extras_require[option])
    tests_require = set(tests_require)
    docs_require = set(docs_require)
    dependency_links = set(dependency_links)

    for option in extras_require:
        extras_require[option] = extras_require[option].difference(
            install_requires)
    tests_require = tests_require.difference(install_requires)
    docs_require = docs_require.difference(install_requires)

    install_requires = sorted(list(install_requires))
    for option in extras_require:
        extras_require[option] = sorted(list(extras_require[option]))
    tests_require = sorted(list(tests_require))
    docs_require = sorted(list(docs_require))
    dependency_links = sorted(list(dependency_links))

    return (install_requires, extras_require, tests_require, dependency_links)


def parse_requirements_file(filename, include_uri=False, include_extras=True, include_specs=True, include_markers=True):
    """ Parse a requirements.txt file into list of requirements and dependency links

    Args:
        filename (:obj:`str`): path to requirements.txt file
        include_uri (:obj:`bool`, optional): if :obj:`True`, include URI in the dependencies list
        include_extras (:obj:`bool`, optional): if :obj:`True`, include extras in the dependencies list
        include_specs (:obj:`bool`, optional): if :obj:`True`, include specifications in the dependencies list
        include_markers (:obj:`bool`, optional): if :obj:`True`, include markers in the dependencies list

    Returns:
        :obj:`list` of :obj:`str`: requirements
        :obj:`list` of :obj:`str`: dependency links
    """
    if os.path.isfile(filename):
        with open(filename, 'r') as file:
            lines = file.readlines()
    else:
        lines = []
    return parse_requirement_lines(lines,
                                   include_uri=include_uri, include_extras=include_extras,
                                   include_specs=include_specs, include_markers=include_markers)


def parse_optional_requirements_file(filename, include_uri=False, include_extras=True, include_specs=True, include_markers=True):
    """ Parse a requirements.optional.txt file into list of requirements and dependency links

    Args:
        filename (:obj:`str`): path to requirements.txt file
        include_uri (:obj:`bool`, optional): if :obj:`True`, include URI in the dependencies list
        include_extras (:obj:`bool`, optional): if :obj:`True`, include extras in the dependencies list
        include_specs (:obj:`bool`, optional): if :obj:`True`, include specifications in the dependencies list
        include_markers (:obj:`bool`, optional): if :obj:`True`, include markers in the dependencies list

    Returns:
        :obj:`dict` of :obj:`list` of :obj:`str`: requirements
        :obj:`list` of :obj:`str`: dependency links

    Raises:
        :obj:`ValueError`: if a line cannot be parsed
    """
    option = None
    extras_require = {}
    dependency_links = []

    if os.path.isfile(filename):
        with open(filename, 'r') as file:
            for line in file:
                line = line.strip()
                if not line or line[0] == '#':
                    continue
                if line[0] == '[':
                    match = re.match(r'^\[([a-zA-Z0-9-_]+)\]$', line)
                    if not match:
                        raise ValueError(
                            'Could not parse optional dependency: {}'.format(line))
                    option = match.group(1)
                else:
                    if option is None:
                        raise ValueError(
                            "Required dependencies should not be placed in an optional dependencies file: {}".format(line))
                    tmp1, tmp2 = parse_requirement_lines([line],
                                                         include_uri=include_uri, include_extras=include_extras,
                                                         include_specs=include_specs, include_markers=include_markers)
                    if option not in extras_require:
                        extras_require[option] = []
                    extras_require[option] += tmp1
                    dependency_links += tmp2

    return (extras_require, dependency_links)


def parse_requirement_lines(lines, include_uri=False, include_extras=True, include_specs=True, include_markers=True):
    """ Parse lines from a requirements.txt file into list of requirements and dependency links

    Args:
        lines (:obj:`list` of :obj:`str`): lines from a requirements.txt file
        include_uri (:obj:`bool`, optional): if :obj:`True`, include URI in the dependencies list
        include_extras (:obj:`bool`, optional): if :obj:`True`, include extras in the dependencies list
        include_specs (:obj:`bool`, optional): if :obj:`True`, include specifications in the dependencies list
        include_markers (:obj:`bool`, optional): if :obj:`True`, include markers in the dependencies list

    Returns:
        :obj:`list` of :obj:`str`: requirements
        :obj:`list` of :obj:`str`: dependency links
    """
    requires = []
    dependency_links = []

    for line in lines:
        requirement, dependency_link = parse_requirement_line(
            line, include_uri=include_uri, include_extras=include_extras,
            include_specs=include_specs, include_markers=include_markers)
        if requirement:
            requires.append(requirement)
        if dependency_link:
            dependency_links.append(dependency_link)

    return (requires, dependency_links)


def parse_requirement_line(line, include_uri=False, include_extras=True, include_specs=True, include_markers=True):
    """ Parse lines from a requirements.txt file into list of requirements and dependency links

    Args:
        line (:obj:`str`): line from a requirements.txt file
        include_uri (:obj:`bool`, optional): if :obj:`True`, include URI in the dependencies list
        include_extras (:obj:`bool`, optional): if :obj:`True`, include extras in the dependencies list
        include_specs (:obj:`bool`, optional): if :obj:`True`, include specifications in the dependencies list
        include_markers (:obj:`bool`, optional): if :obj:`True`, include markers in the dependencies list

    Returns:
        :obj:`str`: requirement
        :obj:`str`: dependency link
    """

    # strip white space
    line = line.strip()

    # stop processing if the line is empty or only contains comments
    if not line or line.startswith('#'):
        return (None, None)

    # get version hints from `egg` metadata. This must be done because (a) pip
    # requires a version hint and (b) the `requirements` package doesn't support version hints.
    match = re.search(r'egg=([a-z0-9_]+)\-([a-z0-9\.]+)', line, re.IGNORECASE)
    if match:
        version_hint = match.group(2)
        line = re.sub(r'egg=([a-z0-9_]+)\-([a-z0-9\.]+)',
                      r'egg=\1', line, re.IGNORECASE)
    else:
        version_hint = None

    # parse line
    req = requirements.parser.Requirement.parse_line(line)
    line = req.line

    # check that name is valid and we support all of the features needed to install the dependency
    if not req.name or not re.match(r'^[a-zA-Z0-9_\.]+$', req.name):
        raise ValueError('Dependency could not be parsed: {}'.format(line))

    if line.startswith('-e ') or req.editable:
        raise ValueError('Editable option is not supported')

    if req.local_file:
        raise ValueError('Local file option is not supported')

    # get dependency link
    if req.uri:
        uri_line = line.replace(req.uri + '#egg=', '')
        dependency_link = req.uri

        if req.revision:
            dependency_link += '@' + req.revision
            uri_line = uri_line.replace('@' + req.revision, '')

        dependency_link += '#egg=' + req.name

        # add version information to dependency link because pip requires a version hint.
        if not version_hint:
            raise ValueError(
                'Version hints must be provided for packages from non-PyPI sources')
        dependency_link += '-' + version_hint

        if req.subdirectory:
            dependency_link += '&subdirectory=' + req.subdirectory
            uri_line = uri_line.replace(
                '&subdirectory=' + req.subdirectory, '')

        if req.hash and req.hash_name:
            dependency_link += '&' + req.hash_name + '=' + req.hash
            uri_line = uri_line.replace(
                '&' + req.hash_name + '=' + req.hash, '')

        uri_req = requirements.parser.Requirement.parse_line(uri_line)
        req.specs = list(set(req.specs + uri_req.specs))
    else:
        dependency_link = None

    # get specifiers/markers
    if ';' in line:
        marker = line[line.find(';')+1:].strip()
    else:
        marker = ''

    # append dependency to requirements list with extras, specs, and specifiers/markers
    if include_uri and req.uri:
        req_setup = dependency_link.replace('#egg={}-{}'.format(req.name, version_hint),
                                            '#egg={}'.format(req.name))
    else:
        req_setup = req.name

    if include_extras and req.extras:
        req_setup += '[' + ', '.join(sorted(req.extras)) + ']'

    if include_specs and req.specs:
        req_setup += ' ' + ', '.join([' '.join(spec)
                                      for spec in sorted(req.specs)])
    req_setup = req_setup.rstrip()

    if include_markers and marker:
        req_setup += '; ' + marker

    requirement = req_setup.strip()
    return (requirement, dependency_link)


def install_dependencies(dependencies, upgrade=False):
    """ Install dependencies

    Args:
        dependencies (:obj:`list`): list of dependencies
        upgrade (:obj:`bool`, optional): if :obj:`True`, upgrade package
    """
    dependencies = " ".join(dependencies)
    if upgrade:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-U", dependencies])
    else:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", dependencies])


def get_console_scripts(dirname, package_name):
    """ Get the console scripts for a package

    Args:
        dirname (:obj:`str`): path to the package
        package_name (:obj:`str`): package name

    Returns:
        :obj:`dict` of :obj:`dict`: console script names and functions
    """
    egg_dir = os.path.join(dirname, package_name + '.egg-info')
    if os.path.isdir(egg_dir):
        parser = configparser.ConfigParser()
        parser.read(os.path.join(egg_dir, 'entry_points.txt'))
        scripts = {}
        for name, func in parser.items('console_scripts'):
            scripts[str(name)] = {
                'function': str(func),
            }
        return scripts
    return None


def add_console_scripts(dirname, package_name, console_scripts):
    """ Add console scripts for a package

    Args:
        dirname (:obj:`str`): path to the package
        package_name (:obj:`str`): package name
        console_scripts (:obj:`dict` of :obj:`dict`): console script names and functions
    """
    if not console_scripts:
        return

    egg_dir = os.path.join(dirname, package_name + '.egg-info')
    parser = configparser.ConfigParser()

    parser.read(os.path.join(egg_dir, 'entry_points.txt'))
    for name, func in parser.items('console_scripts'):
        console_scripts[str(name)] = {
            'function': str(func),
        }

    for name, metadata in console_scripts.items():
        parser.set('console_scripts', name, metadata['function'])

    with open(os.path.join(egg_dir, 'entry_points.txt'), 'w') as file:
        parser.write(file)
