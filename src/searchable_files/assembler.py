import json
import os
import shutil

import click
import ruamel.yaml

from ._common import all_filenames, auth_client, common_options

yaml = ruamel.yaml.YAML(typ="safe")


def _current_user_as_urn():
    if not hasattr(_current_user_as_urn, "identity_id"):
        _current_user_as_urn.identity_id = auth_client().oauth2_userinfo()["sub"]
    return f"urn:globus:auth:identity:{_current_user_as_urn.identity_id}"


def _render_visibility(value, listify=True):
    if isinstance(value, list):
        return [_render_visibility(v, listify=False) for v in value]

    ret = value
    if value == "{current_user}":
        ret = _current_user_as_urn()

    if isinstance(ret, list):
        return ret
    return [ret]


def build_entries(datafile, settings):
    # read data
    with open(datafile) as fp:
        data = json.load(fp)

    full_filename = data["relpath"]

    # if there are annotations to add, do so
    if full_filename in settings.file_specific_annotations:
        data.update(settings.file_specific_annotations[full_filename])

    non_default_entries, non_default_fields = [], []
    for part in settings.doc_parts:
        non_default_entries.append(
            (part["visibility"], {f: data[f] for f in part["fields"]}, part["id"])
        )
        non_default_fields.extend(part["fields"])
    default_entry_data = {k: v for k, v in data.items() if k not in non_default_fields}

    default_visibility = settings.default_visibility
    if full_filename in settings.file_restrictions:
        default_visibility = settings.file_restrictions[full_filename]

    return [
        {
            "subject": full_filename,
            "visible_to": _render_visibility(default_visibility),
            "content": default_entry_data,
        }
    ] + [
        {
            "subject": full_filename,
            "visible_to": _render_visibility(vis),
            "content": fields,
            "id": eid,
        }
        for vis, fields, eid in non_default_entries
    ]


def flush_batch(entry_batch, docid, output_directory):
    os.makedirs(output_directory, exist_ok=True)
    fname = os.path.join(output_directory, f"ingest_doc_{docid}.json")
    with open(fname, "w") as fp:
        json.dump(
            {"ingest_type": "GMetaList", "ingest_data": {"gmeta": entry_batch}}, fp
        )


class Settings:
    def __init__(self, data):
        self.max_batch_size = data.get("max_batch_size", 100)
        self.file_specific_annotations = data.get("file_specific_annotations", {})

        self.visibility = data.get("visibility")
        self.default_visibility = self.visibility.get("default_visibility", "public")
        self.file_restrictions = self.visibility.get("file_restrictions", {})
        self.doc_parts = self.visibility.get("doc_parts", [])


def _load_settings_callback(ctx, param, value):
    if value is not None:
        with open(value) as fp:
            return Settings(yaml.load(fp))


@click.command(
    "assemble",
    short_help="Annotate data and prepare it for ingest",
    help="Given data from the Extractor, notate it and convert it into "
    "Ingest format. This will pull in data from the assembler configuration "
    "and use it to populate `visible_to` (see docs.globus.org/api/search for "
    "details on `visible_to`) and add fields to documents.",
)
@click.option(
    "--directory",
    default="output/extracted",
    show_default=True,
    help="A path, relative to the current working directory, "
    "containing extracted metadata for processing",
)
@click.option(
    "--clean",
    default=False,
    is_flag=True,
    help="Empty the output directory before writing any data there",
)
@click.option(
    "--output",
    default="output/assembled",
    show_default=True,
    help="A path, relative to the current working directory, "
    "where the assembled metadata should be written",
)
@click.option(
    "--settings",
    default="data/config/assembler.yaml",
    show_default=True,
    callback=_load_settings_callback,
    help="YAML file with configuration for the assembler",
)
@common_options
def assemble_cli(settings, directory, output, clean):
    if clean:
        shutil.rmtree(output, ignore_errors=True)

    entry_docs = []
    for filename in all_filenames(directory):
        entry_docs.extend(build_entries(filename, settings))

    current_doc_id = 0
    batch = []
    for entry in entry_docs:
        if len(batch) >= settings.max_batch_size:
            flush_batch(batch, current_doc_id, output)
            batch = []
            current_doc_id += 1
        batch.append(entry)
    flush_batch(batch, current_doc_id, output)

    click.echo("ingest document assembly complete")
    click.echo(f"results visible in\n  {output}")
