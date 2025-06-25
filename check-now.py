import os

import papermill

if os.path.exists("/usr/bin/python3"):
    mypython = "/usr/bin/python3"
else:
    mypython = "python"

os.system(f"{mypython} sync-fed-contracts.py")

try:
    papermill.execute_notebook(
        "extract-to-csvs.ipynb",
        "ignore-extract-to-csvs.ipynb",
        log_output=True,
        log_level="debug",
    )
except:
    print("Failure with extract!")

try:
    os.system(f"{mypython} filter_for_dashboard.py")

except:
    print("Failure with filter!")
