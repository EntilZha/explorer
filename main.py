import os
import subprocess

import typer

from pedroai.io import eprint

from qanta.database import build_db

DATA_PATH = "data/"
FILES = [
    (
        "https://s3.amazonaws.com/my89public/quac/train_v0.2.json",
        "data/quac/train_v0.2.json",
    ),
    (
        "https://s3.amazonaws.com/my89public/quac/val_v0.2.json",
        "data/quac/val_v0.2.json",
    ),
    (
        "https://pinafore-us-west-2.s3-us-west-2.amazonaws.com/karl/protobowl-042818.log.h5",
        "data/protobowl-042818.log.h5",
    ),
    (
        "https://s3-us-west-2.amazonaws.com/pinafore-us-west-2/qanta-jmlr-datasets/qanta.mapped.2018.04.18.json",
        "data/qanta.mapped.2018.04.18.json",
    ),
]


def download(remote_file: str, local_file: str):
    eprint(f"Downloading {remote_file} to {local_file}")
    subprocess.run(
        f"curl -f --create-dirs -o {local_file} {remote_file}", shell=True, check=True
    )


app = typer.Typer()


@app.command()
def populate():
    build_db()


@app.command()
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


if __name__ == "__main__":
    app()
