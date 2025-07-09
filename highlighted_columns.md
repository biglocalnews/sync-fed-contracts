# Highlighted columns

Our CSV files include several columns that are either renamed fields in the original JSON data or have been derived from them. The dataset available through the streamlit application is limited to these columns. This document serves as a guide to those fields.

Unless otherwise noted, quoted definitions are from the [FPDS Data Dictionary](https://www.fpds.gov/downloads/Version_1.5_specs/FPDS_DataDictionary_V1.5.pdf).

## contract_id

1A Procurement Instrument Identifier (PIID): "The unique identifier for each contract, agreement or order."

The combination of contract_id, modification_number, and agency_id uniquely identifies a cancellation when those fields are not empty.

Searchable in USASpending.gov as "Award ID." Also known as "awardContractID\_\_PIID."

## modification_number

1B Modification Number: "An identifier issued by an agency that uniquely identifies one modification for
one contract, agreement, order, etc."

Multiple updates to the records of the same cancellation sometimes appear in the underlying data, our compiled csvs are deduplicated to only include the most recent record for each. Corresponds to transaction records on a particular award in USASpending.gov. The combination of contract_id, modification_number, and agency_id uniquely identifies a cancellation.

Same as "Modification Number" in USASpending.gov. Also known as "awardContractID\_\_modNumber."

## performance_zip9, performance_county, performance_state, performance_country

For Services: The predominant place of performance at the time of award. Predominance is based on funding.

Subfields 9C Principal Place of Performance Code: "If the place of performance is located in the U.S. in an area that has no ZIP Plus 4 code (e.g., a national park, a remote location, etc.), use the closest location that does have a ZIP Plus 4. NOTE: Not all procurements require documentation of the place of performance in the file."

Also known as "principalPlaceOfPerformance." The actual specification in the data dictionary is quite long and addresses how to handle cases where the performance location is ambiguous.

## vendor_address, vendor_zip9, vendor_state, vendor_country,

13JJ Entity Address Line 1: "The address of the entity supplying the product or service as it appears in SAM at the time of the award based on the Unique Entity Identifier provided."

13PP Entity Zip Code, 13MM Entity Address City, 13NN Entity Address State, 13QQ Entity Country Code

Also known as "vendorLocation."

## vendor_county

This field is not supplied in the oiginal data. We calculated this by truncating _vendor_zip9_ (above) to a 5-digit zipcode. We then looked that up in a Big Local News crosswalk derived [from other federal data](https://github.com/biglocalnews/zips-to-counties/).

## vendor_phone

13RR Entity Phone Number: "The phone number of the entity."

Also known as "vendor_phoneNo."

## date_cancelled

2A Date Signed: "The date that a mutually binding agreement was reached. The date signed by the Contracting Officer or the Entity, whichever is later."

We confirmed with Federal Service Desk that this field represents the date of cancellation.

Corresponds to "Action Date" in USASpending.gov.Also known as "relevantContractDates\_\_signedDate".

## amount_cancelled

Derived from 3C Action Obligation in FPDS: "The amount that is obligated or de-obligated by this transaction."

Deobligations are represented in the original data as negative numbers. We've inverted them (multiplied by -1) so that amount_cancelled is positive if money is deobligated. Corresponds to the amount "saved" by cancelling the contract.

3C Action Obligation is also known as "dollarValues\_\_obligatedAmount," and corresponds to the "Amount" associated with a transaction in USASpending.gov.

Values may be strange. Our understanding (which the Federal Service Desk confirmed) is that some of the zero-dollar terminations legitimately saved $0 – there was nothing left to de-obligate at the time of termination. In others, the financial adjustment related to the termination is reported in a separate modification, so the latest cancellation entry won't show any monetary change.

The Federal Service Desk confirmed our understanding that some contract cancellations can cost money because things like settlement costs and allowable expenses exceded what would have been paid if the contrract had simply ben fulfilled thugh its obligations. And yet other cost adjustments may be hiding in other modifications.

## vendor

13GG Legal Business Name: "The name of the entity supplying the product or service as it appears in SAM at the time of the award based on the Unique Entity Identifier provided."

Also known as "UEILegalBusinessName."

## agency

1F Agency Code: "Identifier used to link agency in FPDS to award information."

The agency that owns the _contract_id_, responsible for issuing the contract or award. Also known as "awardContractID**agencyID**name." Corresponds to "Agency" in USASpending.gov.

## department

Derived from 4A Contracting Agency Code: "The code for the agency of the contracting office that executed or is otherwise responsible for the transaction."

The department overseeing the agency whose office is responsible for the modification.

Also known as "contractingOfficeAgencyID\_\_departmentName."

## contract_requirement

6M Description of Requirement: "Enter a brief, summary level, plain English, description of the contract, award, or modification"

Appears to sometimes describe the contract or award, and other times the actual termination. Also known as "contractData\_\_descriptionOfContractRequirement."

## product_or_service_description

8C Product Service Code Description: "A description of the product or service designated by the product service code."

Also known as "productOrServiceInformation**productOrServiceCode**description."

## reason_code, reason

12C Reason for Modification: "The type of modification to an award or IDV performed by this transaction."

| Code | Short Description                               |
| ---- | ----------------------------------------------- |
| E    | Terminate for default                           |
| F    | Terminate for Convenience (complete or partial) |
| K    | Close Out                                       |
| N    | Legal Contract Cancellation                     |
| X    | Terminate for Cause                             |

## last_updated

2F Date/Time Stamp Accepted: "The date and time the transaction was last validated and accepted by FPDS."

Also known as "modified."

## vendor_attributes

13 Entity Business Types: Each business type attribute has its own definition, we recommend looking at the data dictionary for details.

## filedate

The Big Local News script gets a dataset of contract terminations daily in XML and saves them as JSON files.

This is the day that the file this cancellation appears in was written.

## filename

The name of the JSON file inside Big Local News' ZIPped archive that this modification appears in. The date in the filename matches the filedate.

## fpds_url

A link to the contract ID searched on fpds.gov.
