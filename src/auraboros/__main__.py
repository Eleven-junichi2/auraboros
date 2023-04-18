from pathlib import Path
import subprocess
# import sys
import inspect

import click


def example():
    __main__py_path = Path(inspect.getfile(inspect.currentframe()))
    example_dir = __main__py_path.parent / "debugs"
    print(__main__py_path)
    example_scripts = [f for f in example_dir.glob(
        "*.py") if f.name not in ("init_for_dev.py", "__init__.py")]
    click.echo(f"Here are {len(example_scripts)} examples:")
    for i, file_name in enumerate(example_scripts):
        click.echo(f"{i} {file_name.name} ({file_name})")
    example_num = click.prompt(
        "Choose an example to try:", type=int, default=0)
    subprocess.run(["python", example_scripts[example_num]])


def getasset():
    pass


@click.command()
@click.option('--example', is_flag=True, required=False,
              help="navigate to choose example scripts.")
@click.option('--getasset', is_flag=True, required=False,
              help="download assets into assets at current working directory")
def cli(example, getasset):
    if example:
        example()
    elif getasset:
        getasset()
    else:
        click.echo(click.get_current_context().get_help())


if __name__ == '__main__':
    cli()
