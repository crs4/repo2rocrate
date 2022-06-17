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

from pathlib import Path

import click
from . import CI_WORKFLOW
from .nextflow import make_crate as nextflow_make_crate
from .snakemake import make_crate as snakemake_make_crate

GEN_MAP = {
    "nextflow": nextflow_make_crate,
    "snakemake": snakemake_make_crate,
}
DEFAULT_LANG = "snakemake"


@click.command()
@click.option("-r", "--root", type=click.Path(exists=True, file_okay=False, readable=True, path_type=Path), help="workflow repository root", default=Path.cwd)
@click.option('-l', '--lang', type=click.Choice(list(GEN_MAP)), default=DEFAULT_LANG, help="workflow language")
@click.option("-o", "--output", type=click.Path(path_type=Path), help="output directory or zip file")
@click.option("--repo-url", help="workflow repository URL")
@click.option("--version", help="workflow version")
@click.option("--lang-version", help="workflow language version")
@click.option("--license", help="license URL")
@click.option("--ci-workflow", help="filename (basename) of the GitHub Actions workflow that runs the tests for the workflow", default=CI_WORKFLOW)
@click.option("--diagram", help="relative path of the workflow diagram")
def cli(root, lang, output, repo_url, version, lang_version, license, ci_workflow, diagram):
    if not output:
        output = Path(f"{root.name}.crate.zip")
    print(f"generating {output}")
    make_crate = GEN_MAP[lang]
    crate = make_crate(root, repo_url=repo_url, version=version, lang_version=lang_version, license=license, ci_workflow=ci_workflow, diagram=diagram)
    if output.suffix == ".zip":
        crate.write_zip(output)
    else:
        crate.write(output)


if __name__ == "__main__":
    cli()
