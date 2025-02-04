# Copyright 2022-2025 CRS4.
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
from repo2rocrate.utils import get_ci_wf_endpoint


def test_get_ci_wf_endpoint():
    endpoint = get_ci_wf_endpoint("https://github.com/crs4/foo", "main.yml")
    assert endpoint == "repos/crs4/foo/actions/workflows/main.yml"
    for url in "https://github.com/crs4", "https://github.com", "":
        with pytest.raises(ValueError):
            get_ci_wf_endpoint("https://github.com/crs4", "main.yml")
