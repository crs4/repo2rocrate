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

from abc import ABCMeta, abstractmethod
from pathlib import Path

from rocrate.rocrate import ROCrate
from .utils import get_ci_wf_endpoint

GH_API_URL = "https://api.github.com"


class CrateBuilder(metaclass=ABCMeta):

    CI_WORKFLOW = "main.yml"
    DATA_ENTITIES = []
    DIAGRAM = None

    def __init__(self, root, repo_url=None):
        self.root = Path(root)
        self.repo_url = repo_url
        self.crate = ROCrate(gen_preview=False)

    @property
    @abstractmethod
    def lang(self):
        pass

    def build(self, wf_source, version=None, lang_version=None, license=None, ci_workflow=None, diagram=None):
        workflow = self.add_workflow(wf_source, version=version, lang_version=lang_version, license=license, diagram=diagram)
        self.add_test_suite(workflow, ci_workflow=ci_workflow)
        self.add_data_entities()
        return self.crate

    def add_workflow(self, wf_source, version=None, lang_version=None, license=None, diagram=None):
        if not diagram:
            diagram = self.DIAGRAM
        workflow = self.crate.add_workflow(
            wf_source, wf_source.relative_to(self.root), main=True,
            lang=self.lang, lang_version=lang_version, gen_cwl=False
        )
        workflow["name"] = self.crate.root_dataset["name"] = self.root.name
        if version:
            workflow["version"] = version
        # Is there a Python equivalent of https://github.com/licensee/licensee?
        if license:
            self.crate.root_dataset["license"] = license
        if self.repo_url:
            workflow["url"] = self.crate.root_dataset["isBasedOn"] = self.repo_url
        if diagram:
            diag_source = self.root / diagram
            if diag_source.is_file():
                diag = self.crate.add_file(diag_source, diagram, properties={
                    "name": "Workflow diagram",
                    "@type": ["File", "ImageObject"],
                })
                workflow["image"] = diag
        return workflow

    def add_test_suite(self, workflow, ci_workflow=None):
        if not self.repo_url:
            return None
        if not ci_workflow:
            ci_workflow = self.CI_WORKFLOW
        ci_wf_source = self.root / ".github" / "workflows" / ci_workflow
        if ci_wf_source.is_file():
            suite = self.crate.add_test_suite(name=f"{self.root.name} test suite")
            resource = get_ci_wf_endpoint(self.repo_url, ci_workflow)
            self.crate.add_test_instance(
                suite, GH_API_URL, resource=resource, service="github",
                name=f"GitHub testing workflow for {self.root.name}"
            )
        return suite

    def add_data_entities(self, data_entities=None):
        if not data_entities:
            data_entities = self.DATA_ENTITIES
        for relpath, type_, description in data_entities:
            if self.crate.get(str(relpath)):
                continue  # existing entity is more specific
            source = self.root / relpath
            if type_ == "File":
                if source.is_file():
                    entity = self.crate.add_file(source, relpath)
            elif type_ == "Dataset":
                if source.is_dir():
                    entity = self.crate.add_dataset(source, relpath)
            else:
                raise ValueError(f"Unexpected type: {type_!r}")
            if description:
                entity["description"] = str(description)
