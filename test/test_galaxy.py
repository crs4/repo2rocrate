# Copyright 2022 CRS4.
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
from repo2rocrate.galaxy import find_workflow, make_crate


GALAXY_ID = "https://w3id.org/workflowhub/workflow-ro-crate#galaxy"
PLANEMO_ID = "https://w3id.org/ro/terms/test#PlanemoEngine"


@pytest.mark.filterwarnings("ignore")
def test_find_workflow(tmpdir):
    root = tmpdir / "galaxy-repo"
    root.mkdir()
    with pytest.raises(RuntimeError):
        find_workflow(root)
    wf_path = root / "foo.ga"
    with open(wf_path, "wt"):
        pass
    assert find_workflow(root) == wf_path
    new_wf_path = root / "main.ga"
    with open(new_wf_path, "wt"):
        pass
    assert find_workflow(root) == new_wf_path


def test_parallel_accession_download(data_dir):
    repo_name = "parallel-accession-download"
    root = data_dir / repo_name
    repo_url = f"https://github.com/iwc-workflows/{repo_name}"
    crate = make_crate(root, repo_url=repo_url)
    assert crate.root_dataset["license"] == "MIT"
    # workflow
    workflow = crate.mainEntity
    assert workflow.id == "parallel-accession-download.ga"
    assert workflow["name"] == "parallel-accession-download/main"
    assert workflow["version"] == "0.1.3"
    assert not workflow.get("image")
    language = workflow["programmingLanguage"]
    assert language.id == GALAXY_ID
    assert workflow["url"] == crate.root_dataset["isBasedOn"] == repo_url
    # workflow testing metadata
    suite = crate.root_dataset["mentions"]
    assert suite
    if isinstance(suite, list):
        assert len(suite) == 1
        suite = suite[0]
    assert suite.type == "TestSuite"
    assert suite["mainEntity"] is workflow
    instance = suite["instance"]
    assert instance
    if isinstance(instance, list):
        assert len(instance) == 1
        instance = instance[0]
    assert instance.type == "TestInstance"
    assert instance["url"] == "https://api.github.com"
    assert instance["resource"] == f"repos/iwc-workflows/{repo_name}/actions/workflows/wftest.yml"
    definition = suite["definition"]
    assert definition
    assert set(definition.type) == {"File", "TestDefinition"}
    engine = definition["conformsTo"]
    assert engine
    assert engine.id == PLANEMO_ID
    assert engine.type == "SoftwareApplication"
    # layout
    expected_data_entities = [
        ("CHANGELOG.md", "File"),
        ("README.md", "File"),
        (".dockstore.yml", "File"),
        ("test-data", "Dataset"),
    ]
    for relpath, type_ in expected_data_entities:
        entity = crate.get(relpath)
        assert entity, f"{relpath} not listed in crate metadata"
        assert entity.type == type_
