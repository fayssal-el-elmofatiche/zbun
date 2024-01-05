# imports
from typing import Annotated, List, Optional
from rich import print
import errno
import os
from copier import run_copy
import typer
from pathlib import Path
import yaml
import importlib
import warnings
warnings.filterwarnings("ignore")

app = typer.Typer()

# import zipline modules
from zipline.data import bundles as bundles_module
from zipline.utils.calendar_utils import get_calendar_names
from zipline.data.bundles import register

DEFAULT_BUNDLE = "quandl"

@app.command()
def bundles():
    """List all of the available data bundles."""
    for bundle in sorted(bundles_module.bundles.keys()):
        if bundle.startswith("."):
            # hide the test data
            continue
        try:
            ingestions = list(map(str, bundles_module.ingestions_for_bundle(bundle)))
        except OSError as e:
            if e.errno != errno.ENOENT:
                raise
            ingestions = []

        # If we got no ingestions, either because the directory didn't exist or
        # because there were no entries, print a single message indicating that
        # no ingestions have yet been made.
        for timestamp in ingestions or ["<no ingestions>"]:
            print("%s %s" % (bundle, timestamp))

@app.command()
def new():
    """Create scafold for a new zipline data bundle."""
    # create a project from a local path
    run_copy("git+https://github.com/fayssalelmofatiche/zbun_template.git")
   

@app.command()
def delete(bundle_name, bundle_data):
    """Delete a zipline data bundle."""
    # delete the bundle
    bundle_data.delete(bundle_name)

    # return the bundle data
    return bundle_data

@app.command()
def calendars():
    """List all of the available trading calendars."""
    for name in sorted(get_calendar_names()):
        print(name)

@app.command()
def ingest(bundle_dir: str = typer.Option(".", "--dir", "-d", help="The directory of the bundle to ingest.")):
    """Ingest data for a given bundle in current directory."""
    p = Path(bundle_dir)

    print(f"Bundle directory: {p.absolute()}")
    zbundle_yaml_path = p.joinpath("zbundle.yaml")
    print(f"zbundle.yaml path: {zbundle_yaml_path.absolute()}")

    # check if folder contains zbundle.yaml
    if not zbundle_yaml_path.is_file():
        raise typer.Exit(f"No zbundle.yaml file found in given directory[{zbundle_yaml_path.absolute()}]. Please run `zbundle new` to create a new bundle, or `zbundle ingest` in a bundle directory.")
    
    # read bunlde name and calendar from zbundle.yaml
    with open(zbundle_yaml_path, 'r') as f:
        try:
            zbundle_yaml = yaml.safe_load(f)
            bundle_name = zbundle_yaml["bundle"]["name"]
            bundle_calendar = zbundle_yaml["bundle"]["calendar"]
            bundle_module = zbundle_yaml["bundle"]["module"]
        except yaml.YAMLError as exc:
            print(exc)

    print(f"Bundle name: {bundle_name}")
    print(f"Bundle calendar: {bundle_calendar}")
    print(f"Bundle module: {bundle_module}")

    # cd to bundle directory
    os.chdir(p)

    # print content of directory
    print(os.listdir())

    # import bundle module
    module = importlib.import_module(bundle_module)

    # run test_load function from bundle module
    module.test_module()

    # register the bundle
    print(f"Registering bundle {bundle_name} with calendar {bundle_calendar}")
    register(bundle_name, module.process_data, calendar_name=bundle_calendar)

    # ingest the bundle
    print(f"Ingesting bundle {bundle_name}")
    bundles_module.ingest(bundle_name)

    # list bundles
    #bundles()

if __name__ == '__main__':
    app()

# end of script‚