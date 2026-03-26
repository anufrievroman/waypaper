import sys


def display_info(message: str, only_tty = True):
    """Display a message to stdout only if the output is not piped."""
    if only_tty and not sys.stdout.isatty():
        return

    print(message, file=sys.stdout)


def display_warning(message: str):
    """Display a warning."""
    display_info(message)


def display_error(message: str):
    """Output a message to stderr."""
    print(message, file=sys.stderr)