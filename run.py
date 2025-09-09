import logging

from export_fed_contracts import run_pipeline as export_run_pipeline
from fetch_fed_contracts import run_pipeline as fetch_run_pipeline

from utils import set_environment

"""
sync-fed-contracts

These scripts extract important data from the U.S. federal government's contract records.

The Trump administration began cancelling projects en masse in early 2025. These scripts
retrieve data for a number of cancellation types; send it back to Big Local News' archives,
and extracts a friendlier, CSV-formatted collection of highlights from the most relevant
cancellation category. It also exports a much more limited set of highlights to power an
interactive built for Big Local News' Data+ members.

"""

logging.basicConfig(
    format="\n%(asctime)s %(levelname)s: %(message)s",
    level=logging.DEBUG,
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    print("Determining environment ...")
    environment = set_environment()
    print("Retrieving sync-fed-contracts data ...")
    fetch_run_pipeline(environment)
    print("Processing and exporting sync-fed-contracts data ...")
    export_run_pipeline(environment)
