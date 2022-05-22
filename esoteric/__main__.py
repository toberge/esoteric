import sys

import click

import esoteric.gui as gui
from esoteric.befunge import Befunge
from esoteric.fish import Fish


@click.command()
@click.argument(
    "filepath", type=click.Path(exists=True, dir_okay=False), required=False
)
@click.option(
    "-g",
    "--use-gui",
    "--gui",
    is_flag=True,
    help="Interpret visually in a GUI (or TUI if you wish).",
)
@click.option(
    "-v",
    "--value",
    default=None,
    type=click.INT,
    required=False,
    help="Initial value for the stack.",
)
@click.option(
    "-l",
    "--language",
    default=None,
    type=click.Choice(["befunge", "fish"]),
    required=False,
    help="Which esoteric language to interpret – include this when executing from stdin or a file without a proper extension.",
)
def main(filepath, use_gui, value, language):
    code = ""
    if filepath is not None:
        with open(filepath) as file:
            if language is None:
                language = filepath.split(".")[-1]
            code = file.read()
    else:
        code = sys.stdin.read()

    if code == "":
        print("No code in stdin or file", file=sys.stderr)
        exit(1)

    if language == "fish":
        program = Fish.from_string(code)
    else:
        program = Befunge.from_string(code)

    if value is not None and program.__getattribute__("stack") is not None:
        program.stack = [value]

    if use_gui:
        gui.main(program)
    else:
        program.run()


if __name__ == "__main__":
    main()
