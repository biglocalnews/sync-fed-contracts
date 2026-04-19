#!/usr/bin/env python
# coding: utf-8

import asyncio
import datetime
import json
import os
# import socket
# from glob import glob
# from itertools import chain

from fpds import fpdsRequest
from tqdm import tqdm

from utils import *

yesterday = (datetime.datetime.now() - datetime.timedelta(hours=24)).strftime(
    "%Y/%m/%d"
)
today = datetime.datetime.now().strftime("%Y/%m/%d")
timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")

reasons = ["E", "F", "K", "N", "X"]

datadir = "data/"

os.makedirs(datadir, exist_ok=True)

# Force logging
reload(logging)
logging.basicConfig(
    format="%(asctime)s %(levelname)s:%(message)s",
    level=logging.DEBUG,
    datefmt="%I:%M:%S",
)
logger = logging.getLogger()

json_avail = list_json()

bad_dates = []  # This was built to exclude dates where '"title",' was on a line.
# The data processing bug that created this should be fixed,
# so this is vestigial code that ... should not ... be needed. Again.


def screen_files(localdate):
    needfiles = False
    filedate = localdate.strftime("%Y-%m-%d")
    for reason in reasons:
        filename = f"contracts-{filedate}_{reason}.json"
        if filename not in json_avail:
            needfiles = True
        # if not os.path.exists(filename):
        #    needfiles = True
    if needfiles and filedate in bad_dates:
        logger.debug(
            f"! Missing files for {filedate}, but it's marked as bad data. Skipping."
        )
        needfiles = False
    elif needfiles and filedate not in bad_dates:
        logger.debug(f"Need files for {localdate}")
    return needfiles


"""
# This was resulting in some buggy files.
async def fetch_a_date(localdate):
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
"""


def fetch_date_by_reason(datewanted: datetime, reasoncode: str):
    datestr = datewanted.strftime("%Y/%m/%d")

    params_kwargs = {
        "LAST_MOD_DATE": f"[{datestr}, {datestr}]",
        "REASON_FOR_MODIFICATION": '"' + reasoncode + '"',
    }

    request = fpdsRequest(**params_kwargs, cli_run=False)
    records = asyncio.run(request.data())
    return records


if __name__ == "__main__":
    today = datetime.datetime.now()
    start = datetime.datetime(2025, 1, 20)
    days_to_find = (today - start).days
    print(
        f"Reviewing records for {days_to_find:,} days. Any downloads will take some time."
    )

    # Build out a progress bar, because the code runs take time.
    with tqdm(total=days_to_find, desc="1900-00-00Z") as pbar:
        for dateincrement in range(0, days_to_find):  # Current date/today has no data
            targetdate = start + datetime.timedelta(days=dateincrement)
            filedate = targetdate.strftime("%Y-%m-%d")
            pbar.set_description(filedate)
            if screen_files(targetdate):  # If we need data for the days
                for reason in reasons:
                    pbar.set_description(f"{filedate}{reason}")
                    localdata = fetch_date_by_reason(targetdate, reason)
                    filename = f"{datadir}/contracts-{filedate}_{reason}.json"
                    with open(filename, "w", encoding="utf-8") as outfile:
                        outfile.write(json.dumps(localdata, indent=4 * " "))
            pbar.update(1)
