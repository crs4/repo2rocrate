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

from gen_crate import main
from rocrate.rocrate import ROCrate


SNAKEMAKE_ID = "https://w3id.org/workflowhub/workflow-ro-crate#snakemake"


class Args:
    pass


def test_fair_crcc_send_data(data_dir, tmpdir):
    repo_name = "fair-crcc-send-data"
    args = Args()
    args.root = data_dir / repo_name
    args.output = tmpdir / f"{repo_name}-crate"
    args.repo_url = f"https://github.com/crs4/{repo_name}"
    args.version = "0.1"  # made up
    args.lang_version = "6.5.0"
    args.license = "GPL-3.0"
    args.ci_workflow = "main.yml"
    main(args)
    crate = ROCrate(args.output)
    assert crate.root_dataset["license"] == args.license
    # workflow
    workflow = crate.mainEntity
    assert workflow.id == "workflow/Snakefile"
    assert workflow["name"] == repo_name
    assert workflow["version"] == args.version
    image = crate.get("images/rulegraph.svg")
    assert image
    assert set(image.type) == {"File", "ImageObject"}
    assert workflow["image"] is image
    language = workflow["programmingLanguage"]
    assert language.id == SNAKEMAKE_ID
    assert language["version"] == args.lang_version
    assert workflow["url"] == crate.root_dataset["isBasedOn"] == args.repo_url
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
    assert instance["resource"] == f"repos/crs4/{repo_name}/actions/workflows/{args.ci_workflow}"
    # layout
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
        assert (args.output / relpath).is_file()
        entity = crate.get(relpath)
        assert entity.type == "File"
    for relpath in [".tests/integration"]:
        assert (args.output / relpath).is_dir()
        entity = crate.get(relpath)
        assert entity.type == "Dataset"
