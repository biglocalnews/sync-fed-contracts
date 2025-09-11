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

json_avail = list_json()


def screen_files(localdate):
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


if __name__ == "__main__":
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
