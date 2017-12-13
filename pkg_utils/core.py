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
import pip
try:
    import pypandoc
except ImportError:  # pragma: no cover
    pypandoc = None  # pragma: no cover
import re
import requirements


class PackageMetadata(object):
    """ Metadata about a package

    Attributes:
        name (:obj:`str`)
        description (:obj:`str`): short description
        long_description (:obj:`str`): long description, e.g. from ``README.rst``
        version (:obj:`str`): version, e.g. from ``package/VERSION``
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
        :obj:`Exception:` if test or documentation dependencies are defined in `requirements.optional.txt`
    """
    md = PackageMetadata()

    # get long description
    md.long_description = get_long_description(dirname)

    # get version
    md.version = get_version(dirname, package_name)

    # get data files
    md.package_data = expand_package_data_filename_patterns(dirname, package_data_filename_patterns=package_data_filename_patterns)

    # get dependencies
    md.install_requires, md.extras_require, md.tests_require, md.dependency_links = get_dependencies(dirname)

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
    """ Get the version a package from its VERSION file (``package/VERSION``)

    Args:
        dirname (:obj:`str`): path to the package
        package_name (:obj:`str`): package name

    Returns:
        :obj:`str`: version
    """
    with open(os.path.join(dirname, package_name, 'VERSION'), 'r') as file:
        return file.read().strip()


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
                    module_filenames.append(os.path.relpath(filename, os.path.join(dirname, module)))

        package_data[module] = sorted(set(module_filenames))
    return package_data


def get_dependencies(dirname, include_extras=True, include_specs=True, include_markers=True):
    """ Parse required and optional dependencies from requirements.txt files

    Args:
        dirname (:obj:`str`): path to the package
        include_extras (:obj:`bool`, optional): if :obj:`True`, include extras in the dependencies list
        include_specs (:obj:`bool`, optional): if :obj:`True`, include specifications in the dependencies list
        include_markers (:obj:`bool`, optional): if :obj:`True`, include markers in the dependencies list

    Returns:
        :obj:`list` of :obj:`str`: requirements
        :obj:`list` of :obj:`str`: dependency links
    """
    dependency_links = []

    install_requires, tmp = parse_requirements_file(
        os.path.join(dirname, 'requirements.txt'),
        include_extras=include_extras, include_specs=include_specs, include_markers=include_markers)
    dependency_links += tmp

    extras_require, tmp = parse_optional_requirements_file(
        os.path.join(dirname, 'requirements.optional.txt'),
        include_extras=include_extras, include_specs=include_specs, include_markers=include_markers)
    dependency_links += tmp

    tests_require, tmp = parse_requirements_file(
        os.path.join(dirname, 'tests/requirements.txt'),
        include_extras=include_extras, include_specs=include_specs, include_markers=include_markers)
    dependency_links += tmp

    docs_require, tmp = parse_requirements_file(
        os.path.join(dirname, 'docs/requirements.txt'),
        include_extras=include_extras, include_specs=include_specs, include_markers=include_markers)
    dependency_links += tmp

    if 'tests' in extras_require and extras_require['tests']:
        raise Exception('Test dependencies should be defined in `tests/requirements`')
    if 'docs' in extras_require and extras_require['docs']:
        raise Exception('Documentation dependencies should be defined in `docs/requirements`')

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
        extras_require[option] = extras_require[option].difference(install_requires)
    tests_require = tests_require.difference(install_requires)
    docs_require = docs_require.difference(install_requires)

    install_requires = sorted(list(install_requires))
    for option in extras_require:
        extras_require[option] = sorted(list(extras_require[option]))
    tests_require = sorted(list(tests_require))
    docs_require = sorted(list(docs_require))
    dependency_links = sorted(list(dependency_links))

    return (install_requires, extras_require, tests_require, dependency_links)


def parse_requirements_file(filename, include_extras=True, include_specs=True, include_markers=True):
    """ Parse a requirements.txt file into list of requirements and dependency links

    Args:
        filename (:obj:`str`): path to requirements.txt file
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
    return parse_requirement_lines(lines, include_extras=include_extras, include_specs=include_specs, include_markers=include_markers)


def parse_optional_requirements_file(filename, include_extras=True, include_specs=True, include_markers=True):
    """ Parse a requirements.optional.txt file into list of requirements and dependency links

    Args:
        filename (:obj:`str`): path to requirements.txt file
        include_extras (:obj:`bool`, optional): if :obj:`True`, include extras in the dependencies list
        include_specs (:obj:`bool`, optional): if :obj:`True`, include specifications in the dependencies list
        include_markers (:obj:`bool`, optional): if :obj:`True`, include markers in the dependencies list

    Returns:
        :obj:`dict` of :obj:`list` of :obj:`str`: requirements
        :obj:`list` of :obj:`str`: dependency links

    Raises:
        :obj:`Exception`: if a line cannot be parsed
    """
    option = None
    extras_require = {}
    dependency_links = []

    if os.path.isfile(filename):
        with open(filename, 'r') as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue
                if line[0] == '[':
                    match = re.match('^\[([a-zA-Z0-9-_]+)\]$', line)
                    if not match:
                        raise Exception('Could not parse optional dependency: {}'.format(line))
                    option = match.group(1)
                else:
                    if option is None:
                        raise Exception("Required dependencies should be not be place in an optional dependencies file: {}".format(line))
                    tmp1, tmp2 = parse_requirement_lines([line], include_extras=include_extras,
                                                         include_specs=include_specs, include_markers=include_markers)
                    if option not in extras_require:
                        extras_require[option] = []
                    extras_require[option] += tmp1
                    dependency_links += tmp2

    return (extras_require, dependency_links)


def parse_requirement_lines(lines, include_extras=True, include_specs=True, include_markers=True):
    """ Parse lines from a requirements.txt file into list of requirements and dependency links

    Args:
        lines (:obj:`list` of :obj:`str`): lines from a requirements.txt file
        include_extras (:obj:`bool`, optional): if :obj:`True`, include extras in the dependencies list
        include_specs (:obj:`bool`, optional): if :obj:`True`, include specifications in the dependencies list
        include_markers (:obj:`bool`, optional): if :obj:`True`, include markers in the dependencies list

    Returns:
        :obj:`list` of :obj:`str`: requirements
        :obj:`list` of :obj:`str` of :obj:`str`: dependency links

    Raises:
        :obj:`Exception`: if a line cannot be parse
    """
    requires = []
    dependency_links = []

    for line in lines:
        if not line.strip() or line.strip()[0] == '#':
            continue

        req = requirements.parser.Requirement.parse_line(line)
        if not req.name or not re.match('^[a-zA-Z0-9_]+$', req.name):
            raise Exception('Dependency could not be parsed: {}'.format(line))

        line = req.line
        if '#egg=' in line:
            if line.find('#') < line.find('#egg='):
                line = line[0:line.find('#')]  # pragma: no cover # unreachable because this can't be parsed by requirements
            else:
                line = line[0:line.find('#', line.find('#egg=')+5)]
        else:
            if '#' in line:
                line = line[0:line.find('#')]
        if ';' in line:
            marker = line[line.find(';')+1:].strip()
        else:
            marker = ''

        req_setup = req.name
        if include_extras and req.extras:
            req_setup += '[' + ', '.join(sorted(req.extras)) + ']'
        if include_specs and req.specs:
            req_setup += ' ' + ', '.join([' '.join(spec) for spec in sorted(req.specs)])
        req_setup = req_setup.rstrip()
        if include_markers and marker:
            req_setup += '; ' + marker

        requires.append(req_setup.strip())

        if req.uri:
            if req.revision:
                dependency_link = req.uri + '@' + req.revision + '#egg=' + req.name
            else:
                dependency_link = req.uri + '#egg=' + req.name

            dependency_links.append(dependency_link)

    return (requires, dependency_links)


def install_dependencies(dependencies, upgrade=False):
    """ Install dependencies

    Args:
        dependencies (:obj:`list`): list of dependencies
        upgrade (:obj:`bool`, optional): if :obj:`True`, upgrade package
    """
    cmd = ['install']
    if upgrade:
        cmd.append('-U')
    cmd += dependencies
    pip.main(cmd)


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
