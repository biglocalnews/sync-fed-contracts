#!/usr/bin/env python
# coding: utf-8

import asyncio
import datetime
import json
import os
import socket
from glob import glob
from itertools import chain

from bln.client import Client
from fpds import fpdsRequest
from tqdm import tqdm

yesterday = (datetime.datetime.now() - datetime.timedelta(hours=24)).strftime(
    "%Y/%m/%d"
)
today = datetime.datetime.now().strftime("%Y/%m/%d")
timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")

reasons = ["E", "F", "K", "N", "X"]

datadir = "data/"

os.makedirs(datadir, exist_ok=True)


def screen_files(localdate):
    needfiles = False
    filedate = localdate.strftime("%Y-%m-%d")
    for reason in reasons:
        filename = f"{datadir}/contracts-{filedate}_{reason}.json"
        if not os.path.exists(filename):
            needfiles = True
    return needfiles


def in_production():
    if "GITHUB_RUN_ID" in os.environ or socket.gethostname() in [
        "mikelight",
        "racknerd-26f61a",
    ]:
        return True
    else:
        return False


def send_files():
    # Start by seeing what we have
    rawfilenames = list(glob(datadir + "*"))
    basefilenames = []
    for rawfilename in rawfilenames:
        basefilename = rawfilename.replace("\\", "/").replace(datadir, "")
        basefilenames.append(basefilename)

    bln_api = os.environ["BLN_API_TOKEN"]
    bln = Client(bln_api)
    project = bln.get_project_by_name("Federal contract cancellations")
    project_id = project["id"]

    files_to_send = []
    # Get all the files in the project.
    archived_files = {}
    for f in project["files"]:
        archived_files[f["name"]] = f["updatedAt"]

    for basefilename in basefilenames:
        if basefilename not in archived_files:
            files_to_send.append(basefilename)

    print(f"{len(archived_files):,} archived files found.")
    print(f"{len(files_to_send):,} files to send to Big Local News.")
    if len(files_to_send) == 0:
        pass
    else:
        project_id = project["id"]
        for file_to_send in tqdm(files_to_send):
            bln.upload_file(project_id, datadir + file_to_send)
    return


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

    # We should only run this if it's in production. But for now:
    if in_production:
        print("We're in production")
        send_files()
