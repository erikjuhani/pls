"""
This package contains code for invoking `to-html`_ and processing its output.

.. _to-html: https://github.com/Aloso/to-html/
"""

import re
from decouple import config

from examples.utils.sub import run_cmd


def run_to_html(args: list[str], **kwargs) -> str:
    """
    Invoke ``to-html`` with a ``pls`` command and return the HTML output.

    This function creates a ``pls`` command using the given arguments, runs it
    with ``to-html`` so that the HTML is printed to STDOUT and then
    post-processes the HTML into something the docs site can readily use.

    It assumes the project root to be the working directory and that a release
    build of ``pls`` is present on the ``$PATH``.

    All keyword arguments are forwarded as-is to ``run_cmd``.

    :return: the processed HTML output
    """

    pls_bin = config("PLS_BIN", default="pls")
    args = " ".join(args)
    cmd = ["to-html", f"{pls_bin} {args}"]
    print(f"Running command {cmd}")

    proc = run_cmd(cmd, **kwargs)
    html = proc.stdout
    return _cleanup_html(html)


def _cleanup_html(html: str) -> str:
    """
    Clean up the HTML generated by ``to-html`` to make it fit for pasting into
    the ``pls`` documentation.

    This function
    - removes lines that contain the command given to the shell
    - invokes ``_substitutions`` on the remaining lines
    - inserts a zero-width space at the beginning of the second line

    :param html: the HTML captured by ``to-html`` that requires cleaning
    :return: the cleaned up HTML to use in the docs
    """

    lines = [
        _substitutions(line) if line else '<span style="opacity:0;">&nbsp;</span>'
        for line in html.split("\n")
        if "<span class='shell'>" not in line
    ]
    lines[1] = f"​{lines[1]}"
    return "\n".join(lines)


def _substitutions(line: str) -> str:
    """
    Perform substitutions on a line of HTML generated by ``to-html``.

    This function
    - replaces leading space with ``&nbsp;`` to prevent de-denting lines
    - removes default color from the ``color`` rule in the ``style`` attribute

    :param line: one line of the HTML generated by ``to-html``
    :return: the cleaned-up line
    """

    line = re.sub(r"^\s", "&nbsp;", line)
    line = re.sub(
        r"color:var\(--(?P<color>\w+),#[0-9a-f]+\)",
        r"color:var(--\g<color>)",
        line,
    )
    return line
