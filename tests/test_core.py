""" Tests for setuptools_utils

:Author: Jonathan Karr <jonrkarr@gmail.com>
:Date: 2017-11-14
:Copyright: 2017, Karr Lab
:License: MIT
"""

import os
import setuptools_utils
import shutil
import tempfile
import unittest


class TestCase(unittest.TestCase):

    def setUp(self):
        self.dirname = dirname = tempfile.mkdtemp()

        os.mkdir(os.path.join(self.dirname, 'package'))
        os.mkdir(os.path.join(self.dirname, 'tests'))
        os.mkdir(os.path.join(self.dirname, 'docs'))

        with open(os.path.join(dirname, 'package', 'VERSION'), 'w') as file:
            file.write('0.0.1')

        with open(os.path.join(dirname, 'README.md'), 'w') as file:
            file.write('# Test\n')

        with open(os.path.join(dirname, 'requirements.txt'), 'w') as file:
            file.write('req1\n')
            file.write('req1\n')
            file.write('req2[opt2]\n')
            file.write('req3 >= 1.0\n')
            file.write('#comment\n')
            file.write('\n')
            file.write('req4; python_version > "2.6"\n')

        with open(os.path.join(dirname, 'requirements.optional.txt'), 'w') as file:
            file.write('[package_opt_1]\n')
            file.write('req7\n')
            file.write('\n')
            file.write('[package_opt_2]\n')
            file.write('req8[opt8a,opt8b]\n')
            file.write('req9[opt9a, opt9b]\n')
            file.write('git+https://github.com/opt/req10.git@branch#egg=req10[option10] #comment\n')

        with open(os.path.join(dirname, 'tests', 'requirements.txt'), 'w') as file:
            file.write('req9\n')

        with open(os.path.join(dirname, 'docs', 'requirements.txt'), 'w') as file:
            file.write('req1\n')
            file.write('req1\n')
            file.write('req2[opt2]\n')
            file.write('req3 >= 1.0\n')
            file.write('req10\n')
            file.write('req11 #comment\n')
            file.write('req12[opt12a, opt12b] <=1.0,>=2.0; python_version>="2.7"\n')
            file.write('req13[opt13a,opt13b]; python_version >= "2.7"\n')
            file.write('git+https://github.com/opt/req14.git#egg=req14[opt13a,opt13b]; python_version >= "2.7"\n')
            file.write('git+https://github.com/opt/req15.git#egg=req15 ; python_version >= "2.7"\n')
            file.write('git+https://github.com/opt/req16.git#egg=req16\n')
            file.write('git+https://github.com/opt/req17.git#egg=req17 #comment\n')
            file.write('git+https://github.com/opt/req18.git@branch#egg=req18 #comment\n')

    def tearDown(self):
        shutil.rmtree(self.dirname)

    def test_get_package_metadata(self):
        setuptools_utils.convert_readme_md_to_rst(self.dirname)
        md = setuptools_utils.get_package_metadata(self.dirname, 'package')
        self.assertEqual(md.long_description, 'Test\n====\n')
        self.assertEqual(md.version, '0.0.1')

        self.assertEqual(md.install_requires, [
            'req1',
            'req2[opt2]',
            'req3 >= 1.0',
            'req4; python_version > "2.6"',
        ])
        self.assertEqual(md.tests_require, [
            'req9',
        ])

        self.assertEqual(md.extras_require, {
            'package_opt_1': [
                'req7',
            ],
            'package_opt_2': [
                'req10[option10]',
                'req8[opt8a, opt8b]',
                'req9[opt9a, opt9b]',
            ],
            'tests': [
                'req9',
            ],
            'docs': [
                'req10',
                'req11',
                'req12[opt12a, opt12b] <= 1.0, >= 2.0; python_version>="2.7"',
                'req13[opt13a, opt13b]; python_version >= "2.7"',
                'req14[opt13a, opt13b]; python_version >= "2.7"',
                'req15; python_version >= "2.7"',
                'req16',
                'req17',
                'req18',
            ],
            'all': [
                'req10',
                'req10[option10]',
                'req11',
                'req12[opt12a, opt12b] <= 1.0, >= 2.0; python_version>="2.7"',
                'req13[opt13a, opt13b]; python_version >= "2.7"',
                'req14[opt13a, opt13b]; python_version >= "2.7"',
                'req15; python_version >= "2.7"',
                'req16',
                'req17',
                'req18',
                'req7',
                'req8[opt8a, opt8b]',
                'req9',
                'req9[opt9a, opt9b]',
            ],
        })

        self.assertEqual(md.dependency_links, [
            'git+https://github.com/opt/req10.git@branch',
            'git+https://github.com/opt/req14.git',
            'git+https://github.com/opt/req15.git',
            'git+https://github.com/opt/req16.git',
            'git+https://github.com/opt/req17.git',
            'git+https://github.com/opt/req18.git@branch',
        ])

    def test_get_package_metadata_tests_require_error(self):
        with open(os.path.join(self.dirname, 'requirements.optional.txt'), 'w') as file:
            file.write('[tests]\n')
            file.write('req1\n')

        with self.assertRaisesRegexp(Exception, '^Test dependencies should be defined in `tests/requirements`$'):
            setuptools_utils.get_package_metadata(self.dirname, 'package')

    def test_get_package_metadata_docs_require_error(self):
        with open(os.path.join(self.dirname, 'requirements.optional.txt'), 'w') as file:
            file.write('[docs]\n')
            file.write('req1\n')

        with self.assertRaisesRegexp(Exception, '^Documentation dependencies should be defined in `docs/requirements`$'):
            setuptools_utils.get_package_metadata(self.dirname, 'package')

    def test_PackageMetadata(self):
        setuptools_utils.core.PackageMetadata()

    def test_convert_readme_md_to_rst(self):
        setuptools_utils.convert_readme_md_to_rst(self.dirname)

        with open(os.path.join(self.dirname, 'README.rst'), 'r') as file:
            self.assertEqual(file.read(), 'Test\n====\n')

    def test_get_long_description(self):
        setuptools_utils.convert_readme_md_to_rst(self.dirname)
        self.assertEqual(setuptools_utils.get_long_description(self.dirname), 'Test\n====\n')

    def test_get_long_description_no_rst(self):
        self.assertEqual(setuptools_utils.get_long_description(self.dirname), '')

    def test_get_version(self):
        self.assertEqual(setuptools_utils.get_version(self.dirname, 'package'), '0.0.1')

    def test_parse_requirements_file(self):
        reqs, links = setuptools_utils.parse_requirements_file(os.path.join(self.dirname, 'requirements.txt'))
        self.assertEqual(reqs, [
            'req1',
            'req1',
            'req2[opt2]',
            'req3 >= 1.0',
            'req4; python_version > "2.6"',
        ])
        self.assertEqual(links, [])

        reqs, links = setuptools_utils.parse_requirements_file(os.path.join(self.dirname, 'tests', 'requirements.txt'))
        self.assertEqual(reqs, ['req9'])
        self.assertEqual(links, [])

        reqs, links = setuptools_utils.parse_requirements_file(os.path.join(self.dirname, 'docs', 'requirements.txt'))
        self.assertEqual(reqs, [
            'req1',
            'req1',
            'req2[opt2]',
            'req3 >= 1.0',
            'req10',
            'req11',
            'req12[opt12a, opt12b] <= 1.0, >= 2.0; python_version>="2.7"',
            'req13[opt13a, opt13b]; python_version >= "2.7"',
            'req14[opt13a, opt13b]; python_version >= "2.7"',
            'req15; python_version >= "2.7"',
            'req16',
            'req17',
            'req18',
        ])
        self.assertEqual(sorted(links), [
            'git+https://github.com/opt/req14.git',
            'git+https://github.com/opt/req15.git',
            'git+https://github.com/opt/req16.git',
            'git+https://github.com/opt/req17.git',
            'git+https://github.com/opt/req18.git@branch',
        ])

        reqs, links = setuptools_utils.parse_requirements_file(os.path.join(self.dirname, 'NONE'))
        self.assertEqual(reqs, [])
        self.assertEqual(links, [])

    def test_parse_optional_requirements_file(self):
        reqs, links = setuptools_utils.parse_optional_requirements_file(os.path.join(self.dirname, 'requirements.optional.txt'))
        self.assertEqual(reqs, {
            'package_opt_1': [
                'req7',
            ],
            'package_opt_2': [
                'req8[opt8a, opt8b]',
                'req9[opt9a, opt9b]',
                'req10[option10]',
            ],
        })
        self.assertEqual(links, [
            'git+https://github.com/opt/req10.git@branch',
        ])

        reqs, links = setuptools_utils.parse_optional_requirements_file(os.path.join(self.dirname, 'NONE'))
        self.assertEqual(reqs, {})
        self.assertEqual(links, [])

    def test_parse_optional_requirements_file_error(self):
        filename = os.path.join(self.dirname, 'requirements.optional.txt')

        with open(filename, 'w') as file:
            file.write('[package_opt_1] #\n')
        with self.assertRaisesRegexp(Exception, '^Could not parse optional dependency: '):
            setuptools_utils.parse_optional_requirements_file(filename)

        with open(filename, 'w') as file:
            file.write('req1\n')
            file.write('[option1]\n')
            file.write('[req2]\n')
        with self.assertRaisesRegexp(Exception, '^Required dependencies should be not be '):
            setuptools_utils.parse_optional_requirements_file(filename)

    def test_parse_requirement_lines_error(self):
        with self.assertRaisesRegexp(Exception, '^Dependency could not be parsed: '):
            setuptools_utils.parse_requirement_lines(['req2 #git+https://github.com/opt/req1.git#egg=req1'])

    def test_install_dependencies(self):
        setuptools_utils.install_dependencies(['setuptools'])

    def test_get_console_scripts(self):
        os.mkdir(os.path.join(self.dirname, 'package.egg-info'))
        with open(os.path.join(self.dirname, 'package.egg-info', 'entry_points.txt'), 'w') as file:
            file.write('[console_scripts]\nentry1=package.__main__1:main\n')

        scripts = setuptools_utils.get_console_scripts(self.dirname, 'package')
        self.assertEqual(scripts, {
            'entry1': 'package.__main__1:main',
        })

    def test_get_console_scripts_no_egg(self):
        scripts = setuptools_utils.get_console_scripts(self.dirname, 'package')
        self.assertEqual(scripts, None)

    def test_add_console_scripts(self):
        os.mkdir(os.path.join(self.dirname, 'package.egg-info'))
        with open(os.path.join(self.dirname, 'package.egg-info', 'entry_points.txt'), 'w') as file:
            file.write('[console_scripts]\nentry1=package.__main__1:main\n')

        setuptools_utils.add_console_scripts(self.dirname, 'package', {'entry2': 'package.__main__2:main'})
        scripts = setuptools_utils.get_console_scripts(self.dirname, 'package')
        self.assertEqual(scripts, {
            'entry1': 'package.__main__1:main',
            'entry2': 'package.__main__2:main',
        })
