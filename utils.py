from glob import glob
import logging
import os
from pathlib import Path
import zipfile

datadir = "data/"
archivefile = f"{datadir}archive.zip"

from importlib import reload
reload(logging)
logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=logging.DEBUG, datefmt='%I:%M:%S')
logger = logging.getLogger()
logger.setLevel('DEBUG')

def archive_json(deleteafterarchiving=True):
    rawfiles = list_loose_json()
    logger.debug(f"{len(rawfiles):,} loose JSON files might get archived.")
    if len(rawfiles) == 0:
        return
    jsonlist = list_archived_json()
    duplicates = []
    for rawfile in rawfiles:
        if rawfile in jsonlist:
            duplicates.append(rawfile)
    if len(duplicates) > 0:
        message = f"{len(duplicates):,} duplicates found, both loose JSON and in the ZIP. "
        message += f"You'll want to clear these out yourself. This program will neither replace nor "
        mesage += "delete them."
        logger.debug(message)
    for duplicate in duplicates:
        jsonlist.remove(duplicate)
    if len(rawfiles) == 0:
        return
    logger.debug(f"Confirmed: Writing {len(rawfiles):,} files to archive.")
    with ZipFile(archivefile, "a", compression=ZIP_DEFLATED, compresslevel=9) as myzip:
        for rawfile in rawfiles:
            myzip.write(filename=datadir + rawfile,
                arcname = rawfile,
                compress_type=ZIP_DEFLATED,
                compresslevel=9
                )
            if deleteaafterarchiving:
                os.remove(datadir + rawfile)
    # Need to upload to BLN after this
    return


def list_json():
    rawfiles = list_loose_json()
    zippedfiles = list_archived_json()
    return(zippedfiles.extend(rawfiles))


def list_archived_json():
    if not os.path.exists(archivefile):
        zippedfiles = []
    else:
        with ZipFile(archivefile, "r") as myzip:
            zippedfiles = myzip.namelist()
    return(zippedfiles)


def list_loose_json():
    rawfilesraw = glob(datadir + "*.json")
    rawfiles = []
    for rawfileraw in rawfilesraw:
        rawfiles.append(Path(rawfileraw).relative_to(datadir))
    return(rawfiles)
