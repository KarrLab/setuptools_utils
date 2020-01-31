""" Tests for pkg_utils

:Author: Jonathan Karr <jonrkarr@gmail.com>
:Date: 2017-11-14
:Copyright: 2017, Karr Lab
:License: MIT
"""

import os
import pkg_utils
import shutil
import tempfile
import unittest


class TestCase(unittest.TestCase):

    def setUp(self):
        self.dirname = dirname = tempfile.mkdtemp()

        os.mkdir(os.path.join(self.dirname, 'package'))
        os.mkdir(os.path.join(self.dirname, 'tests'))
        os.mkdir(os.path.join(self.dirname, 'docs'))

        with open(os.path.join(dirname, 'package', '_version.py'), 'w') as file:
            file.write("__version__ = '0.0.1'")

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
            file.write('#comment\n')
            file.write('[package_opt_1]\n')
            file.write('req7\n')
            file.write('\n')
            file.write('[package_opt_2]\n')
            file.write('req8[opt8a,opt8b]\n')
            file.write('req9[opt9a, opt9b]\n')
            file.write('git+https://github.com/opt/req10.git@branch#egg=req10-10.1.2[option10] #comment\n')

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
            file.write('git+https://github.com/opt/req14.git#egg=req14-14.1.2[opt13a,opt13b]; python_version >= "2.7"\n')
            file.write('git+https://github.com/opt/req15.git#egg=req15-15.1.2 ; python_version >= "2.7"\n')
            file.write('git+https://github.com/opt/req16.git#egg=req16-16.1.2\n')
            file.write('git+https://github.com/opt/req17.git#egg=req17-17.1.2 #comment\n')
            file.write('git+https://github.com/opt/req18.git@branch#egg=req18-18.1.2 #comment\n')

    def tearDown(self):
        shutil.rmtree(self.dirname)

    def test_get_package_metadata(self):
        pkg_utils.convert_readme_md_to_rst(self.dirname)
        md = pkg_utils.get_package_metadata(self.dirname, 'package')
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
            'git+https://github.com/opt/req10.git@branch#egg=req10-10.1.2',
            'git+https://github.com/opt/req14.git#egg=req14-14.1.2',
            'git+https://github.com/opt/req15.git#egg=req15-15.1.2',
            'git+https://github.com/opt/req16.git#egg=req16-16.1.2',
            'git+https://github.com/opt/req17.git#egg=req17-17.1.2',
            'git+https://github.com/opt/req18.git@branch#egg=req18-18.1.2',
        ])

    def test_get_package_metadata_tests_require_error(self):
        with open(os.path.join(self.dirname, 'requirements.optional.txt'), 'w') as file:
            file.write('[tests]\n')
            file.write('req1\n')

        with self.assertRaisesRegex(ValueError, '^Test dependencies should be defined in `tests/requirements`$'):
            pkg_utils.get_package_metadata(self.dirname, 'package')

    def test_get_package_metadata_docs_require_error(self):
        with open(os.path.join(self.dirname, 'requirements.optional.txt'), 'w') as file:
            file.write('[docs]\n')
            file.write('req1\n')

        with self.assertRaisesRegex(ValueError, '^Documentation dependencies should be defined in `docs/requirements`$'):
            pkg_utils.get_package_metadata(self.dirname, 'package')

    def test_PackageMetadata(self):
        pkg_utils.core.PackageMetadata()

    def test_convert_readme_md_to_rst(self):
        pkg_utils.convert_readme_md_to_rst(self.dirname)

        with open(os.path.join(self.dirname, 'README.rst'), 'r') as file:
            self.assertEqual(file.read(), 'Test\n====\n')

    def test_get_long_description(self):
        pkg_utils.convert_readme_md_to_rst(self.dirname)
        self.assertEqual(pkg_utils.get_long_description(self.dirname), 'Test\n====\n')

    def test_get_long_description_no_rst(self):
        self.assertEqual(pkg_utils.get_long_description(self.dirname), '')

    def test_get_version(self):
        self.assertEqual(pkg_utils.get_version(self.dirname, 'package'), '0.0.1')

    def test_expand_package_data_filename_patterns(self):
        def touch(filename):
            with open(filename, 'w') as file:
                pass

        os.mkdir(os.path.join(self.dirname, 'pkg1'))
        os.mkdir(os.path.join(self.dirname, 'pkg1', 'dir1a'))
        os.mkdir(os.path.join(self.dirname, 'pkg1', 'dir1b'))
        os.mkdir(os.path.join(self.dirname, 'pkg1', 'dir1b', 'dir1c'))
        os.mkdir(os.path.join(self.dirname, 'pkg1', 'dir1b', 'dir1d'))
        os.mkdir(os.path.join(self.dirname, 'pkg1', 'dir1b', 'dir1d', 'dir1e'))
        os.mkdir(os.path.join(self.dirname, 'pkg2'))
        os.mkdir(os.path.join(self.dirname, 'pkg2', 'dir2a'))
        os.mkdir(os.path.join(self.dirname, 'pkg2', 'dir2b'))
        os.mkdir(os.path.join(self.dirname, 'pkg3'))
        os.mkdir(os.path.join(self.dirname, 'pkg3', 'dir3a'))
        os.mkdir(os.path.join(self.dirname, 'pkg3', 'dir3a', 'dir3b'))
        os.mkdir(os.path.join(self.dirname, 'pkg3', 'dir3a', 'dir3b', 'dir3c'))
        os.mkdir(os.path.join(self.dirname, 'pkg3', 'dir3d'))

        touch(os.path.join(self.dirname, 'pkg1', 'file-1.txt'))
        touch(os.path.join(self.dirname, 'pkg1', 'file-0.pdf'))
        touch(os.path.join(self.dirname, 'pkg1', 'dir1a', 'file1.txt'))
        touch(os.path.join(self.dirname, 'pkg1', 'dir1a', 'file2.txt'))
        touch(os.path.join(self.dirname, 'pkg1', 'dir1a', 'file3.pdf'))
        touch(os.path.join(self.dirname, 'pkg1', 'dir1a', 'file4.pdf'))
        touch(os.path.join(self.dirname, 'pkg1', 'dir1b', 'file5.txt'))
        touch(os.path.join(self.dirname, 'pkg1', 'dir1b', 'file6.pdf'))
        touch(os.path.join(self.dirname, 'pkg1', 'dir1b', 'dir1c', 'file7.txt'))
        touch(os.path.join(self.dirname, 'pkg1', 'dir1b', 'dir1c', 'file8.pdf'))
        touch(os.path.join(self.dirname, 'pkg1', 'dir1b', 'dir1d', 'dir1e', 'file9.txt'))
        touch(os.path.join(self.dirname, 'pkg1', 'dir1b', 'dir1d', 'dir1e', 'file10.pdf'))

        touch(os.path.join(self.dirname, 'pkg3', 'dir3a', 'file11.txt'))
        touch(os.path.join(self.dirname, 'pkg3', 'dir3a', 'dir3b', 'file12.pdf'))
        touch(os.path.join(self.dirname, 'pkg3', 'dir3a', 'dir3b', 'dir3c', 'file13.txt'))
        touch(os.path.join(self.dirname, 'pkg3', 'dir3d', 'file14.pdf'))

        self.assertEqual(pkg_utils.core.expand_package_data_filename_patterns(self.dirname), {})

        package_data_filename_patterns = {
            'pkg1': [
                '*',
                '**/*',
            ],
            'pkg2': [
                '*',
                '**/*',
            ],
            'pkg3': [
                '*',
                '**/*',
            ],
        }
        package_data = pkg_utils.core.expand_package_data_filename_patterns(self.dirname,
                                                                            package_data_filename_patterns=package_data_filename_patterns)

        self.assertEqual(package_data, {
            'pkg1': sorted([
                os.path.join('file-1.txt'),
                os.path.join('file-0.pdf'),
                os.path.join('dir1a', 'file1.txt'),
                os.path.join('dir1a', 'file2.txt'),
                os.path.join('dir1a', 'file3.pdf'),
                os.path.join('dir1a', 'file4.pdf'),
                os.path.join('dir1b', 'file5.txt'),
                os.path.join('dir1b', 'file6.pdf'),
                os.path.join('dir1b', 'dir1c', 'file7.txt'),
                os.path.join('dir1b', 'dir1c', 'file8.pdf'),
                os.path.join('dir1b', 'dir1d', 'dir1e', 'file9.txt'),
                os.path.join('dir1b', 'dir1d', 'dir1e', 'file10.pdf'),
            ]),
            'pkg2': [],
            'pkg3': sorted([
                os.path.join('dir3a', 'file11.txt'),
                os.path.join('dir3a', 'dir3b', 'file12.pdf'),
                os.path.join('dir3a', 'dir3b', 'dir3c', 'file13.txt'),
                os.path.join('dir3d', 'file14.pdf'),
            ]),
        })

        package_data_filename_patterns = {
            'pkg1': [
                'dir1b/**/*',
            ],
            'pkg3': [
                '*',
                'dir3a/**/dir3c/*',
            ],
        }
        package_data = pkg_utils.core.expand_package_data_filename_patterns(self.dirname,
                                                                            package_data_filename_patterns=package_data_filename_patterns)

        self.assertEqual(package_data, {
            'pkg1': sorted([
                os.path.join('dir1b', 'file5.txt'),
                os.path.join('dir1b', 'file6.pdf'),
                os.path.join('dir1b', 'dir1c', 'file7.txt'),
                os.path.join('dir1b', 'dir1c', 'file8.pdf'),
                os.path.join('dir1b', 'dir1d', 'dir1e', 'file9.txt'),
                os.path.join('dir1b', 'dir1d', 'dir1e', 'file10.pdf'),
            ]),
            'pkg3': sorted([
                os.path.join('dir3a', 'dir3b', 'dir3c', 'file13.txt'),
            ]),
        })

        self.assertEqual(pkg_utils.core.expand_package_data_filename_patterns(self.dirname, package_data_filename_patterns={
            'pkg1': [
                '*',
            ],
            'pkg2': [
                '*',
            ],
            'pkg3': [
                '*',
            ],
        }), {
            'pkg1': sorted([
                os.path.join('file-1.txt'),
                os.path.join('file-0.pdf'),
            ]),
            'pkg2': [],
            'pkg3': sorted([
            ]),
        })

        package_data_filename_patterns = {
            'pkg1': [
                '**/*',
            ],
            'pkg2': [
                '**/*',
            ],
            'pkg3': [
                '**/*',
            ],
        }
        package_data = pkg_utils.core.expand_package_data_filename_patterns(
            self.dirname, package_data_filename_patterns=package_data_filename_patterns)
        self.assertEqual(package_data, {
            'pkg1': sorted([
                os.path.join('file-1.txt'),
                os.path.join('file-0.pdf'),
                os.path.join('dir1a', 'file1.txt'),
                os.path.join('dir1a', 'file2.txt'),
                os.path.join('dir1a', 'file3.pdf'),
                os.path.join('dir1a', 'file4.pdf'),
                os.path.join('dir1b', 'file5.txt'),
                os.path.join('dir1b', 'file6.pdf'),
                os.path.join('dir1b', 'dir1c', 'file7.txt'),
                os.path.join('dir1b', 'dir1c', 'file8.pdf'),
                os.path.join('dir1b', 'dir1d', 'dir1e', 'file9.txt'),
                os.path.join('dir1b', 'dir1d', 'dir1e', 'file10.pdf'),
            ]),
            'pkg2': [],
            'pkg3': sorted([
                os.path.join('dir3a', 'file11.txt'),
                os.path.join('dir3a', 'dir3b', 'file12.pdf'),
                os.path.join('dir3a', 'dir3b', 'dir3c', 'file13.txt'),
                os.path.join('dir3d', 'file14.pdf'),
            ]),
        })

        self.assertEqual(pkg_utils.core.expand_package_data_filename_patterns(self.dirname, package_data_filename_patterns={
            'pkg1': [
                '*.txt',
                '**/*.txt',
            ],
            'pkg2': [
                '*.txt',
                '**/*.txt',
            ],
            'pkg3': [
                '*.txt',
                '**/*.txt',
            ],
        }), {
            'pkg1': sorted([
                os.path.join('file-1.txt'),
                os.path.join('dir1a', 'file1.txt'),
                os.path.join('dir1a', 'file2.txt'),
                os.path.join('dir1b', 'file5.txt'),
                os.path.join('dir1b', 'dir1c', 'file7.txt'),
                os.path.join('dir1b', 'dir1d', 'dir1e', 'file9.txt'),
            ]),
            'pkg2': [],
            'pkg3': sorted([
                os.path.join('dir3a', 'file11.txt'),
                os.path.join('dir3a', 'dir3b', 'dir3c', 'file13.txt'),
            ]),
        })

        self.assertEqual(pkg_utils.core.expand_package_data_filename_patterns(self.dirname, package_data_filename_patterns={
            'pkg1': [
                '*.pdf',
                '**/*.pdf',
            ],
        }), {
            'pkg1': sorted([
                os.path.join('file-0.pdf'),
                os.path.join('dir1a', 'file3.pdf'),
                os.path.join('dir1a', 'file4.pdf'),
                os.path.join('dir1b', 'file6.pdf'),
                os.path.join('dir1b', 'dir1c', 'file8.pdf'),
                os.path.join('dir1b', 'dir1d', 'dir1e', 'file10.pdf'),
            ]),
        })

    def test_parse_requirements_file(self):
        reqs, links = pkg_utils.parse_requirements_file(os.path.join(self.dirname, 'requirements.txt'))
        self.assertEqual(reqs, [
            'req1',
            'req1',
            'req2[opt2]',
            'req3 >= 1.0',
            'req4; python_version > "2.6"',
        ])
        self.assertEqual(links, [])

        reqs, links = pkg_utils.parse_requirements_file(os.path.join(self.dirname, 'tests', 'requirements.txt'))
        self.assertEqual(reqs, ['req9'])
        self.assertEqual(links, [])

        reqs, links = pkg_utils.parse_requirements_file(os.path.join(self.dirname, 'docs', 'requirements.txt'))
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
            'git+https://github.com/opt/req14.git#egg=req14-14.1.2',
            'git+https://github.com/opt/req15.git#egg=req15-15.1.2',
            'git+https://github.com/opt/req16.git#egg=req16-16.1.2',
            'git+https://github.com/opt/req17.git#egg=req17-17.1.2',
            'git+https://github.com/opt/req18.git@branch#egg=req18-18.1.2',
        ])

        reqs, links = pkg_utils.parse_requirements_file(os.path.join(self.dirname, 'NONE'))
        self.assertEqual(reqs, [])
        self.assertEqual(links, [])

    def test_parse_optional_requirements_file(self):
        reqs, links = pkg_utils.parse_optional_requirements_file(os.path.join(self.dirname, 'requirements.optional.txt'))
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
            'git+https://github.com/opt/req10.git@branch#egg=req10-10.1.2',
        ])

        reqs, links = pkg_utils.parse_optional_requirements_file(os.path.join(self.dirname, 'NONE'))
        self.assertEqual(reqs, {})
        self.assertEqual(links, [])

    def test_parse_optional_requirements_file_error(self):
        filename = os.path.join(self.dirname, 'requirements.optional.txt')

        with open(filename, 'w') as file:
            file.write('[package_opt_1] #\n')
        with self.assertRaisesRegex(ValueError, '^Could not parse optional dependency: '):
            pkg_utils.parse_optional_requirements_file(filename)

        with open(filename, 'w') as file:
            file.write('req1\n')
            file.write('[option1]\n')
            file.write('[req2]\n')
        with self.assertRaisesRegex(ValueError, '^Required dependencies should not be '):
            pkg_utils.parse_optional_requirements_file(filename)

    def test_parse_requirement_with_uri(self):
        reqs, links = pkg_utils.parse_requirement_lines(['req1'])
        self.assertEqual(reqs, ['req1'])
        self.assertEqual(links, [])

        reqs, links = pkg_utils.parse_requirement_lines(['req1'], include_uri=True)
        self.assertEqual(reqs, ['req1'])
        self.assertEqual(links, [])

        reqs, links = pkg_utils.parse_requirement_lines(['git+https://github.com/opt/req1.git#egg=req1-1.1.2&subdirectory=subdir'])
        self.assertEqual(reqs, ['req1'])
        self.assertEqual(links, ['git+https://github.com/opt/req1.git#egg=req1-1.1.2&subdirectory=subdir'])

        reqs, links = pkg_utils.parse_requirement_lines(['git+https://github.com/opt/req1.git#egg=req1-1.1.2&subdirectory=subdir'],
                                                        include_uri=True)
        self.assertEqual(reqs, ['git+https://github.com/opt/req1.git#egg=req1&subdirectory=subdir'])
        self.assertEqual(links, ['git+https://github.com/opt/req1.git#egg=req1-1.1.2&subdirectory=subdir'])

        reqs, links = pkg_utils.parse_requirement_lines(['git+https://github.com/opt/req1.git#egg=req1-1.1.2&subdirectory=subdir > 1.1.2'])
        self.assertEqual(reqs, ['req1 > 1.1.2'])
        self.assertEqual(links, ['git+https://github.com/opt/req1.git#egg=req1-1.1.2&subdirectory=subdir'])

        reqs, links = pkg_utils.parse_requirement_lines(['git+https://github.com/opt/req1.git#egg=req1-1.1.2&subdirectory=subdir > 1.1.2'],
                                                        include_uri=True)
        self.assertEqual(reqs, ['git+https://github.com/opt/req1.git#egg=req1&subdirectory=subdir > 1.1.2'])
        self.assertEqual(links, ['git+https://github.com/opt/req1.git#egg=req1-1.1.2&subdirectory=subdir'])

    def test_parse_requirement_with_subdirectory(self):
        reqs, links = pkg_utils.parse_requirement_lines(['git+https://github.com/opt/req1.git#egg=req1-1.1.2&subdirectory=subdir'])
        self.assertEqual(reqs, ['req1'])
        self.assertEqual(links, ['git+https://github.com/opt/req1.git#egg=req1-1.1.2&subdirectory=subdir'])

        reqs, links = pkg_utils.parse_requirement_lines(['git+https://github.com/opt/req1.git#egg=req1-1.1.2&subdirectory=subdir > 1.1.2'])
        self.assertEqual(reqs, ['req1 > 1.1.2'])
        self.assertEqual(links, ['git+https://github.com/opt/req1.git#egg=req1-1.1.2&subdirectory=subdir'])

    def test_parse_requirement_with_hash_option(self):
        reqs, links = pkg_utils.parse_requirement_lines(['git+https://github.com/opt/req1.git#egg=req1-1.2.3&sha256=44ddfb12'])
        self.assertEqual(reqs, ['req1'])
        self.assertEqual(links, ['git+https://github.com/opt/req1.git#egg=req1-1.2.3&sha256=44ddfb12'])

        reqs, links = pkg_utils.parse_requirement_lines(['git+https://github.com/opt/req1.git#egg=req1-1.2.3&sha256=44ddfb12 >= 1.1.2'])
        self.assertEqual(reqs, ['req1 >= 1.1.2'])
        self.assertEqual(links, ['git+https://github.com/opt/req1.git#egg=req1-1.2.3&sha256=44ddfb12'])

    def test_parse_requirement_invalid_comment_before_egg(self):
        with self.assertRaisesRegex(ValueError, ''):
            pkg_utils.parse_requirement_lines(['req2 #git+https://github.com/opt/req1.git#egg=req1'])

    def test_parse_requirement_invalid_name(self):
        with self.assertRaisesRegex(ValueError, 'Dependency could not be parsed:'):
            pkg_utils.parse_requirement_lines(['git+https://github.com/opt/req1.git#egg=req-ui-r-ment'])

    def test_parse_requirement_with_editable_option(self):
        with self.assertRaisesRegex(ValueError, 'Editable option is not supported'):
            pkg_utils.parse_requirement_lines(['-e git+https://github.com/opt/req1.git#egg=req1'])

    def test_parse_requirement_local_file_option(self):
        with self.assertRaisesRegex(ValueError, 'Local file option is not supported'):
            pkg_utils.parse_requirement_lines(['local_dir/req1.git#egg=req1'])

    def test_parse_requirement_without_version_hint(self):
        with self.assertRaisesRegex(ValueError, 'Version hints must be provided'):
            pkg_utils.parse_requirement_lines(['git+https://github.com/opt/req1.git#egg=req1'])

    def test_install_dependencies(self):
        pkg_utils.install_dependencies(['setuptools'])
        pkg_utils.install_dependencies(['setuptools'], upgrade=True)

    def test_get_console_scripts(self):
        os.mkdir(os.path.join(self.dirname, 'package.egg-info'))
        with open(os.path.join(self.dirname, 'package.egg-info', 'entry_points.txt'), 'w') as file:
            file.write('[console_scripts]\n')
            file.write('entry1=package.__main__1:main\n')
            file.write('pip=package.__main__2:main\n')

        scripts = pkg_utils.get_console_scripts(self.dirname, 'package')
        self.assertEqual(sorted(list(scripts.keys())), ['entry1', 'pip'])
        self.assertEqual(scripts['entry1'], {
            'function': 'package.__main__1:main',
        })
        self.assertEqual(scripts['pip']['function'], 'package.__main__2:main')

    def test_get_console_scripts_no_egg(self):
        scripts = pkg_utils.get_console_scripts(self.dirname, 'package')
        self.assertEqual(scripts, None)

    def test_add_console_scripts(self):
        egg_dir = os.path.join(self.dirname, 'package.egg-info')
        entry_points_filename = os.path.join(egg_dir, 'entry_points.txt')
        os.mkdir(egg_dir)
        with open(entry_points_filename, 'w') as file:
            file.write('[console_scripts]\n')
            file.write('entry1=package.__main__1:main\n')

        pkg_utils.add_console_scripts(self.dirname, 'package', {
            'entry2': {
                'function': 'package.__main__2:main',
            },
            'entry3': {
                'function': 'package.__main__3:main',
            }
        })

        scripts = pkg_utils.get_console_scripts(self.dirname, 'package')
        self.assertEqual(scripts, {
            'entry1': {
                'function': 'package.__main__1:main',
            },
            'entry2': {
                'function': 'package.__main__2:main',
            },
            'entry3': {
                'function': 'package.__main__3:main',
            },
        })

        # add no additional console scripts
        pkg_utils.add_console_scripts(self.dirname, 'package', {})

        scripts = pkg_utils.get_console_scripts(self.dirname, 'package')
        self.assertEqual(scripts, {
            'entry1': {
                'function': 'package.__main__1:main',
            },
            'entry2': {
                'function': 'package.__main__2:main',
            },
            'entry3': {
                'function': 'package.__main__3:main',
            },
        })
