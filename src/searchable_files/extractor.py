import hashlib
import json
import os

import click
from identify import identify


def file_tags(filename):
    return list(identify.tags_from_path(filename))


def stat_dict(filename):
    info = os.stat(filename)
    return {"mode": oct(info.st_mode), "size": info.st_size, "mtime": info.st_mtime}


def extension(filename):
    if "." in filename:
        return filename.split(".")[:-1]
    return None


def read_head(filename):
    with open(filename) as fp:
        return fp.read(100)


def filename2dict(filename):
    return {
        "tags": file_tags(filename),
        "extension": extension(filename),
        "head": read_head(filename),
        "name": os.path.basename(filename),
        **stat_dict(filename),
    }


def all_filenames(directory):
    for dirpath, _dirnames, filenames in os.walk(directory):
        for f in filenames:
            yield os.path.join(dirpath, f)


def target_file(output_directory, filename):
    hashed_name = hashlib.sha256(filename.encode("utf-8")).hexdigest()
    return os.path.join(output_directory, hashed_name) + ".json"


@click.command("extract")
@click.option(
    "--directory",
    default="data/files",
    help="A path, relative to the current working directory, "
    "containing data files from which to extract metadata",
)
@click.option(
    "--output",
    default="output/extracted",
    help="A path, relative to the current working directory, "
    "where the extracted metadata should be written",
)
def main(directory, output):
    for filename in all_filenames(directory):
        with open(target_file(output, filename), "w") as fp:
            json.dump(fp, filename2dict(filename))
