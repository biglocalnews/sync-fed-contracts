import logging
import os
import zipfile
from glob import glob
from importlib import reload
from pathlib import Path

from tqdm import tqdm

# Very basic config
datadir = "data/"
archivefile = f"{datadir}archive.zip"

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
            f"{len(duplicates):,} duplicates found, both loose JSON and in the ZIP. "
        )
        message += f"You'll want to clear these out yourself. This program will neither replace nor "
        message += "delete them."
        logger.debug(message)
    for duplicate in duplicates:
        rawfiles.remove(duplicate)
    logger.debug(f"{len(rawfiles):,} files remain to be added to the ZIP.")
    if len(rawfiles) == 0:
        return
    logger.debug(f"Confirmed: Writing {len(rawfiles):,} files to archive.")
    with zipfile.ZipFile(archivefile, "a", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as myzip:
        for rawfile in tqdm(rawfiles):
            myzip.write(
                filename=datadir + rawfile,
                arcname=rawfile,
                compress_type=zipfile.ZIP_DEFLATED,
                compresslevel=9,
            )
            if deleteafterarchiving:
                os.remove(datadir + rawfile)
    # Need to upload to BLN after this ... or just handle with any in_production pushing?
    return


def list_json():
    rawfiles = list_loose_json()
    zippedfiles = list_archived_json()
    return zippedfiles.extend(rawfiles)


def list_archived_json():
    if not os.path.exists(archivefile):
        zippedfiles = []
    else:
        with zipfile.ZipFile(archivefile, "r") as myzip:
            zippedfiles = myzip.namelist()
    return zippedfiles


def list_loose_json():
    rawfilesraw = glob(datadir + "*.json")
    rawfiles = []
    for rawfileraw in rawfilesraw:
        rawfiles.append(str(Path(rawfileraw).relative_to(datadir)))
    return rawfiles
