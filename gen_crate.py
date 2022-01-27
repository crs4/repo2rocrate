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
Generate a Workflow RO-Crate for a "best practices" Snakemake workflow.

https://snakemake.readthedocs.io/en/stable/snakefiles/deployment.html#distribution-and-reproducibility
https://snakemake.readthedocs.io/en/stable/snakefiles/deployment.html#uploading-workflows-to-workflowhub
https://snakemake.github.io/snakemake-workflow-catalog/?rules=true
"""

import argparse
import os
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlparse

from rocrate.rocrate import ROCrate
from snakemake.workflow import Workflow


GH_API_URL = "https://api.github.com"
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


def get_ci_resource(repo_url, ci_wf_name):
    repo_path = PurePosixPath(urlparse(unquote(repo_url)).path)
    if len(repo_path.parts) != 3:  # first one is '/'
        raise RuntimeError(
            "repository url must be like https://github.com/<OWNER>/<REPO>"
        )
    owner, repo_name = repo_path.parts[-2:]
    return f"repos/{owner}/{repo_name}/actions/workflows/{ci_wf_name}"


def make_crate(args):
    crate = ROCrate(gen_preview=False)
    wf_source = find_workflow(args.root)
    workflow = crate.add_workflow(
        wf_source, wf_source.relative_to(args.root), main=True,
        lang="snakemake", lang_version=args.lang_version, gen_cwl=False
    )
    # wf_obj = parse_workflow(wf_source)
    workflow["name"] = crate.root_dataset["name"] = args.root.name
    if args.version:
        workflow["version"] = args.version
    # Is there a Python equivalent of https://github.com/licensee/licensee?
    if args.license:
        crate.root_dataset["license"] = args.license
    for name in STANDARD_TOP_LEVEL_FILES:
        source = args.root / name
        if source.is_file():
            crate.add_file(source, name)
    if args.repo_url:
        workflow["url"] = crate.root_dataset["isBasedOn"] = args.repo_url
        ci_wf_source = args.root / ".github" / "workflows" / args.ci_workflow
        if ci_wf_source.is_file():
            suite = crate.add_test_suite(name=f"{args.root.name} test suite")
            resource = get_ci_resource(args.repo_url, args.ci_workflow)
            crate.add_test_instance(
                suite, GH_API_URL, resource=resource, service="github",
                name=f"GitHub testing workflow for {args.root.name}"
            )
    for relpath, desc in STANDARD_DIRS.items():
        source = args.root / relpath
        if not source.is_dir():
            continue
        crate.add_dataset(source, relpath, properties={
            "description": desc,
        })
        if relpath.startswith(".tests"):
            # non-flat arbitrary structure, treat them as opaque
            # note: contents will still be added to the crate
            continue
        for entry in os.scandir(source):
            if entry.is_file():
                f_source = Path(entry.path)
                if not f_source.samefile(wf_source):
                    crate.add_file(f_source, f_source.relative_to(args.root))
    diag_source = args.root / STANDARD_DIAGRAM
    if diag_source.is_file():
        diag = crate.add_file(diag_source, STANDARD_DIAGRAM, properties={
            "name": "Workflow diagram",
            "@type": ["File", "ImageObject"],
        })
        workflow["image"] = diag
    if args.output.endswith(".zip"):
        crate.write_zip(args.output)
    else:
        crate.write(args.output)


def main(args):
    args.root = Path(args.root)
    if not args.output:
        args.output = f"{args.root.name}.crate.zip"
    print(f"generating {args.output}")
    make_crate(args)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("root", metavar="ROOT_DIR",
                        help="top-level directory (workflow repository)")
    parser.add_argument("-o", "--output", metavar="DIR OR ZIP",
                        help="output RO-Crate directory or zip file")
    parser.add_argument("--repo-url", metavar="STRING",
                        help="workflow repository URL")
    parser.add_argument("--version", metavar="STRING", help="workflow version")
    parser.add_argument("--lang-version", metavar="STRING",
                        help="Snakemake version required by the workflow")
    parser.add_argument("--license", metavar="STRING", help="license URL")
    parser.add_argument(
        "--ci-workflow", metavar="STRING", default="main.yml",
        help=("filename (basename) of the GitHub Actions workflow "
              "that runs the tests for the Snakemake workflow")
    )
    main(parser.parse_args())
