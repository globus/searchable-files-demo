import click


def common_options(f):
    # any shared/common options for all commands
    return click.help_option("-h", "--help")(f)
