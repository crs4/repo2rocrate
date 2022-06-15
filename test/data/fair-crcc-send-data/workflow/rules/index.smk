checkpoint gen_rename_index:
    """
    The workflow renames the files to be sent to uuid4 values.

    This rule generates the index for the dataset to be sent, mapping
    new random name to the original name.

    Since parts of the DAG depend on these mappings, we mark
    this rule as a "checkpoint", so that its output can be used
    to generate/re-evaluate the DAG.

    Index format:
      * one file per line;
      * each line has the following tab-separated fields
        new name <tab> original name\n
    """
    output:
        index = "base_index.tsv",
    log:
        "logs/base_index.tsv.log",
    params:
        source_items = lambda _: [path for path in source_files],
    script:
        "../scripts/gen_rename_index.py"


rule final_index:
    """
    Creates the final data index by adding a new column to the base_index.
    The new column contains the checksums of the new, reencrypted files.

    Line order remains as in base_index, so the file is sorted by the first
    column (new randomly generated file name).
    """
    input:
        base_index = rules.gen_rename_index.output.index,
        data_files = lambda _: expand("reencrypted/{filename}.sha", filename=get_all_new_item_names()),
    output:
        index = "index.tsv",
    log:
        "logs/index.tsv.log",
    script:
        "../scripts/gen_final_index.py"
