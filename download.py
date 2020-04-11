import os
import subprocess

import click

from pedroai.io import eprint

DATA_PATH = 'data/'
FILES = [
    ("https://s3.amazonaws.com/my89public/quac/train_v0.2.json", "data/quac/train_v0.2.json"),
    ("https://s3.amazonaws.com/my89public/quac/val_v0.2.json", "data/quac/val_v0.2.json"),
]


def download(remote_file: str, local_file: str):
    eprint(f"Downloading {remote_file} to {local_file}")
    subprocess.run(
        f"curl -f --create-dirs -o {local_file} {remote_file}", shell=True, check=True
    )


def download_all(overwrite=False):
    os.makedirs(DATA_PATH, exist_ok=True)
    for remote_file, local_file in FILES:
        if os.path.exists(local_file):
            if overwrite:
                download(remote_file, local_file)
            else:
                eprint(f"File exists, skipping download of: {local_file}")
        else:
            download(remote_file, local_file)


@click.command()
@click.option("--overwrite-data", default=False, is_flag=True, type=bool)
def cli(overwrite_data: bool):
    download_all(overwrite=overwrite_data)


if __name__ == '__main__':
    cli()