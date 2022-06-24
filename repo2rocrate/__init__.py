# Copyright 2022 CRS4.
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

from importlib import import_module
from .version import VERSION

__version__ = VERSION
LANG_NAMES = ["nextflow", "snakemake", "galaxy"]
LANG_MODULES = {_: import_module(f".{_}", __name__) for _ in LANG_NAMES}


def find_workflow(root_dir):
    for name, module in LANG_MODULES.items():
        try:
            return name, module.find_workflow(root_dir)
        except RuntimeError:
            pass
    raise RuntimeError(f"Workflow file not found in {root_dir}")
