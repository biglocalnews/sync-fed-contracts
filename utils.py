import logging
import os
import sys
import zipfile
from glob import glob
from importlib import reload
from pathlib import Path

from dotenv import load_dotenv
from tqdm import tqdm

# Very basic config
datadir = "data/"
archivefile = f"{datadir}archived_json.zip"

# Force logging
reload(logging)
logging.basicConfig(
    format="%(asctime)s %(levelname)s:%(message)s",
    level=logging.DEBUG,
    datefmt="%H:%M:%S",
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
        message += "You'll want to clear these out yourself. This program will neither replace nor "
        message += "delete them."
        logger.debug(message)
    for duplicate in duplicates:
        rawfiles.remove(duplicate)
    logger.debug(f"{len(rawfiles):,} files remain to be added to the ZIP.")
    if len(rawfiles) == 0:
        return
    logger.debug(f"Confirmed: Writing {len(rawfiles):,} files to archive.")
    with zipfile.ZipFile(
        archivefile, "a", compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as myzip:
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
    zippedfiles.extend(rawfiles)
    logger.debug(f"{len(zippedfiles):,} total files found, with possible overlaps.")
    return zippedfiles


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
    logger.debug(f"{len(rawfiles):,} files found loose.")
    return rawfiles


def set_environment():
    """
    Load and validate environment variables from a `.env.<env>` file based on a required command-line argument.

    This function:
    - Requires the first command-line argument to be either 'test' or 'prod'
    - Loads environment variables from the corresponding `.env.test` or `.env.prod` file
    - Verifies that all required environment variables are present and non-empty
    - Logs success or exits with errors if configuration is missing or invalid

    Returns:
        str: The name of the environment that was successfully loaded ('test' or 'prod').

    Raises:
        SystemExit: If the CLI argument is missing or invalid.
        RuntimeError: If any required environment variable is missing or empty.
    """
    if len(sys.argv) < 2:
        logger.error("python run.py <test|prod>")
        sys.exit(1)

    env = sys.argv[1].strip()
    if env not in ["test", "prod"]:
        logger.error(f"Invalid env '{env}'. Use 'test' or 'prod'.")
        sys.exit(1)

    # Get the directory this script is in
    script_dir = Path(__file__).parent
    # Build path to the .env file relative to this script
    dotenv_path = script_dir / f".env.{env}"

    logger.info(f"Loading environment from: {dotenv_path}")
    load_dotenv(dotenv_path=dotenv_path, override=True)
    # make sure all required env vars are present
    required_env_vars = [
        "BLN_API_TOKEN",
        "BLN_PROJECT_ID",
        "SLACK_ERROR_TOKEN",
        "SLACK_ERROR_CHANNEL_ID",
    ]
    for key in required_env_vars:
        value = os.environ.get(key)
        if not value or not value.strip():
            logger.error(f"Missing or empty: {key} (from {dotenv_path})")
            raise RuntimeError(
                f"Required env variable '{key}' is missing or empty in {dotenv_path}"
            )
    logger.info(f"{dotenv_path} successsfully loaded")
    return env

