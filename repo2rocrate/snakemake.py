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

"""\
Generate a Workflow Testing RO-Crate from a "best practices" Snakemake
workflow repository.

https://snakemake.readthedocs.io/en/stable/snakefiles/deployment.html
https://snakemake.github.io/snakemake-workflow-catalog/?rules=true
"""

from rocrate.rocrate import ROCrate
from snakemake.workflow import Workflow
from . import CI_WORKFLOW, GH_API_URL
from .utils import get_ci_wf_endpoint


WF_BASENAME = "Snakefile"
# "standard" resources will be included if present
STANDARD_DIRS = {
    ".tests/integration": "Integration tests for the workflow",
    ".tests/unit": "Unit tests for the workflow",
    "workflow": "Workflow folder",
    "config": "Configuration folder",
    "results": "Output files",
    "resources": "Retrieved resources",
    "workflow/rules": "Workflow rule module",
    "workflow/envs": "Conda environments",
    "workflow/scripts": "Scripts folder",
    "workflow/notebooks": "Notebooks folder",
    "workflow/report": "Report caption files",
    "workflow/schemas": "Validation files",
}
STANDARD_TOP_LEVEL_FILES = {
    "README", "README.md",
    "LICENSE", "LICENSE.md",
    "CODE_OF_CONDUCT", "CODE_OF_CONDUCT.md",
    "CONTRIBUTING", "CONTRIBUTING.md",
}
STANDARD_DIAGRAM = "images/rulegraph.svg"


def find_workflow(root_dir):
    candidates = [
        root_dir / "workflow" / WF_BASENAME,
        root_dir / WF_BASENAME,
    ]
    for p in candidates:
        if p.is_file():
            return p
    raise RuntimeError(
        f"workflow definition (one of: {', '.join(candidates)}) not found"
    )


def parse_workflow(workflow_path):
    wf = Workflow(snakefile=workflow_path, overwrite_configfiles=[])
    try:
        wf.include(workflow_path)
    except Exception:
        pass
    wf.execute(dryrun=True, updated_files=[])
    return wf


def make_crate(root, repo_url=None, version=None, lang_version=None,
               license=None, ci_workflow=None, diagram=None):
    if ci_workflow is None:
        ci_workflow = CI_WORKFLOW
    if diagram is None:
        diagram = STANDARD_DIAGRAM
    crate = ROCrate(gen_preview=False)
    wf_source = find_workflow(root)
    workflow = crate.add_workflow(
        wf_source, wf_source.relative_to(root), main=True,
        lang="snakemake", lang_version=lang_version, gen_cwl=False
    )
    # wf_obj = parse_workflow(wf_source)
    workflow["name"] = crate.root_dataset["name"] = root.name
    if version:
        workflow["version"] = version
    # Is there a Python equivalent of https://github.com/licensee/licensee?
    if license:
        crate.root_dataset["license"] = license
    for name in STANDARD_TOP_LEVEL_FILES:
        source = root / name
        if source.is_file():
            crate.add_file(source, name)
    if repo_url:
        workflow["url"] = crate.root_dataset["isBasedOn"] = repo_url
        ci_wf_source = root / ".github" / "workflows" / ci_workflow
        if ci_wf_source.is_file():
            suite = crate.add_test_suite(name=f"{root.name} test suite")
            resource = get_ci_wf_endpoint(repo_url, ci_workflow)
            crate.add_test_instance(
                suite, GH_API_URL, resource=resource, service="github",
                name=f"GitHub testing workflow for {root.name}"
            )
    for relpath, desc in STANDARD_DIRS.items():
        source = root / relpath
        if not source.is_dir():
            continue
        crate.add_dataset(source, relpath, properties={
            "description": desc,
        })
    diag_source = root / diagram
    if diag_source.is_file():
        diag = crate.add_file(diag_source, diagram, properties={
            "name": "Workflow diagram",
            "@type": ["File", "ImageObject"],
        })
        workflow["image"] = diag
    return crate
