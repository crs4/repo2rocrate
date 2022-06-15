
rule upload_file:
    input:
        "reencrypted/{filename}",
    output:
        remote = get_remote("{filename}"),
    log:
        "logs/upload-{filename}.log",
    shell:
        # Snakemake makes us locally copy the file from its
        # "current" input path to a staging directory (the
        # "output" path).  Rather than waste time actually
        # making a copy of the file we create a hard link.
        """
        cp --link {input:q} {output:q}
        """
