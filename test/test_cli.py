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

import shutil

import pytest
import repo2rocrate
from click.testing import CliRunner
from rocrate.rocrate import ROCrate
from repo2rocrate.cli import cli

SNAKEMAKE_ID = "https://w3id.org/workflowhub/workflow-ro-crate#snakemake"


@pytest.mark.parametrize("to_zip", [False, True])
def test_default(data_dir, tmpdir, monkeypatch, to_zip):
    repo_name = "fair-crcc-send-data"
    root = tmpdir / repo_name
    crate_zip = tmpdir / f"{repo_name}.crate.zip"
    shutil.copytree(data_dir / repo_name, root)
    monkeypatch.chdir(root)
    runner = CliRunner()
    result = runner.invoke(cli, ["-o", crate_zip] if to_zip else [])
    assert result.exit_code == 0
    if to_zip:
        assert crate_zip.is_file()
        crate_dir = tmpdir / f"{repo_name}-crate"
        shutil.unpack_archive(crate_zip, crate_dir)
    else:
        crate_dir = root
    crate = ROCrate(crate_dir)
    workflow = crate.mainEntity
    assert workflow.id == "workflow/Snakefile"
    assert workflow["name"] == crate.root_dataset["name"] == repo_name
    language = workflow["programmingLanguage"]
    assert language.id == SNAKEMAKE_ID
    assert language["version"] == "6.5.0"
    image = crate.get("images/rulegraph.svg")
    assert image
    assert set(image.type) == {"File", "ImageObject"}
    assert workflow["image"] is image
    expected_data_entities = [
        ("LICENSE", "File"),
        ("README.md", "File"),
        ("config", "Dataset"),
        (".tests/integration", ["Dataset", "SoftwareSourceCode"]),
        ("workflow/rules", ["Dataset", "SoftwareSourceCode"]),
        ("workflow/schemas", "Dataset"),
        ("workflow/scripts", ["Dataset", "SoftwareSourceCode"]),
    ]
    for relpath, type_ in expected_data_entities:
        entity = crate.get(relpath)
        assert entity, f"{relpath} not listed in crate metadata"
        assert entity.type == type_
        p = crate_dir / relpath
        assert p.is_file() if type_ == "File" else p.is_dir()
    unlisted = crate_dir / "workflow/rules/common.smk"
    assert not crate.get(str(unlisted))
    assert unlisted.is_file()


def test_options(data_dir, tmpdir):
    repo_name = "fair-crcc-send-data"
    root = data_dir / repo_name
    wf_path = root / "pyproject.toml"
    crate_dir = tmpdir / f"{repo_name}-crate"
    repo_url = f"https://github.com/crs4/{repo_name}"
    wf_name = "spam"
    wf_version = "3.14"
    lang_version = "9.9.0"
    license = "http://example.org/license"
    ci_workflow = "conventional-prs.yml"
    diagram = "images/rulegraph.dot"
    runner = CliRunner()
    # fmt: off
    result = runner.invoke(cli, [
        "-r", str(root),
        "-l", "snakemake",
        "-w", str(wf_path),
        "-o", str(crate_dir),
        "--repo-url", f"https://github.com/crs4/{repo_name}",
        "--wf-name", wf_name,
        "--wf-version", wf_version,
        "--lang-version", lang_version,
        "--license", license,
        "--ci-workflow", ci_workflow,
        "--diagram", diagram,
    ])
    # fmt: on
    assert result.exit_code == 0
    assert crate_dir.is_dir()
    crate = ROCrate(crate_dir)
    workflow = crate.mainEntity
    assert workflow.id == wf_path.name
    assert workflow["name"] == crate.root_dataset["name"] == wf_name
    assert workflow["version"] == wf_version
    image = crate.get(diagram)
    assert image
    assert set(image.type) == {"File", "ImageObject"}
    assert workflow["image"] is image
    language = workflow["programmingLanguage"]
    assert language.id == SNAKEMAKE_ID
    assert language["version"] == lang_version
    assert workflow["url"] == crate.root_dataset["isBasedOn"] == repo_url
    instance = [_ for _ in crate.get_entities() if _.type == "TestInstance"][0]
    assert instance["resource"] == f"repos/crs4/{repo_name}/actions/workflows/{ci_workflow}"


def test_version():
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert result.output.strip() == repo2rocrate.__version__
