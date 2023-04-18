from collections import OrderedDict
from pathlib import Path
from urllib.parse import urlparse
import inspect
import json
import ssl
import subprocess
import tarfile
import urllib.error
import urllib.parse
import urllib.request
import zipfile

try:
    import click
except ModuleNotFoundError:
    print("auraboros use 'click' for implement CLI.")
    print("Try 'pip install click' to install it.")

__main__py_path = Path(inspect.getfile(inspect.currentframe()))
getasset_order_filepath = __main__py_path.parent / "getasset_order.json"


def filename_from_url(content_disposition, url) -> str:
    if content_disposition:
        filename = content_disposition.split("filename=")[1].strip('"')
    else:
        filename = Path(urllib.parse.unquote(url.split('/')[-1])).name
    return filename


def calc_best_chunk_size_of_dl(filesize):
    for i in range(0, 2):
        if filesize < 1024 * 1024 * (10 ** i):
            chunk_size = 1024 * (10 ** i)
            filesize_is_large = False
        else:
            filesize_is_large = True
    if filesize_is_large:
        chunk_size = 1024 ** 2
    return chunk_size


def without_suffix_of_compressed_file(filepath) -> Path:
    if ".tar.gz" in "".join(Path(filepath).suffixes):
        filepath = Path(filepath).parent / Path(filepath).stem
        filepath = Path(filepath).parent / Path(filepath).stem
        return filepath
    elif ".zip" in "".join(Path(filepath).suffixes):
        filepath = Path(filepath).parent / Path(filepath).stem
        return filepath


def extract_compressed_file(
        path_compressed_file, dir_extract_to, show_progress=False):
    if "tar.gz" in "".join(Path(path_compressed_file).suffixes):
        with tarfile.open(path_compressed_file, "r:gz") as tar:
            tar.extractall(dir_extract_to)
    elif ".zip" in "".join(Path(path_compressed_file).suffixes):
        with zipfile.ZipFile(path_compressed_file, "r") as zip_:
            if show_progress:
                total_size = sum(info.file_size for info in zip_.infolist())
                extracted_size = 0
                with click.progressbar(
                        zip_.infolist(),
                        length=len(zip_.infolist()),
                        label="Extracting files ...") as bar:
                    for info in bar:
                        zip_.extract(info, dir_extract_to)
                        extracted_size += info.file_size
                        bar.update(int(extracted_size / total_size * 100))
            else:
                zip_.extractall()


def example_process():
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


def getasset_process():
    dirname_of_the_asset_type = {
        "font": "fonts",
        "image": "imgs",
        "sound": "sounds"
    }
    asset_dir = click.prompt(
        "directory to put assets",
        type=click.Path(file_okay=False, exists=True),
        default=Path.cwd() / "assets")
    with open(getasset_order_filepath, "r") as f:
        assets = OrderedDict(json.load(f))
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
    is_confirmed = click.confirm("Are you sure to download?")
    if not is_confirmed:
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
            filename = filename_from_url(content_disposition, url)
            click.echo(filename)
            download_to = asset_dir / \
                dirname_of_the_asset_type[asset_info["type"]] / filename
            filesize = int(response.headers.get("Content-Length", 0))
            chunk_size = calc_best_chunk_size_of_dl(filesize)
            if not Path(download_to).parent.exists():
                Path(download_to).parent.mkdir()
            with open(download_to, mode="wb") as f,\
                click.progressbar(
                    length=filesize, label="Downloading...") as bar:
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    bar.update(len(chunk))
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
    is_confirmed = click.confirm(
        "Would you like to unzip/untar the downloaded files?")
    if not is_confirmed:
        return
    extract_to = without_suffix_of_compressed_file(download_to)
    try:
        extract_compressed_file(download_to, extract_to, True)
        click.echo(
            click.style(
                f"Extract completed successfully\n-> {extract_to}",
                fg="green"))
    except Exception as e:
        raise e


@click.command()
@click.option(
    '--example', is_flag=True, required=False,
    help="navigate to choose example scripts.")
@click.option(
    '--getasset', is_flag=True, required=False,
    help=f"Select and download assets listed in {getasset_order_filepath}.")
def cli(example, getasset):
    if example:
        example_process()
    elif getasset:
        getasset_process()
    else:
        click.echo(click.get_current_context().get_help())


if __name__ == '__main__':
    cli()
