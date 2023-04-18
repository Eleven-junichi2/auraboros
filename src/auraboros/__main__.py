from collections import OrderedDict
from pathlib import Path
from urllib.parse import urlparse
import ssl
import subprocess
import urllib.request
import urllib.error
import urllib.parse
import inspect

import click


def example_process():
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


def _progress_of_download(block_count: int, block_size: int, total_size: int):
    progress_bar = click.progressbar(length=total_size, label="Downloading...")
    downloaded = block_count * block_size
    if downloaded < total_size:
        progress_bar.update(downloaded - progress_bar.pos)
    else:
        progress_bar.update(total_size - progress_bar.pos)
    progress_bar.render_progress()


def getasset_process():
    dirname_of_the_asset_type = {
        "font": "fonts"
    }
    asset_dir = click.prompt(
        "directory to put assets",
        type=click.Path(file_okay=False, exists=True),
        default=Path.cwd() / "assets")
    assets = OrderedDict()
    assets["misaki"] = \
        {"url": "https://littlelimit.net/arc/misaki/misaki_ttf_2021-05-05.zip",
         "type": "font",
         "license": "Read the attached file."}
    assets["ayu18mincho"] = \
        {"url": "https://ja.osdn.net/frs/redir.php?m=nchc&f=x-tt%2F8494%2Fayu18mincho-1.1.tar.gz",
         "type": "font",
         "license": "public"}
    for i, (asset_name, asset_info) in enumerate(
            zip(assets.keys(), assets.values())):
        click.echo(f"{i} {asset_name} ({asset_info['type']})")
    request_num = click.prompt(
        "Choose the asset you wish to use", type=int, default=0)
    asset_name = list(assets.keys())[request_num]
    asset_info = list(assets.values())[request_num]
    click.echo(
        f"{asset_name}({asset_info['type']})" +
        f"\nlicense: {asset_info['license']}")
    is_confirm = click.confirm("Are you sure to download?")
    if not is_confirm:
        return
    url = asset_info["url"]
    context = ssl.create_default_context()
    domain = urlparse(url).netloc
    if domain == "ja.osdn.net":
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
    try:
        with urllib.request.urlopen(url, context=context) as response:
            content_disposition = response.headers.get("Content-Disposition")
            if content_disposition:
                filename = content_disposition.split('filename=')[1].strip('"')
            else:
                filename = Path(urllib.parse.unquote(url.split('/')[-1])).name
            print(filename)
            download_to = asset_dir / \
                dirname_of_the_asset_type[asset_info["type"]] / filename
            with open(download_to, mode="wb") as f:
                content = response.read()
                f.write(content)
    except urllib.error.HTTPError as e:
        click.echo(f'HTTPError: {e.code} {e.reason}')
    except urllib.error.URLError as e:
        click.echo(f'URLError: {e.reason}')
    else:
        click.echo(
            click.style(
                f"Download completed successfully\n-> {download_to}",
                fg="green"))
        click.echo(
            click.style(
                "Be careful: You must comply with licence of the assets.",
                fg="red"))


@click.command()
@click.option('--example', is_flag=True, required=False,
              help="navigate to choose example scripts.")
@click.option('--getasset', is_flag=True, required=False,
              help="download assets into assets at current working directory")
def cli(example, getasset):
    if example:
        example_process()
    elif getasset:
        getasset_process()
    else:
        click.echo(click.get_current_context().get_help())


if __name__ == '__main__':
    cli()
