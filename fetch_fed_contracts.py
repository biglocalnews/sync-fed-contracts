#!/usr/bin/env python
# coding: utf-8

import asyncio
import datetime
import json
import logging
import os
from importlib import reload
from itertools import chain

from fpds import fpdsRequest
from tqdm import tqdm

import utils

yesterday = (datetime.datetime.now() - datetime.timedelta(hours=24)).strftime(
    "%Y/%m/%d"
)
today = datetime.datetime.now().strftime("%Y/%m/%d")
timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")

reasons = {
    "E": "Terminate for default",
    "F": "Terminate for convenience",
    "K": "Close out",
    "N": "Legal contract cancellation",
    "X": "Terminate for cause",
}

datadir = "data/"

os.makedirs(datadir, exist_ok=True)

# Force logging
reload(logging)
logging.basicConfig(
    format="%(asctime)s %(levelname)s:%(message)s",
    level=logging.DEBUG,
    datefmt="%H:%M:%S",
)
logger = logging.getLogger()


def screen_files(localdate: datetime):
    """
    Given a date, determine whether any files are missing.

    Args:
        localdate: datetime object
    Returns:
        needfiles: boolean showing whether any files were missing
    """
    needfiles = False
    filedate = localdate.strftime("%Y-%m-%d")
    for reason in reasons:
        filename = f"contracts-{filedate}_{reason}.json"
        if filename not in json_avail:
            needfiles = True
        # if not os.path.exists(filename):
        #    needfiles = True
    if needfiles:
        logger.debug(f"Need files for {localdate}")
    return needfiles


async def fetch_a_date(localdate: datetime):
    """
    Retrieve data files for a particular date.

    Args:
        localdate: datetime object showing desired date
    Returns:
        If no files needed, return value is None
        If files are needed, ... I think it builds a dictionary by reasoncode with file-level contents as the value.
        Why, yes, someone else wrote this and it's stable.
    """
    needfiles = screen_files(localdate)
    if not needfiles:
        return None
    else:
        requests = {}
        requestdate = localdate.strftime("%Y/%m/%d")
        async with asyncio.TaskGroup() as tg:
            for reason in reasons:
                request = fpdsRequest(
                    LAST_MOD_DATE=f"[{requestdate}, {requestdate}]",
                    REASON_FOR_MODIFICATION=f"{reason}",
                )
                requests[reason] = tg.create_task(request.data())
        return {
            reason: list(chain.from_iterable(request.result()))
            for (reason, request) in requests.items()
        }


def run_pipeline(environment):
    utils.fetch_json_archive()
    global json_avail
    json_avail = utils.list_json()  # Get list of available JSON.
    today = datetime.datetime.now()
    start = datetime.datetime(2025, 1, 20)
    days_to_find = (today - start).days
    print(
        f"Reviewing records for {days_to_find:,} days. Any downloads will take some time."
    )

    # Build out a progress bar, because the code runs take time.
    with tqdm(total=days_to_find, desc="1900-00-00") as pbar:
        for dateincrement in range(0, days_to_find):  # Current date/today has no data
            targetdate = start + datetime.timedelta(days=dateincrement)
            filedate = targetdate.strftime("%Y-%m-%d")
            pbar.set_description(filedate)
            data = asyncio.run(fetch_a_date(targetdate))
            if data:  # If we got data back, not a None, save the data
                for reason in reasons:
                    filename = f"{datadir}/contracts-{filedate}_{reason}.json"
                    localdata = data[reason]
                    with open(filename, "w", encoding="utf-8") as outfile:
                        outfile.write(json.dumps(localdata, indent=4 * " "))
            pbar.update(1)
