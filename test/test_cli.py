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

import shutil

from click.testing import CliRunner
from repo2rocrate.cli import cli
from rocrate.rocrate import ROCrate


SNAKEMAKE_ID = "https://w3id.org/workflowhub/workflow-ro-crate#snakemake"


def test_default(data_dir, tmpdir, monkeypatch):
    repo_name = "fair-crcc-send-data"
    root = tmpdir / repo_name
    shutil.copytree(data_dir / repo_name, root)
    monkeypatch.chdir(root)
    runner = CliRunner()
    result = runner.invoke(cli, [])
    assert result.exit_code == 0
    crate_zip = root / f"{repo_name}.crate.zip"
    assert (crate_zip).is_file()
    crate_dir = tmpdir / f"{repo_name}-crate"
    shutil.unpack_archive(crate_zip, crate_dir)
    crate = ROCrate(crate_dir)
    workflow = crate.mainEntity
    assert workflow.id == "workflow/Snakefile"
    assert workflow["name"] == repo_name
    exp_files = [
        "LICENSE",
        "README.md",
        "config/example_config.yml",
        "workflow/rules/common.smk",
        "workflow/rules/encryption.smk",
        "workflow/rules/index.smk",
        "workflow/rules/upload.smk",
        "workflow/schemas/config.schema.yml",
        "workflow/scripts/gen_final_index.py",
        "workflow/scripts/gen_rename_index.py",
    ]
    for relpath in exp_files:
        assert (crate_dir / relpath).is_file()
        entity = crate.get(relpath)
        assert entity.type == "File"
    for relpath in [".tests/integration"]:
        assert (crate_dir / relpath).is_dir()
        entity = crate.get(relpath)
        assert entity.type == "Dataset"


def test_options(data_dir, tmpdir):
    repo_name = "fair-crcc-send-data"
    root = data_dir / repo_name
    crate_dir = tmpdir / f"{repo_name}-crate"
    repo_url = f"https://github.com/crs4/{repo_name}"
    version = "3.14"
    lang_version = "9.9.0"
    license = "http://example.org/license"
    ci_workflow = "conventional-prs.yml"
    runner = CliRunner()
    result = runner.invoke(cli, [
        "-r", str(root),
        "-l", "snakemake",
        "-o", str(crate_dir),
        "--repo-url", f"https://github.com/crs4/{repo_name}",
        "--version", version,
        "--lang-version", lang_version,
        "--license", license,
        "--ci-workflow", ci_workflow,
    ])
    assert result.exit_code == 0
    assert crate_dir.is_dir()
    crate = ROCrate(crate_dir)
    workflow = crate.mainEntity
    assert workflow["name"] == repo_name
    assert workflow["version"] == version
    language = workflow["programmingLanguage"]
    assert language.id == SNAKEMAKE_ID
    assert language["version"] == lang_version
    assert workflow["url"] == crate.root_dataset["isBasedOn"] == repo_url
    instance = [_ for _ in crate.get_entities() if _.type == "TestInstance"][0]
    assert instance["resource"] == f"repos/crs4/{repo_name}/actions/workflows/{ci_workflow}"
