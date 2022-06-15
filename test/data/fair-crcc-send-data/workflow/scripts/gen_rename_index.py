
from typing import List, TextIO
from uuid import uuid4


def write_index_file(f: TextIO, mapping: dict) -> None:
    for new_fname in sorted(mapping):
        original_name = mapping[new_fname]
        f.write(f"{new_fname}\t{original_name}\n")


def gen_rename_index(source_items: List[str], output_path: str):
    mapping = {str(uuid4()) + '.c4gh': original_name for original_name in source_items}
    with open(output_path, 'w') as f:
        write_index_file(f, mapping)


gen_rename_index(snakemake.params.source_items, snakemake.output.index)
