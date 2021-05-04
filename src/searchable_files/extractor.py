import datetime
import fnmatch
import hashlib
import json
import os

import click
import ruamel.yaml
from identify import identify

from ._common import all_filenames, common_options

yaml = ruamel.yaml.YAML(typ="safe")


def file_tags(filename):
    return list(identify.tags_from_path(filename))


def stat_dict(filename):
    info = os.stat(filename)
    return {
        "mode": oct(info.st_mode),
        "size_bytes": info.st_size,
        "mtime": datetime.datetime.fromtimestamp(info.st_mtime).isoformat(),
    }


def extension(filename):
    if "." in filename:
        return filename.split(".")[-1]
    return None


def read_head(filename, settings):
    match = False
    for pattern in settings.read_head["files"]:
        if fnmatch.fnmatch(filename, pattern):
            match = True

    if not match:
        return None

    # note, this is not necessarily 100 bytes
    # if the file is encoded in utf-8, for example, 100 characters could be 400
    # bytes
    with open(filename) as fp:
        return fp.read(100)


def filename2dict(filename, settings):
    return {
        "tags": file_tags(filename),
        "extension": extension(filename),
        "head": read_head(filename, settings),
        "name": os.path.basename(filename),
        "relpath": filename,
        **stat_dict(filename),
    }


def target_file(output_directory, filename):
    hashed_name = hashlib.sha256(filename.encode("utf-8")).hexdigest()
    os.makedirs(output_directory, exist_ok=True)
    return os.path.join(output_directory, hashed_name) + ".json"


class Settings:
    def __init__(self, settingsdict):
        self.read_head = settingsdict.get("read_head", {})
        if "files" not in self.read_head:
            self.read_head["files"] = []


def _load_settings_callback(ctx, param, value):
    if value is not None:
        with open(value) as fp:
            return Settings(yaml.load(fp))


@click.command("extract")
@click.option(
    "--directory",
    default="data/files",
    show_default=True,
    help="A path, relative to the current working directory, "
    "containing data files from which to extract metadata",
)
@click.option(
    "--output",
    default="output/extracted",
    show_default=True,
    help="A path, relative to the current working directory, "
    "where the extracted metadata should be written",
)
@click.option(
    "--settings",
    default="data/config/extractor.yaml",
    show_default=True,
    callback=_load_settings_callback,
    help="YAML file with configuration for the extractor",
)
@common_options
def extract_cli(settings, directory, output):
    old_cwd = os.getcwd()
    os.chdir(directory)

    rendered_data = {}
    for filename in all_filenames("."):
        rendered_data[filename] = filename2dict(filename, settings)

    os.chdir(old_cwd)
    for filename, data in rendered_data.items():
        with open(target_file(output, filename), "w") as fp:
            json.dump(data, fp)

    click.echo("metadata extraction complete")
    click.echo(f"results visible in\n  {output}")
