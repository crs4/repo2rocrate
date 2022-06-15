#!/usr/bin/env python

import subprocess
import sys
import tempfile

from pathlib import Path
from typing import Any, Mapping

import boto3
import yaml


def read_config(path: str) -> Mapping[str, Any]:
    with open(path) as f:
        return yaml.safe_load(f)


def download_file(remote_name: str, local_dir: Path, dest_config: Mapping[str, Any]) -> Path:
    if dest_config['type'].lower() != 's3':
        raise NotImplementedError("Only S3 destinations are supported. "
                                  f"Configuration specifies {dest_config['type']}")
    if dest_config['root_path'].startswith('/'):
        raise ValueError("root_path must not start with '/' "
                         f"(got value {dest_config['root_path']}")

    remote_path = Path(dest_config['root_path']) / remote_name
    bucket_name = remote_path.parts[0]
    object_path = Path(*remote_path.parts[1:])
    local_path = local_dir / object_path.name

    session = boto3.Session(
        aws_access_key_id=dest_config['connection']['access_key_id'],
        aws_secret_access_key=dest_config['connection']['secret_access_key']
    )
    boto_args = {}
    if 'host' in dest_config['connection']:
        boto_args['endpoint_url'] = dest_config['connection']['host']
    if 'verify' in dest_config['connection']:
        boto_args['verify'] = dest_config['connection']['verify']
    s3 = session.resource('s3', **boto_args)
    print(f"downloading bucket={bucket_name} object={object_path}  to local path", str(local_path), file=sys.stderr)
    s3.Bucket(bucket_name).download_file(str(object_path), str(local_path))
    return local_path


def fetch_and_decrypt_file(remote_name: str, private_key: Path, config: Mapping[str, Any], tmpdir: Path) -> str:
    path = download_file(remote_name, tmpdir, config['destination'])
    with open(path) as index_fp, tempfile.TemporaryFile() as output_fp:
        subprocess.check_call(
            ['crypt4gh', 'decrypt', '--sk', str(private_key)],
            stdin=index_fp, stdout=output_fp)

        output_fp.seek(0)
        return output_fp.read()


def fetch_index(private_key: Path, config: Mapping[str, Any], tmpdir: Path) -> Path:
    contents = fetch_and_decrypt_file('index.tsv.c4gh', private_key, config, tmpdir)
    index = [line.split('\t') for line in contents.decode().splitlines()]
    return index


def main():
    private_key = Path('test.sec')
    with tempfile.TemporaryDirectory(prefix='test_') as d:
        tmpdir = Path(d)
        cfg = read_config('./config.yml')
        test_file = Path(cfg['repository']['path']) / 'test-file.txt'

        # Fetch and decrypt index.  Verify that its contents seem reasonable
        index = fetch_index(private_key, cfg, tmpdir)
        print("Fetched and decrypted index.", file=sys.stderr)
        assert len(index) == 1, f"{len(index)} != 1"
        index_entry = index[0]
        assert len(index_entry) == 3, f"{len(index_entry)} != 3"
        assert index_entry[0].endswith('.c4gh'), f"{index_entry[0]} does not end with .c4gh"
        assert index_entry[1].endswith(test_file.name + '.c4gh'), f"{index_entry[1]} does not end with test file name"

        data = fetch_and_decrypt_file(index_entry[0], private_key, cfg, tmpdir).decode()
        print("Fetched and decrypted data file", index_entry[0], file=sys.stderr)
        with open(test_file) as tf:
            original_data = tf.read()
        assert data == original_data, f"{data} != {original_data}"

    print("Test OK")


if __name__ == '__main__':
    main()
