

def gen_final_index(base_index_path: str, final_index_path: str) -> None:
    with open(base_index_path) as base_index, open(final_index_path, 'w') as final_index:
        for line in base_index:
            rnd_name, original_name = line.rstrip('\n').split('\t')
            chksum_path = f"reencrypted/{rnd_name}.sha"
            with open(chksum_path) as chk_file:
                chksum_value = chk_file.read().split(' ', 1)[0]
            new_index_line = f"{rnd_name}\t{original_name}\t{chksum_value}\n"
            final_index.write(new_index_line)


gen_final_index(snakemake.input.base_index, snakemake.output.index)
