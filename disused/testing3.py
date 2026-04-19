from fpds import fpdsRequest

import asyncio

requestdate = "2026/03/15"
reason = "F"

"""
async def do_stuff(requestdate, reason):
    params_kwargs = {
        "LAST_MOD_DATE": f"[{requestdate}, {requestdate}]",
        "REASON_FOR_MODIFICATION": f"{reason}",
        }

    # records = await asyncio.run(request.data())
    gen = request.iter_data()

    # evaluating generator entries
    records = []
    for entry in gen:
        records.append(entry)
    print(records[0])
    return records


if __name__ == "__main__":
    records =  do_stuff(requestdate, reason)
    print(records)

"""
"""
request = fpdsRequest(**params_kwargs)


records = asyncio.run(request.data())
print(records)

"""


"""
request = fpdsRequest(
    LAST_MOD_DATE=f"[{requestdate}, {requestdate}]",
    REASON_FOR_MODIFICATION=f"{reason}",
        )
"""
"""gen = request.iter_data()

# evaluating generator entries
records = []
for entry in gen:
    records.append(entry)
print(records[0])
"""


def do_stuff():
    params_kwargs = {
        "LAST_MOD_DATE": "[2026/03/15, 2026/03/15]",
        "REASON_FOR_MODIFICATION": '"F"',
        }
        
    print(f"Params: {params_kwargs}")
    request = fpdsRequest(**params_kwargs, cli_run=False)
    records = asyncio.run(request.data())
    return records

if __name__ == "__main__":
    records = do_stuff()
    print(records[0])
