#!/usr/bin/env python
# coding: utf-8

from fpds import fpdsRequest

import asyncio
import datetime
from itertools import chain
import json


yesterday = (datetime.datetime.now() - datetime.timedelta(hours=24)).strftime(
    "%Y/%m/%d"
)
today = datetime.datetime.now().strftime("%Y/%m/%d")
timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")

reasons = ["E", "F", "K", "N", "X"]


async def main():
    requests = {}
    async with asyncio.TaskGroup() as tg:
        for reason in reasons:
            request = fpdsRequest(
                LAST_MOD_DATE=f"[{yesterday}, {today}]",
                REASON_FOR_MODIFICATION=f"{reason}",
            )
            requests[reason] = tg.create_task(request.data())
    return {
        reason: list(chain.from_iterable(request.result()))
        for (reason, request) in requests.items()
    }


if __name__ == "__main__":
    data = asyncio.run(main())
    with open(f"output-{timestamp}.json", "w", encoding="utf-8") as outfile:
        outfile.write(json.dumps(data, indent=4 * " "))


ignore = """
Ethan Corey's starting point:
uvx fpds parse "LAST_MOD_DATE=[2025/01/20, 2025/02/14]" "REASON_FOR_MODIFICATION=F"

From 
@Sarah Cohen
, this is what's required to happen when the government terminates a contract for convenience. I don't know how well this requirement is being followed. https://www.dau.edu/acquipedia-article/contract-termination

Ethan Corey folo:
My suggestion would be to include all types of contract terminations (see list of modification types on p. 144 here: https://www.fpds.gov/downloads/Version_1.5_specs/FPDS_DataDictionary_V1.5.pdf), which I believe would include E, F, K, N, and X.

The fpds_status field in the DOGE receipts JSON includes a number of other modification types (e.g., OTHER ADMINISTRATIVE ACTION and EXERCISE_AN_OPTION), but when I looked at the linked FPDS pages for those entries, they either a) showed a different reason for modification (e.g., https://www.fpds.gov/ezsearch/jsp/viewLinkController.jsp?agencyID=1344&PIID=1333BJ23F00220001&modNumber=P25007&idvAgencyID=&idvPIID=47QRAA18D006U&contractType=AWARD) or b) linked to a modification that occurred before Jan. 20 (e.g., https://www.fpds.gov/ezsearch/jsp/viewLinkController.jsp?agencyID=12C2&PIID=12318723C0016&modNumber=P00001&idvAgencyID=&idvPIID=&contractType=AWARD). My hunch is that DOGE used the most recent available modification in FPDS if the cancellation hasn't posted to FPDS yet, though without documentation from DOGE, that's just a guess.
"""
