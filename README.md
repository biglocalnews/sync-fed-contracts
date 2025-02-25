# About this
This is a project to extract important data from the U.S. federal government's contract records.

The Trump administration in 2025 began cancelling contracts en masse. This project extracts relevant data.

## How to use

You may simply want to get the data this generated, which will be available through https://www.biglocalnews.org under a project called [Federal contract cancellations](https://biglocalnews.org/#/project/UHJvamVjdDpjZjgyZTRkYS0xNTQ4LTQ4NGUtOTk2MC1mNzk4ZTg4NmY5ODM=).

This is a pretty typical Python program. To install it:

    git clone https://github.com/biglocalnews/sync-fed-contracts.git
    cd sync-fed-contracts
	pip install -r requirements.txt

If you wish to run it and collect data beginning from the second Trump administration on Jan. 20, 2025, simply run:

	python sync-fed-contracts.py

## Reference materials
The [Federal Payment Procurement System](https://www.fpds.gov/fpdsng_cms/index.php/en/) has some documentation and interfaces on its main web site.

In the initial release of this program, we are scraping modification codes with reason codes of E, F, K, N, and X. 

You can see what that means in the [official data dictionary](https://www.fpds.gov/downloads/Version_1.5_specs/FPDS_DataDictionary_V1.5.pdf).

Specific steps on a prescibed procedure are required when the government terminates a contract for convenience. For information on that process, and to evaluate whether it's being followed, see [the Defense Acquisition University's guide to contract termination](https://www.dau.edu/acquipedia-article/contract-termination).

## Credits

This really started when Ethan Corey ([@ethanscorey](https://github.com/ethanscorey)) offered up a magical one-liner to retrieve some of the data. In a Slack, he posted a discussion and `uvx fpds parse "LAST_MOD_DATE=[2025/01/20, 2025/02/14]" "REASON_FOR_MODIFICATION=F"`. This code has grown *a bit* since then. Ethan went on to identify more reasons for modification and draft code that would retrieve them.

Cheryl Phillips ([@cephillips](https://github.com/cephillips)) decided the data should have a home at Big Local News. Sarah Cohen ([@sarahcnyt](https://github.com/sarahcnyt)), also with Big Local News, offered helpful guidance and resources  to understand the data. Anything in this project that is nonsensical is likely the fault of Mike Stucka ([@stucka](https://github.com/stucka)), who is working with [Big Local News](https://www.biglocalnews.org) and its repositories [@biglocalnews](https://github.com/biglocalnews) here. 

Working with MinnPost to track some related goings-ons, Michael Nolan ([@m-nolan](https://github.com/m-nolan)) built [Doge Scrape](https://github.com/m-nolan/doge-scrape) to track federal government claims of savings; some of that data ties directly back to FPDS.
