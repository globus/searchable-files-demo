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

- the **Assembler** (`src/searchable_files/assembler.py`)

Given the parsed data, combine it with extra information about visibility
to produce ingest documents for Globus Search. An ingest document is data
formatted for submission to Globus Search, containing searchable data and
visibility information for who is allowed to search on and view different parts
of the data.

The visibility data and additional annotations used to augment the data from
the Extractor is loaded from configuration data. By default, this is
`data/config/assembler.yaml`.

By default, this reads data from `output/extracted/`, and outputs to
`output/assembled/`.

- the **Submitter** (`src/searchable_files/submit.py`)

Given a set of ingest documents, valid for Globus Search, this sends the data
to the Search service.

By default, this reads data from `output/assembled/` and writes information to
`output/task_submit/`.

- the **Watcher** (`src/searchable_files/watcher.py`)

Given a set of tasks in Globus Search, this monitors those tasks and waits for
completion or failure.

By default, this reads task IDs from `output/task_submit/` and monitors those
tasks to ensure they succeeded. It outputs the number of passing and failing
tasks (or only success if no tasks fail) and shows a progress bar.

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

## Usage

After installation, you can use the `searchable-files` script.

> **WARNING**: Always run `searchable-files` from the top level of the
> repository, unless you pass additional options. Its defaults are all written
> as relative paths with respect to this directory.

### Setup

Before running any of the steps, you must run

    ./searchable-files login

This will log you in to Globus and write your credentials to
`~/.globus_searchable_files.db`.

After login, run

    ./searchable-files create-index

This will create a new index for you to use Searchable Files.
Its index ID will be stored in `~/.globus_searchable_files.db`.

Running `./searchable-files create-index` a second time will print a message
stating that the index already exists and giving you the index ID.

You can also run

    ./searchable-files show-index

to get info about your index.

### Running the Workflow

Each component of the Searchable Files App is run with a separate
subcommand, and each one supports a `--help` option for full details on its
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

The `searchable-files` tool includes a query command which you can use to
search your files.

See

    ./searchable-files query --help

for more details.

You can filter in various ways using this. For example

    ./searchable-files query "foo" --types-or=text,png

will submit a query which matches `"foo"` and requires that the files matched
have either the `txt` or `png` type.


    ./searchable-files query "foo" --types=text,non-executable

will find results which are both text files and not executable.

#### Testing Unauthenticated Queries

By default, queries are made authenticated as the logged-in user. For
comparison, the query command supports a `--no-auth` flag, which will make the
query submitted unauthenticated.

This will result in any results which are only visible due to `visible_to`
filtering disappearing from the results. Only "public" results will remain
visible.

On the example data, you should see a difference between

    ./searchable-files '*' --extensions=sh

and

    ./searchable-files '*' --extensions=sh --no-auth

#### Dumping the Query

Finally, if you want to inspect the query which the `searchable-files` command
is generating instead of submitting it to the Search service, you can use
`--dump-query` to write the query to standard out, as in

    ./searchable-files query "foo" --types=tar --dump-query

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

The only special consideration when modifying these components is that the use
the Index ID retrieved from `create-index`. If modifying or replacing these
commands, it may be necessary to replace the logic which loads the `index_id`
from storage.
