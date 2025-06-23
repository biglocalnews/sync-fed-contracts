import logging
import os
import zipfile
from glob import glob
from importlib import reload
from pathlib import Path

from tqdm import tqdm

# Very basic config
datadir = "data/"
archivefile = f"{datadir}archived_json.zip"

# Force logging
reload(logging)
logging.basicConfig(
    format="%(asctime)s %(levelname)s:%(message)s",
    level=logging.DEBUG,
    datefmt="%I:%M:%S",
)
logger = logging.getLogger()


def archive_json(deleteafterarchiving=True):
    rawfiles = list_loose_json()
    logger.debug(f"{len(rawfiles):,} loose JSON files might get added to the ZIP.")
    if len(rawfiles) == 0:
        return
    jsonlist = list_archived_json()
    duplicates = []
    for rawfile in rawfiles:
        if rawfile in jsonlist:
            duplicates.append(rawfile)
    if len(duplicates) > 0:
        message = (
            f"{len(duplicates):,} duplicates found, b
            
def list_archived_json():
    if not os.path.exists(archivefile):
        logger.warning(f"No archive file at {archivefile} found")
        zippedfiles = []
    else:
        with zipfile.ZipFile(archivefile, "r") as myzip:
            zippedfiles = myzip.namelist()
            logger.debug(f"{len(zippedfiles):,} files found in {archivefile}")
    return zippedfiles


def list_loose_json():
    rawfilesraw = glob(datadir + "*.json")
    rawfiles = []
    for rawfileraw in rawfilesraw:
        rawfiles.append(str(Path(rawfileraw).relative_to(datadir)))
    return rawfiles
