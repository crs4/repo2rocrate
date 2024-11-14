# Copyright 2022-2024 CRS4.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pytest
from repo2rocrate import find_workflow


def test_find_workflow(tmpdir):
    root = tmpdir / "repo"
    root.mkdir()
    with pytest.raises(RuntimeError):
        find_workflow(root)
    cases = [("nextflow", "main.nf"), ("snakemake", "Snakefile"), ("galaxy", "foo.ga")]
    for lang, wf_name in cases:
        wf_path = root / wf_name
        wf_path.touch()
        assert find_workflow(root) == (lang, wf_path)
        wf_path.unlink()
