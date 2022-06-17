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
Generate a Workflow Testing RO-Crate from a "best practices" Nextflow
workflow repository.

https://nf-co.re/contributing/guidelines
https://nf-co.re/developers/adding_pipelines#nf-core-pipeline-structure
"""

from rocrate.rocrate import ROCrate
from . import CI_WORKFLOW, GH_API_URL
from .utils import get_ci_wf_endpoint


WF_BASENAME = "main.nf"
# "standard" resources will be listed in the metadata if present
STANDARD_DIRS = {
    "assets": "Additional files",
    "bin": "Scripts that must be callable from a pipeline process",
    "conf": "Configuration files",
    "docs": "Markdown files for documenting the pipeline",
    "docs/images": "Images for the documentation files",
    "lib": "Groovy utility functions",
    "modules": "Modules used by the pipeline",
    "modules/local": "Pipeline-specific modules",
    "modules/nf-core": "nf-core modules",
    "workflows": "Main pipeline workflows to be executed in main.nf",
    "subworkflows": "Smaller subworkflows",
}
STANDARD_TOP_LEVEL_FILES = {
    "nextflow.config": "Main Nextflow configuration file",
    "README.md": "Basic pipeline usage information",
    "nextflow_schema.json": "JSON schema for pipeline parameter specification",
    "CHANGELOG.md": "Information on changes made to the pipeline",
    "LICENSE": "The license - should be MIT",
    "CODE_OF_CONDUCT.md": "The nf-core code of conduct",
    "CITATIONS.md": "Citations needed when using the pipeline",
    "modules.json": "Version information for modules from nf-core/modules",
}


def find_workflow(root_dir):
    wf_path = root_dir / WF_BASENAME
    if not wf_path.is_file():
        raise RuntimeError(f"{wf_path} not found")
    return wf_path


def make_crate(root, repo_url=None, version=None, lang_version=None,
               license=None, ci_workflow=None, diagram=None):
    if ci_workflow is None:
        ci_workflow = CI_WORKFLOW
    crate = ROCrate(gen_preview=False)
    wf_source = find_workflow(root)
    workflow = crate.add_workflow(
        wf_source, wf_source.relative_to(root), main=True,
        lang="nextflow", lang_version=lang_version, gen_cwl=False
    )
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
    if diagram:
        diag_source = root / diagram
        if diag_source.is_file():
            diag = crate.add_file(diag_source, diagram, properties={
                "name": "Workflow diagram",
                "@type": ["File", "ImageObject"],
            })
            workflow["image"] = diag
    return crate
