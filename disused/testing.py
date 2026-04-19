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


if __name__ == "__main__":
    today = datetime.datetime.now()
    start = datetime.datetime(2025, 1, 20)
    localdate = datetime.datetime(2026, 3, 15)
    filedate = "2026-03-15"
    data = asyncio.run(fetch_a_date(localdate))
    if data:  # If we got data back, not a None, save the data
        for reason in reasons:
            filename = f"{datadir}/contracts-{filedate}_{reason}.json"
            localdata = data[reason]
            with open(filename, "w", encoding="utf-8") as outfile:
                outfile.write(json.dumps(localdata, indent=4 * " "))




# fpds parse "LAST_MOD_DATE=[2026/03/15, 2026/03/15]" "REASON_FOR_MODIFICATION=N"