# Searchable Files (demo)

This demo application shows how Globus Search can be used to build an index of
files. Similar to the `find` command, it lets you search for files
in a directory based on simple criteria. Unlike `find`, however, the user
searching the files does not need shell access to the server where files are
stored.

Searchable Files is broken up into four main components:

- the **Extractor** (`src/searchable_files/extractor.py`)

Parses file metadata and contents into chunks, labeled either as public or private.
By default, this parses content in `data/files` and outputs to
`output/extracted/`.

- the **Assembler** (`sr/searchable_filesc/assembler.py`)

Given the parsed data, combine it with extra information about visibility
to produce ingest documents for Globus Search. An ingest document is data
formatted for submission to Globus Search, containing searchable data and
visibility information for who is allowed to search on and view different parts
of the data.

By default, this reads data from `output/extracted/`, takes visibility
information from `data/visibility.yaml`, and adds additional annotations from
`settings/assembler.yaml`. It outputs to `output/assembled/`.

- the **Submitter** (`src/searchable_files/submit.py`)

Given a set of ingest documents, valid for Globus Search, this sends the data
to the Search service.

By default, this reads data from `output/assembled/` and writes information to
`output/task_submit/`.

- the **Watcher** (`src/searchable_files/watcher.py`)

Given a set of tasks in Globus Search, this monitors those tasks and waits for
completion or failure.

By default, this reads task IDs from `output/task_submit/` and writes detailed
information to `output/task_watch/`, including a summary in
`output/task_watch/summary`.

When run interactively, the Watcher also prints a progress bar in the terminal.

## Prerequisites

The following software is required in order to install and run the
Searchable Files app:

- python3.6+
- virtualenv
- pip
- make

## Installation

Run

    make install

This will create a virtualenv and install the necessary dependencies.

It will also create a script named `searchable-files`.

## Usage

After installation, you can use the `searchable-files` script.

### Setup

Before running any of the steps, you must run

    ./searchable-files login

This will log you in to Globus and write your credentials to
`~/.globus-searchable-files-demo/creds.json`.

After login, run

    ./searchable-files create-index

This will create a new index for you to use Searchable Files.
Its index ID will be written to `~/.globus-searchable-files-demo/index_id`.

Running `./searchable-files create-index` a second time will print a message
stating that the index already exists and giving you the index ID.

You can also run

    ./searchable-files show-index

to get info about your index.

### Running Parts

Each component of the Searchable Files App can be run with a separate
subcommand, and each one supports a `--help` option for full details on their
usage.

    ./searchable-files extract --help
    ./searchable-files assemble --help
    ./searchable-files submit --help
    ./searchable-files watch --help

The order of these commands matters, as each command's output is the input to
the next command.

### Running the full flow at once

If you wish to run the equivalent of

    ./searchable-files extract
    ./searchable-files assemble
    ./searchable-files submit
    ./searchable-files watch

You can instead run

    ./searchable-files all-parts

These are equivalent. Note that `all-parts` does not take any options, and
therefore cannot be customized in all the ways that these other commands can be.

### Querying Results

The `searchable-files` tool includes a query command which you can use to
search your files.

See

    ./searchable-files query --help

for more details.

You can filter in various ways using this. For example

    ./searchable-files query "foo" --types=txt,png

will submit a query which matches `"foo"` and requires that the files matched
have either the `txt` or `png` type.

You can test the difference between a query as your current user and an
unauthenticated query by adding `--no-auth`, as in

    ./searchable-files query --no-auth "bar"

You will see that unauthenticated queries can only see data marked as
"public".

Finally, if you want to inspect the query which the `searchable-files` command
is generating, you can use `--dump-query` to write the query to a file, as in

    ./searchable-files query "foo" --types=tar --dump-query test-query-1.json

### Logout

When you are done with the demo, you can log out with

    ./searchable-files logout

Please note that this will not delete your index and it will still be available
and searchable.

## Next Steps

For a fully featured Search client, you may want to install and explore the
[`globus-search-cli`](https://globus-search-cli.readthedocs.io/en/latest/overview.html).

You can also write your own python clients against the Globus Search service by
using the
[`SearchClient` class from the Globus SDK](https://globus-sdk-python.readthedocs.io/en/stable/clients/search.html).

The full [Globus Search documentation](https://docs.globus.org/api/search/) offers a
great deal more detail about the service and reference documentation for all of
its supported methods and features.

### Customizing and Extending Searchable Files

This demo application is intentionally segmented into parts which you can
customize or replace to meet your needs.

The Extractor examines a source for raw metadata and pulls out features which
it recognizes. In the simplest case, just pass the `--directory` option to read
a different source directory with the existing extractor.

The Assembler takes the raw data from the Extractor and annotates it with
additional information from a secondary source. In the sample extractor,
annotations are stored in some simple YAML files, but annotations could just as
easily come from a database, external API calls, or any other source. A
replacement Assembler still needs to incorporate that information with the
Extractor's data to produce valid documents for Globus Search.

The Submitter and Watcher can be applied to any directory full of Globus Search
ingest documents (the format of data produced by the Assembler). Although you
may want to modify them to alter their outputs, combine them into a single
command, or make other minor changes, their main logic should probably be
left unmodified.
