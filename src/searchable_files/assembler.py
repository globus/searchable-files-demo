import json
import os

import click
import ruamel.yaml

from ._common import all_filenames, common_options

yaml = ruamel.yaml.YAML(typ="safe")


def _render_visibility(value):
    if value == "public":
        return value
    if value == "{current_user}":
        # raise ValueError("TODO")
        return "foo-bar"
    return value


def build_entries(datafile, settings):
    # read data
    with open(datafile) as fp:
        data = json.load(fp)
    # if there are annotations to add, do so
    if data["relpath"] in settings.file_specific_annotations:
        data.update(settings.file_specific_annotations[data["relpath"]])

    non_default_entries, non_default_fields = [], []
    for part in settings.doc_parts:
        non_default_entries.append(
            (part["visibility"], {f: data[f] for f in part["fields"]}, part["id"])
        )
        non_default_fields.extend(part["fields"])
    default_entry_data = {k: v for k, v in data.items() if k not in non_default_fields}

    default_visibility = settings.default_visibility
    if data["relpath"] in settings.file_restrictions:
        default_visibility = settings.file_restrictions[data["relpath"]]

    return [
        {
            "visible_to": _render_visibility(default_visibility),
            "content": default_entry_data,
        }
    ] + [
        {"visible_to": _render_visibility(vis), "content": fields, "entry_id": eid}
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


@click.command("assemble")
@click.option(
    "--directory",
    default="output/extracted",
    show_default=True,
    help="A path, relative to the current working directory, "
    "containing extracted metadata for processing",
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
    callback=_load_settings_callback,
    help="YAML file with configuration for the assembler",
)
@common_options
def assemble_cli(settings, directory, output):
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


if __name__ == "__main__":
    assemble_cli()
