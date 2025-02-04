# Copyright 2022-2025 CRS4.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy
# of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import re
from pathlib import Path

from setuptools import setup

THIS_DIR = Path(__file__).absolute().parent


# don't import version.py so pip can run setup before installing dependencies
def get_version():
    pattern = r'^VERSION\s*=\s*"([^"]+)"'
    module = THIS_DIR / "repo2rocrate" / "version.py"
    code = module.read_text()
    return re.search(pattern, code, re.MULTILINE).groups()[0]


setup(
    name="repo2rocrate",
    version=get_version(),
    url="https://github.com/crs4/repo2rocrate",
    description="Generate RO-Crates from workflow repositories",
    long_description=(THIS_DIR / "README.md").read_text(),
    long_description_content_type="text/markdown",
    author="Simone Leo, Matthias Hörtenhuber",
    author_email="<simone.leo@crs4.it>, <mashehu3@gmail.com>",
    license="Apache-2.0",
    platforms=["Linux"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
        "Intended Audience :: Science/Research",
    ],
    packages=["repo2rocrate"],
    python_requires=">=3.9, <4",
    install_requires=["click", "pyyaml", "rocrate"],
    entry_points={
        "console_scripts": ["repo2rocrate=repo2rocrate.cli:cli"],
    },
    zip_safe=True,
)
