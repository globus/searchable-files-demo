# Searchable Files (demo)

This demo application shows how Globus Search can be used to build an index of
file metadata. Similar to the unix `find` command, it lets you search for files
in a directory.
Unlike `find`, however, the user searching the files does not need shell access
to the server where files are stored.

## Companion Doc

Globus provides a
[companion doc](https://docs.globus.org/api/search/guides/searchable_files/)
which expands upon the content in this demo.

The doc covers some of the motivation and background for this app, as well as
some ideas about ways in which the demo can be adapted or extended.

## Architecture

The demo app is broken up into four main components:

- the **Extractor** (`src/searchable_files/extractor.py`)

Parses file metadata and contents into chunks, and formats that data into JSON
files.

By default, this parses content in `data/files` and outputs to
`output/extracted/`.

- the **Assembler** (`src/searchable_files/assembler.py`)

Combines the output of the Extractor with visibility information
to produce ingest documents for Globus Search. An ingest document is data
formatted for submission to Globus Search, containing searchable data and
visibility information for who is allowed to search on and view different parts
of the data.

The visibility information and additional annotations used to augment the data from
the Extractor is loaded from configuration, located by default in
`data/config/assembler.yaml`.

By default, the Assembler reads data from `output/extracted/` and outputs to
`output/assembled/`.

- the **Submitter** (`src/searchable_files/submit.py`)

The Submitter sends ingest documents to the Search service.

By default, the Submitter reads data from `output/assembled/` and writes
information to `output/task_submit/`.

- the **Watcher** (`src/searchable_files/watcher.py`)

The Watcher monitors tasks in Globus Search and waits for completion or failure.

By default, the Watcher reads task IDs from `output/task_submit/` and outputs to
standard output the number of passing and failing
tasks (or only success if no tasks fail).

## Prerequisites

The following software is required in order to install and run the
Searchable Files app:

- python3.6+
- virtualenv
- pip
- make

## Download

To grab the latest version of the app, clone this repo or download it from
GitHub.

- [download searchable-files-demo-main.zip](https://github.com/globus/searchable-files-demo/archive/refs/heads/main.zip)
- [download searchable-files-demo-main.tar.gz](https://github.com/globus/searchable-files-demo/archive/refs/heads/main.tar.gz)

## Installation

Run

    make install

This will create a virtualenv and install the necessary dependencies.

It will also create a script named `searchable-files`.

> **WARNING**: Always run `searchable-files` from the top level of the
> repository, unless you pass additional options. The script's defaults are all
> written as relative paths with respect to this directory.

### Setup

Before running any of the steps, you must run

    ./searchable-files login

This will log you in to Globus and write your credentials to
`~/.globus_searchable_files.db`.

After login, run

    ./searchable-files create-index

This will create a new index for you to use with the Searchable Files demo app.
Its index ID will be stored in `~/.globus_searchable_files.db`.

To retrieve the index ID and other index information, run

    ./searchable-files show-index

### Running the Workflow

Each component of the Searchable Files app is run with a separate
subcommand. Each supports a `--help` option for full details on its
usage.

    ./searchable-files extract --help
    ./searchable-files assemble --help
    ./searchable-files submit --help
    ./searchable-files watch --help

The order of these commands matters, as each command's output is the input to
the next command.

The entire workflow can run in one line by simply running each command
back-to-back, thusly:

    ./searchable-files extract && ./searchable-files assemble && ./searchable-files submit && ./searchable-files watch

### Querying Results

The Searchable Files demo app includes a query command which you can use to
search your files. Search results will be output in the JSON format produced by
the Globus Search service.

See

    ./searchable-files query --help

for more details.

You can filter your search results. For example

    ./searchable-files query "foo" --types-or=text,png

will submit a query which matches `"foo"` and requires that the files matched
have either the `txt` or `png` type.


    ./searchable-files query "foo" --types=text,non-executable

will filter results to text files that are not executable.

#### Making Unauthenticated Queries

By default, queries are submitted as the logged-in user.
The query command supports a `--no-auth` flag, which will submit the
query without any credentials.

Unauthenticated queries return only results for which which the `visible_to`
field is set to `public`.

Using the example data, you should see a different result set between

    ./searchable-files query '*' --extensions=sh

and

    ./searchable-files query '*' --extensions=sh --no-auth

#### Dumping the Query

If you want to inspect the query which the `searchable-files` command
is generating instead of submitting the query, you can use
`--dump-query` to write the query to standard out, as in

    ./searchable-files query "foo" --types=tar --dump-query

### Logout

When you are done with the demo, you can log out with

    ./searchable-files logout

Please note that this will not delete your index. The index will still be available
and searchable.

## Next Steps

For a fully featured Globus Search client, you may want to install and explore the
[`globus-search-cli`](https://globus-search-cli.readthedocs.io/en/latest/overview.html).

You can also write your own python clients against the Search service by
using the
[`SearchClient` class from the Globus SDK](https://globus-sdk-python.readthedocs.io/en/stable/clients/search.html).

The full [Globus Search documentation](https://docs.globus.org/api/search/) offers a
great deal more detail about the service and reference documentation for all of
its supported methods and features.

### Customizing and Extending Searchable Files

This demo application is intentionally segmented into parts which you can
customize or replace to meet your needs.

#### Setup

The `login` and `create-index` commands create and store data in a sqlite
database at `~/.globus_searchable_files.db`.
If you wish to use an alternative index ID, be aware that several commands
rely on data stored in this database.

#### Extractor

The Extractor examines a source for raw metadata and pulls out features which
it recognizes. In the simplest case, just pass the `--directory` option to read
a different source directory with the existing extractor. This can be run on
any directory without any special considerations.

#### Assembler

The Assembler takes the raw data from the Extractor and annotates it with
additional information from a secondary source. In the provided Assembler,
annotations are stored in some simple YAML files, but annotations could just as
easily come from a database, external API calls, or any other source.

A replacement Assembler still needs to incorporate that information with the
Extractor's data to produce valid documents for Globus Search. Note that the
Assembler included in the Searchable Files demo has special handling for the
string `"{current_user}"` in order to resolve this to the logged-in user's
primary identity ID. A custom Assembler could replicate this functionality
(requiring login) or omit support for this usage.

#### Submitter and Watcher

The Submitter and Watcher can be applied to any directory full of Globus Search
ingest documents (the format of data produced by the Assembler). Although you
may want to modify them to alter their outputs, combine them into a single
command, or make other minor changes, their main logic should probably be
left unmodified.

The only special consideration when modifying these components is that these
commands use the Index ID retrieved from `create-index`. If modifying or
replacing these commands, it may be necessary to replace the logic that
loads the `index_id` from storage.
