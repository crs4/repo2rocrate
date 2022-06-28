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
from repo2rocrate.nextflow import find_workflow, get_metadata, make_crate


NEXTFLOW_ID = "https://w3id.org/workflowhub/workflow-ro-crate#nextflow"
REPO_NAME = "nf-core-foobar"


def test_find_workflow(tmpdir):
    root = tmpdir / "nextflow-repo"
    root.mkdir()
    with pytest.raises(RuntimeError):
        find_workflow(root)
    wf_path = root / "main.nf"
    wf_path.touch()
    assert find_workflow(root) == wf_path


def test_get_metadata(tmpdir, data_dir):
    metadata = get_metadata(data_dir / REPO_NAME / "nextflow.config")
    assert len(metadata) == 7
    assert metadata["name"] == "nf-core/foobar"
    assert metadata["author"] == "Simone Leo"
    assert metadata["homePage"] == "https://github.com/nf-core/foobar"
    assert metadata["description"] == "the foobar pipeline"
    assert metadata["mainScript"] == "main.nf"
    assert metadata["nextflowVersion"] == "!>=21.10.3"
    assert metadata["version"] == "0.1.0"
    config_file_path = tmpdir / "nextflow.config"
    config_file_path.write_text(
        "manifest{name='nf-core/foobar'\n"
        "version='0.1.0'}\n"
    )
    metadata = get_metadata(config_file_path)
    assert metadata["name"] == "nf-core/foobar"
    assert metadata["version"] == "0.1.0"


@pytest.mark.parametrize("defaults", [False, True])
def test_nf_core_foobar(data_dir, defaults):
    root = data_dir / REPO_NAME
    license = "MIT"
    kwargs = {"license": license}
    if defaults:
        repo_url = "https://github.com/nf-core/foobar"
        wf_version = "0.1.0"
        lang_version = "!>=21.10.3"
        ci_workflow = "ci.yml"
        diagram = None
        resource = f"repos/nf-core/foobar/actions/workflows/{ci_workflow}"
    else:
        repo_url = f"https://github.com/crs4/{REPO_NAME}"
        wf_version = "0.9.9"
        lang_version = "21.10.0"
        ci_workflow = "linting.yml"
        diagram = "docs/images/nf-core-foobar_logo_light.png"
        resource = f"repos/crs4/{REPO_NAME}/actions/workflows/{ci_workflow}"
        kwargs.update(repo_url=repo_url, wf_version=wf_version, lang_version=lang_version, license=license, ci_workflow=ci_workflow, diagram=diagram)
    crate = make_crate(root, **kwargs)
    assert crate.root_dataset["license"] == license
    # workflow
    workflow = crate.mainEntity
    assert workflow.id == "main.nf"
    assert workflow["name"] == "nf-core/foobar"
    assert workflow["version"] == wf_version
    if diagram:
        image = crate.get(diagram)
        assert image
        assert set(image.type) == {"File", "ImageObject"}
        assert workflow["image"] is image
    language = workflow["programmingLanguage"]
    assert language.id == NEXTFLOW_ID
    assert language["version"] == lang_version
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
    assert instance["resource"] == resource
    # layout
    expected_data_entities = [
        ("nextflow.config", "File"),
        ("README.md", "File"),
        ("nextflow_schema.json", "File"),
        ("CHANGELOG.md", "File"),
        ("LICENSE", "File"),
        ("CODE_OF_CONDUCT.md", "File"),
        ("CITATIONS.md", "File"),
        ("modules.json", "File"),
        ("assets", "Dataset"),
        ("bin", "Dataset"),
        ("conf", "Dataset"),
        ("docs", "Dataset"),
        ("docs/images", "Dataset"),
        ("lib", "Dataset"),
        ("modules", "Dataset"),
        ("modules/local", "Dataset"),
        ("modules/nf-core", "Dataset"),
        ("workflows", "Dataset"),
        ("subworkflows", "Dataset"),
    ]
    for relpath, type_ in expected_data_entities:
        entity = crate.get(relpath)
        assert entity, f"{relpath} not listed in crate metadata"
        assert entity.type == type_
