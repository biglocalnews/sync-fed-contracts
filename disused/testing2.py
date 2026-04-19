#!/usr/bin/env python
# coding: utf-8

import asyncio
import datetime
import json
import os
import socket
from glob import glob
from itertools import chain

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

bad_dates = ["2025-11-13", "2025-11-14", "2025-11-15"]


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

async def fetch_a_date_by_code(localdate, reason):
    requestdate = localdate.strftime("%Y/%m/%d")
    request = fpdsRequest(
        LAST_MOD_DATE=f"[{requestdate}, {requestdate}]",
        REASON_FOR_MODIFICATION=f"{reason}",
            )
#     records = await asyncio.run(request.data())
    # returns records as an async generator
    gen = request.iter_data()

    # evaluating generator entries
    records = []
    async for entry in gen:
        records.append(entry)
    return records


if __name__ == "__main__":
    today = datetime.datetime.now()
    # HEY! start = datetime.datetime(2025, 1, 20)
    start = datetime.datetime(2026, 3, 15)
    days_to_find = (today - start).days
    print(
        f"Reviewing records for {days_to_find:,} days. Any downloads will take some time."
    )

    # Build out a progress bar, because the code runs take time.
    with tqdm(total=days_to_find, desc="1900-00-00?") as pbar:
        for dateincrement in range(0, days_to_find):  # Current date/today has no data
            targetdate = start + datetime.timedelta(days=dateincrement)
            filedate = targetdate.strftime("%Y-%m-%d")
            needfiles = screen_files(targetdate)
            if needfiles:
                for reason in reasons:
                    pbar.set_description(f"{filedate}{reason}")
                    localdata = asyncio.run(fetch_a_date_by_code(targetdate, reason))
                    filename = f"{datadir}/contracts-{filedate}_{reason}.json"
                    with open(filename, "w", encoding="utf-8") as outfile:
                        outfile.write(json.dumps(localdata, indent=4 * " "))
            pbar.update(1)



# Sample failure: 2026/03/15, type N
# $  fpds parse "LAST_MOD_DATE=[2026/03/15, 2026/03/15]" "REASON_FOR_MODIFICATION=F" # -o ~/.my-preferred-dir