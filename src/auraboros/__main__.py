from pathlib import Path
import subprocess

import click


@click.command()
@click.option('--example', is_flag=True, required=False,
              help="navigate to choose example scripts.")
def cli(example):
    if example:
        example_dir = Path(__file__).parent.parent / "debugs"
        example_scripts = [f for f in example_dir.glob(
            "*.py") if not f.name == "init_for_dev.py"]
        click.echo(f"Here are {len(example_scripts)} examples:")
        for i, file_name in enumerate(example_scripts):
            click.echo(f"{i} {file_name.name} ({file_name})")
        example_num = click.prompt(
            "Choose an example to try:", type=int, default=0)
        subprocess.run(["python", example_scripts[example_num]])
    else:
        click.echo(click.get_current_context().get_help())


if __name__ == '__main__':
    cli()
