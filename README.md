# repo2rocrate

Generate a [Workflow Testing RO-Crate](https://crs4.github.io/life_monitor/workflow_testing_ro_crate) from a "best-practices" workflow repository.

Example:

```
pip install -r requirements.txt
python setup.py install
git clone https://github.com/crs4/fair-crcc-send-data
repo2rocrate -r fair-crcc-send-data -l snakemake --repo-url https://github.com/crs4/fair-crcc-send-data --license GPL-3.0
```
