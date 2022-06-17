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

from repo2rocrate.nextflow import make_crate


NEXTFLOW_ID = "https://w3id.org/workflowhub/workflow-ro-crate#nextflow"


def test_nf_core_foobar(data_dir):
    repo_name = "nf-core-foobar"
    root = data_dir / repo_name
    repo_url = f"https://github.com/crs4/{repo_name}"
    version = "0.1.0"
    lang_version = "21.10.3"
    license = "MIT"
    ci_workflow = "ci.yml"
    diagram = "docs/images/nf-core-foobar_logo_light.png"
    crate = make_crate(root, repo_url=repo_url, version=version, lang_version=lang_version, license=license, ci_workflow=ci_workflow, diagram=diagram)
    assert crate.root_dataset["license"] == license
    # workflow
    workflow = crate.mainEntity
    assert workflow.id == "main.nf"
    assert workflow["name"] == repo_name
    assert workflow["version"] == version
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
    assert instance["resource"] == f"repos/crs4/{repo_name}/actions/workflows/{ci_workflow}"
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
