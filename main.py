# imports
import typer
from typing import Annotated, List, Optional
from rich import print
import errno
import os
from copier import run_copy
import pandas as pd

app = typer.Typer()

# import zipline modules
from zipline.data import bundles as bundles_module

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
    run_copy("./bundle_template", "./new_bundle")
   

@app.command()
def delete(bundle_name, bundle_data):
    """Delete a zipline data bundle."""
    # delete the bundle
    bundle_data.delete(bundle_name)

    # return the bundle data
    return bundle_data

def main(name: str = typer.Argument(..., help="The name of the person to greet.", metavar="NAME", show_default="World")):
    print(f"Hello {name}!")

@app.command()
def ingest(bundle: Annotated[str, typer.Option(["-b", "--bundle"], help="The data bundle to ingest.", metavar="BUNDLE-NAME", show_default=True)] = DEFAULT_BUNDLE,
           assets_version: Annotated[int, typer.Option("--assets-version", help="Version of the assets db to which to downgrade.")] = None,
           show_progress: Annotated[bool, typer.Option(default=True, help="Print progress information to the terminal.")] = True):
    """Ingest the data for the given bundle."""
    bundles_module.ingest(
        bundle,
        os.environ,
        pd.Timestamp.utcnow(),
        assets_version,
        show_progress,
    )

if __name__ == '__main__':
    app()

# end of script‚