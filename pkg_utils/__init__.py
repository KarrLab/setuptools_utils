from .core import (PackageMetadata, get_package_metadata, convert_readme_md_to_rst, get_long_description, get_version,
                   expand_package_data_filename_patterns, get_dependencies, parse_requirements_file, parse_optional_requirements_file, 
                   parse_requirement_lines, install_dependencies, get_console_scripts, add_console_scripts)
import pkg_resources

# read version
from ._version import __version__
