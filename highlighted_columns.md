# Highlighted columns
Our CSV files include several columns that are either renamed fields in the original JSON data or have been derived from them. The dataset available through the streamlit application is limited to these columns. This document serves as a guide to those fields.

## Renamed from FPDS
Unless otherwise noted, quotes are from the [FPDS Data Dictionary](https://www.fpds.gov/downloads/Version_1.5_specs/FPDS_DataDictionary_V1.5.pdf)


### contract_id
"The unique identifier for each contract, agreement or order"

Searchable in USASpending.gov as "Award ID." Corresponds to "awardContractID__PIID" or "1A Procurement Instrument Identifier (PIID)" in FPDS. The combination of contract_id and modification_number uniquely identifies a cancellation.

### modification_number
"An identifier issued by an agency that uniquely identifies one modification for
one contract, agreement, order, etc."

Corresponds to transaction records on a particular award in USASpending.gov. Corresponds to "awardContractID__modNumber" or "1B Modification Number" in FPDS. The combination of contract_id and modification_number uniquely identifies a cancellation. Multiple updates to the records of the same cancellation sometimes appear in the underlying data, our compiled csvs are deduplicated to only include the most recent record for each.

[[ROSIE NOTE: This is different from Sara's hunch that we also needed Agency ID. But it appears PIIDs are unique government-wide, not just within agencies (["each PIID used to identify a solicitation or contract action is unique Governmentwide"](https://www.acquisition.gov/far/subpart-4.16)) This checks out: when we remove agency_id from the dedupe it's functionally equivalent.]]

### performance_country, performance_state, performance_county, performance_zip9
"For Services: The predominant place of performance at the time of award. Predominance is based on funding."

"If the place of performance is located in the U.S. in an area that has no ZIP Plus 4 code (e.g., a national park, a remote location, etc.), use the closest location that does have a ZIP Plus 4. NOTE: Not all procurements require documentation of the place of performance in the file."

Correspond to the records under "principalPlaceOfPerformance" or "Principal Place of Performance Code" in FPDS. The actual specification for these record in the data dictionary is quite long and addresses how to handle cases where the performance location is ambiguous.

### vendor_country, vendor_state, vendor_zip9, vendor_address
"The address of the entity supplying the product or service as it appears in SAM at
the time of the award based on the Unique Entity Identifier provided."

Correspond to records under "vendorLocation" or "Entity Address", "Entity Country Code" in FPDS.

### vendor_phone
"The phone number of the entity."

Corresponds to "vendor_phoneNo" or "13RR Entity Phone Number" in FPDS.

### date_cancelled
"The date that a mutually binding agreement was reached. The date signed by the
Contracting Officer or the Entity, whichever is later."

Corresponds to "relevantContractDates__signedDate" or "2A Date Signed" in FPDS. This date seems corresponds to "Action Date" in USASpending.gov, and seems to apply to the day the *cancellation itself* was signed.

### vendor
"The name of the entity supplying the product or service as it appears in SAM at
the time of the award based on the Unique Entity Identifier provided."

Corresponds to "UEILegalBusinessName" or "13GG Legal Business Name" in FPDS.

### agency
The agency that owns the *contract_id*, responsible for issuing the contract or award.

Corresponds to "awardContractID__agencyID__name" or the agency name linked to "1F Agency Code" in FPDS. Also "Agency Name" in the [FPDS API](https://www.fpds.gov/wiki/index.php/Atom_Feed_Usage).

[[ROSIE NOTE: There are several different agency fields -- I think they generally line up but I'm not sure which one to use/where the actual documentation about this is]]

### department
The department containing the agency that operates the office that awarded the contract.

Corresponds to "contractingOfficeAgencyID__departmentName" or the department name linked to the agency indicated in "4A Contracting Agency Code" in FPDS. Also "Department Name" in the [FPDS API](https://www.fpds.gov/wiki/index.php/Atom_Feed_Usage).

### fpds_url
A link to the contract ID searched on fpds.gov. ("link__href")

[[ROSIE NOTE: This also is neither in the data dict or that atom feed site. I guess it comes from the python wrapepr we're using?]]

### contract_requirement
"Enter a brief, summary level, plain English, description of the contract, award, or
modification"

Corresponds to "contractData__descriptionOfContractRequirement" or "6M Description of Requirement" in FPDS.

### general_service_description
"A description of the product or service designated by the product service code."

Corresponds to "productOrServiceInformation__productOrServiceCode__description" or "8C Product Service Code Description" in FPDS.

### reason_code, reason
"The type of modification to an award or IDV performed by this transaction."

| Code | Short Description                                                                 |
|------|------------------------------------------------------------------------------------|
| E    | Terminate for default                                                                     |
| F    | Terminate for Convenience (complete or partial)                                   |
| K    | Close Out                                                                         |
| N    | Legal Contract Cancellation                                                       |
| X    | Terminate for Cause                                                               |

Corresponds to "12C Reason for Modification" in FPDS

### last_updated
"The date and time the transaction was last validated and accepted by FPDS."

Corresponds to "modified" or "2F Date/Time Stamp Accepted" in FPDS.

## Original Fields
### vendor_county
We calculated this by truncating *vendor_zip9* to a 5-digit zipcode, and looking it up in a Census crosswalk.

### amount_cancelled
Derived from "3C Action Obligation" in FPDS: "The amount that is obligated or de-obligated by this transaction."

Deobligations are represented in the original data as negative numbers. We've inverted them so the amount cancelled is positive if money is deobligated. Corresponds to the amount "saved" by cancelling the contract.

### filedate

### filename

### dei_flags


### has_dei_flags

### is_nonprofit
