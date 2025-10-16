from bln import Client
import os
import logging

logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=logging.DEBUG, datefmt='%I:%M:%S')
logger = logging.getLogger()
BLN_API_KEY = os.environ["BLN_API_TOKEN"]
bln = Client(BLN_API_KEY)
project = bln.get_project_by_name("Federal contract cancellations")





from bln import Client
import logging
import os


datadir = "data/"


logging.basicConfig(
    format="%(asctime)s %(levelname)s:%(message)s",
    level=logging.DEBUG,
    datefmt="%H:%M:%S",
)
logger = logging.getLogger()

logger.debug("Fetching JSON archive.")
bln_api = os.environ["BLN_API_TOKEN"]
bln = Client(bln_api)
project = bln.get_project_by_name("Federal contract cancellations")
project_id = project["id"]
bln.download_file(project_id, "archived_json.zip", output_dir=datadir)



from bln import Client
import logging
import os


datadir = "data/"

logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=logging.DEBUG, datefmt='%I:%M:%S')
logger = logging.getLogger()


logger.debug("Fetching JSON archive.")
logger.debug("Getting token from environment")
print("Getting token")
bln_api = os.environ["BLN_API_TOKEN"]
bln = Client(bln_api)
logger.debug("Client initialized")
logger.debug("Getting project by name")
print("Getting project by name")
project = bln.get_project_by_name("Federal contract cancellations")
print("Extracting project ID")
logger.debug("Extracting project ID")
project_id = project["id"]
print(f"Trying to download file from project_id {project_id} to datadir {datadir}")
logger.debug(f"Trying to download file from project_id {project_id} to datadir {datadir}")
bln.download_file(project_id, "archived_json.zip", output_dir=datadir)