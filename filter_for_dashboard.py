"""Filter most recent entries in a CSV file.

   Given a CSV file with multiple entries for the same contract,
   generates a new CSV file that contains only the most recent entry
   for each contract (ie deduplicates the data).

   Along the way, the data is subsetted and modified for downstream
   use in Streamlit.

USAGE:
    python filter_most_recent.py <target_file>

    # for example
    python filter_most_recent.py dashboard/collected_F.csv

    # ...produces...
    dashboard/collected_F.filtered.csv

"""
import csv
import sys
from datetime import datetime
from operator import itemgetter
from pathlib import Path

TARGET_FIELDS = [
    'state', # performance location
    'county', # performance location
    'agency',
    'principalPlaceOfPerformance__stateCode',
    'principalPlaceOfPerformance__countryCode__name',
    'placeOfPerformanceZIPCode',
    'placeOfPerformanceZIPCode__county',
    'placeOfPerformanceZIPCode__city',
    'filedate',
    'business',
    'vendorLocation__streetAddress',
    'vendorLocation__city',
    'vendorLocation__state',
    'vendorLocation__ZIPCode_5',
    'vendorLocation__ZIPCode_9',
    'vendorLocation__countryCode__name',
    'vendorLocation__phoneNo',
    'amount',
    'general_service_description',
    'contract_requirement', # More detailed description of the contract
    'awardContractID__agencyID',
    'awardContractID__PIID',
    'awardContractID__modNumber',
    'modified',
    'title',
    'link_href',
    'contractingOfficeAgencyID__departmentID',
    'contractingOfficeAgencyID__departmentName',
    'contractingOfficeAgencyID__name',
    'contractData__reasonForModification__description',
]

FIRST_SCRAPE_DAY = datetime(2025, 1, 20) # There's older stuff in the data, but we only want to summarize entries from this date onward.

def filter_file(target_file):
    """Filter the most recent entries in a CSV file based on the 'date' column.

    # Unique identifiers:
    awardContractID__agencyID
    awardContractID__PIID
    awardContractID__modNumber

    modified - sort by modified column date and only keep the most recent
    """
    print(f"Grouping records from file: {target_file}")
    grouped_rows = group_rows(target_file)
    print(f"Extracting unique entries from {len(grouped_rows)} groups.")
    most_recent_only = filter_groups(grouped_rows)
    write_csv(most_recent_only, target_file)


def group_rows(target_file):
    """Group rows by unique identifiers."""
    grouped = {}
    with open(target_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            key = (
                row['awardContractID__agencyID'],
                row['awardContractID__PIID'],
                row['awardContractID__modNumber']
            )
            # Add date obj for downstream sorting
            row['modified_date'] = datetime.strptime(row['modified'], "%Y-%m-%d %H:%M:%S")
            row["vendorLocation__ZIPCode_9"] = row['vendorLocation__ZIPCode'] if row['vendorLocation__ZIPCode'] else None
            row['vendorLocation__ZIPCode_5'] = row['vendorLocation__ZIPCode'][:5] if row['vendorLocation__ZIPCode'] else None
            if row['modified_date'] < FIRST_SCRAPE_DAY:
                continue  # skip this row 
            else:
                # Invert the "change" amount for more sensible graphing downstream
                change = float(row.pop('change', 0))
                row['amount'] = change * -1
                grouped.setdefault(key, []).append(row)
    return grouped

def filter_groups(grouped_rows):
    """Filter groups to keep only the most recent entry based on the 'modified' ."""
    data = []
    for key, rows in grouped_rows.items():
        # Sort by 'modified' date in descending order
        rows.sort(key=itemgetter('modified_date'), reverse=True)
        # Keep the most recent entry
        to_keep = rows[0]
        to_keep.pop('modified_date', None)
        data.append(to_keep)
    return data


def write_csv(data, target_file):
    """Write the filtered data to a new CSV file."""
    outfile = Path(target_file).with_suffix('.filtered.csv')
    fieldnames = TARGET_FIELDS or data[0].keys()
    with open(outfile, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(data)
    print(f"Wrote {len(data)} unique entries to file: {outfile}")


if __name__ == "__main__":
    try:
        target_file = sys.argv[1]
    except IndexError:
        msg = "Usage: python filter_most_recent.py <target_file>"
        sys.exit(msg)
    filter_file(target_file)
