#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import csv
import datetime
import json
import logging
import os
from decimal import *
from glob import glob

from bln.client import Client
from tqdm import tqdm

from utils import *

# In[ ]:


datadir = "data/"


# In[ ]:


reasons = {
    "E": "Terminate for default",
    "F": "Terminate for convenience",
    "K": "Close out",
    "N": "Legal contract cancellation",
    "X": "Terminate for cause",
}

reasons_simplified = {
    "E": "default",
    "F": "convenience",
    "K": "close_out",
    "N": "legal",
    "X": "for_cause",
}


# In[ ]:


from importlib import reload

reload(logging)
logging.basicConfig(
    format="%(asctime)s %(levelname)s:%(message)s",
    level=logging.DEBUG,
    datefmt="%I:%M:%S",
)
logger = logging.getLogger()
logger.setLevel("DEBUG")


# In[ ]:


archive_json(deleteafterarchiving=True)  # ZIP stuff up!


# In[ ]:


### Depending on the value of contract_type, one of these gets prefixed to many values. We want to merge these groups into one column.

prefixes = {
    "IDV": "content__IDV__",
    "AWARD": "content__award__",
    "OTHERTRANSACTIONAWARD": "content__OtherTransactionAward__contractDetail__",
    "OTHERTRANSACTIONIDV": "content__OtherTransactionIDV__contractDetail__",
}


# In[ ]:


roughshortwanted = """
title
contract_type
# link__rel
# link__type
link__href
modified
# content
# content__type
relevantContractDates__signedDate
relevantContractDates__effectiveDate
relevantContractDates__currentCompletionDate
relevantContractDates__ultimateCompletionDate
relevantContractDates__solicitationDate


dollarValues__obligatedAmount
dollarValues__baseAndAllOptionsValue
totalDollarValues__totalObligatedAmount
totalDollarValues__totalBaseAndAllOptionsValue
# placeOfPerformance__principalPlaceOfPerformance
awardID__awardContractID__agencyID
awardID__awardContractID__agencyID__name
awardID__awardContractID__PIID
awardID__awardContractID__modNumber
awardID__awardContractID__transactionNumber

purchaserInformation__contractingOfficeID
purchaserInformation__contractingOfficeID__name
placeOfPerformance__principalPlaceOfPerformance__stateCode
placeOfPerformance__principalPlaceOfPerformance__stateCode__name
placeOfPerformance__principalPlaceOfPerformance__countryCode
placeOfPerformance__principalPlaceOfPerformance__countryCode__name
placeOfPerformance__principalPlaceOfPerformance__locationCode
placeOfPerformance__placeOfPerformanceZIPCode
placeOfPerformance__placeOfPerformanceZIPCode__county
placeOfPerformance__placeOfPerformanceZIPCode__city
placeOfPerformance__placeOfPerformanceCongressionalDistrict
purchaserInformation__contractingOfficeAgencyID
purchaserInformation__contractingOfficeAgencyID__name
purchaserInformation__contractingOfficeAgencyID__departmentID
purchaserInformation__contractingOfficeAgencyID__departmentName
purchaserInformation__contractingOfficeID
purchaserInformation__contractingOfficeID__name

purchaserInformation__fundingRequestingAgencyID
purchaserInformation__fundingRequestingAgencyID__name
purchaserInformation__fundingRequestingAgencyID__departmentID
purchaserInformation__fundingRequestingAgencyID__departmentName

contractData__solicitationID
contractData__contractActionType
contractData__contractActionType__description
contractData__reasonForModification
contractData__reasonForModification__description
contractData__descriptionOfContractRequirement
competition__extentCompeted
competition__extentCompeted__description
# transactionInformation
transactionInformation__createdBy
transactionInformation__createdDate
transactionInformation__lastModifiedBy
transactionInformation__lastModifiedDate
transactionInformation__status
transactionInformation__status__description
transactionInformation__closedStatus
vendor__vendorHeader__vendorDoingAsBusinessName
# placeOfPerformance__principalPlaceOfPerformance
contractData__solicitationID
# vendor__vendorSiteDetails__vendorLocation
# vendor__vendorSiteDetails__entityIdentifiers
# vendor__vendorSiteDetails__entityIdentifiers__vendorUEIInformation
# vendor__vendorSiteDetails__entityIdentifiers__vendorUEIInformation__UEI
vendor__vendorSiteDetails__entityIdentifiers__cageCode
vendor__vendorSiteDetails__entityIdentifiers__vendorUEIInformation__UEILegalBusinessName
vendor__vendorSiteDetails__entityIdentifiers__vendorUEIInformation__ultimateParentUEI
vendor__vendorSiteDetails__entityIdentifiers__vendorUEIInformation__ultimateParentUEIName
vendor__vendorSiteDetails__vendorLocation__streetAddress
vendor__vendorSiteDetails__vendorLocation__city
vendor__vendorSiteDetails__vendorLocation__state
vendor__vendorSiteDetails__vendorLocation__state__name
vendor__vendorSiteDetails__vendorLocation__ZIPCode
vendor__vendorSiteDetails__vendorLocation__ZIPCode__city
vendor__vendorSiteDetails__vendorLocation__countryCode
vendor__vendorSiteDetails__vendorLocation__countryCode__name
vendor__vendorSiteDetails__vendorLocation__phoneNo
vendor__vendorSiteDetails__vendorLocation__faxNo
vendor__vendorSiteDetails__vendorLocation__congressionalDistrictCode
vendor__vendorSiteDetails__vendorLocation__entityDataSource

productOrServiceInformation__productOrServiceCode
productOrServiceInformation__productOrServiceCode__description
productOrServiceInformation__principalNAICSCode
productOrServiceInformation__principalNAICSCode__description

# vendor__vendorSiteDetails
# vendor__vendorSiteDetails__vendorSocioEconomicIndicators__isAlaskanNativeOwnedCorporationOrFirm
vendor__vendorSiteDetails__vendorSocioEconomicIndicators__isAmericanIndianOwned
vendor__vendorSiteDetails__vendorSocioEconomicIndicators__isIndianTribe
vendor__vendorSiteDetails__vendorSocioEconomicIndicators__isNativeHawaiianOwnedOrganizationOrFirm
vendor__vendorSiteDetails__vendorSocioEconomicIndicators__isTriballyOwnedFirm
vendor__vendorSiteDetails__vendorSocioEconomicIndicators__isSmallBusiness
vendor__vendorSiteDetails__vendorSocioEconomicIndicators__isVeteranOwned
vendor__vendorSiteDetails__vendorSocioEconomicIndicators__isServiceRelatedDisabledVeteranOwnedBusiness
vendor__vendorSiteDetails__vendorSocioEconomicIndicators__isWomenOwned
# vendor__vendorSiteDetails__vendorSocioEconomicIndicators__minorityOwned
vendor__vendorSiteDetails__vendorSocioEconomicIndicators__minorityOwned__isMinorityOwned
vendor__vendorSiteDetails__vendorSocioEconomicIndicators__minorityOwned__isSubContinentAsianAmericanOwnedBusiness
vendor__vendorSiteDetails__vendorSocioEconomicIndicators__minorityOwned__isAsianPacificAmericanOwnedBusiness
vendor__vendorSiteDetails__vendorSocioEconomicIndicators__minorityOwned__isBlackAmericanOwnedBusiness
vendor__vendorSiteDetails__vendorSocioEconomicIndicators__minorityOwned__isHispanicAmericanOwnedBusiness
vendor__vendorSiteDetails__vendorSocioEconomicIndicators__minorityOwned__isNativeAmericanOwnedBusiness
vendor__vendorSiteDetails__vendorSocioEconomicIndicators__minorityOwned__isOtherMinorityOwned
vendor__vendorSiteDetails__vendorSocioEconomicIndicators__isVerySmallBusiness
vendor__vendorSiteDetails__vendorSocioEconomicIndicators__isWomenOwnedSmallBusiness
vendor__vendorSiteDetails__vendorSocioEconomicIndicators__isEconomicallyDisadvantagedWomenOwnedSmallBusiness
vendor__vendorSiteDetails__vendorSocioEconomicIndicators__isJointVentureWomenOwnedSmallBusiness
vendor__vendorSiteDetails__vendorSocioEconomicIndicators__isJointVentureEconomicallyDisadvantagedWomenOwnedSmallBusiness
# vendor__vendorSiteDetails__vendorBusinessTypes
vendor__vendorSiteDetails__vendorBusinessTypes__isCommunityDevelopedCorporationOwnedFirm
vendor__vendorSiteDetails__vendorBusinessTypes__isLaborSurplusAreaFirm
# vendor__vendorSiteDetails__vendorBusinessTypes__federalGovernment
vendor__vendorSiteDetails__vendorBusinessTypes__federalGovernment__isFederalGovernment
vendor__vendorSiteDetails__vendorBusinessTypes__federalGovernment__isFederallyFundedResearchAndDevelopmentCorp
vendor__vendorSiteDetails__vendorBusinessTypes__federalGovernment__isFederalGovernmentAgency
vendor__vendorSiteDetails__vendorBusinessTypes__isStateGovernment
# vendor__vendorSiteDetails__vendorBusinessTypes__localGovernment
vendor__vendorSiteDetails__vendorBusinessTypes__localGovernment__isLocalGovernment
vendor__vendorSiteDetails__vendorBusinessTypes__localGovernment__isCityLocalGovernment
vendor__vendorSiteDetails__vendorBusinessTypes__localGovernment__isCountyLocalGovernment
vendor__vendorSiteDetails__vendorBusinessTypes__localGovernment__isInterMunicipalLocalGovernment
vendor__vendorSiteDetails__vendorBusinessTypes__localGovernment__isLocalGovernmentOwned
vendor__vendorSiteDetails__vendorBusinessTypes__localGovernment__isMunicipalityLocalGovernment
vendor__vendorSiteDetails__vendorBusinessTypes__localGovernment__isSchoolDistrictLocalGovernment
vendor__vendorSiteDetails__vendorBusinessTypes__localGovernment__isTownshipLocalGovernment
vendor__vendorSiteDetails__vendorBusinessTypes__isTribalGovernment
vendor__vendorSiteDetails__vendorBusinessTypes__isForeignGovernment
# vendor__vendorSiteDetails__vendorBusinessTypes__businessOrOrganizationType
vendor__vendorSiteDetails__vendorBusinessTypes__businessOrOrganizationType__isCorporateEntityNotTaxExempt
vendor__vendorSiteDetails__vendorBusinessTypes__businessOrOrganizationType__isCorporateEntityTaxExempt
vendor__vendorSiteDetails__vendorBusinessTypes__businessOrOrganizationType__isPartnershipOrLimitedLiabilityPartnership
vendor__vendorSiteDetails__vendorBusinessTypes__businessOrOrganizationType__isSolePropreitorship
vendor__vendorSiteDetails__vendorBusinessTypes__businessOrOrganizationType__isSmallAgriculturalCooperative
vendor__vendorSiteDetails__vendorBusinessTypes__businessOrOrganizationType__isInternationalOrganization
vendor__vendorSiteDetails__vendorBusinessTypes__businessOrOrganizationType__isUSGovernmentEntity
# vendor__vendorSiteDetails__vendorLineOfBusiness
vendor__vendorSiteDetails__vendorLineOfBusiness__isCommunityDevelopmentCorporation
vendor__vendorSiteDetails__vendorLineOfBusiness__isDomesticShelter
vendor__vendorSiteDetails__vendorLineOfBusiness__isEducationalInstitution
vendor__vendorSiteDetails__vendorLineOfBusiness__isFoundation
vendor__vendorSiteDetails__vendorLineOfBusiness__isHospital
vendor__vendorSiteDetails__vendorLineOfBusiness__isManufacturerOfGoods
vendor__vendorSiteDetails__vendorLineOfBusiness__isVeterinaryHospital
vendor__vendorSiteDetails__vendorLineOfBusiness__isHispanicServicingInstitution
# vendor__vendorSiteDetails__vendorRelationshipWithFederalGovernment
vendor__vendorSiteDetails__vendorRelationshipWithFederalGovernment__receivesContracts
vendor__vendorSiteDetails__vendorRelationshipWithFederalGovernment__receivesGrants
vendor__vendorSiteDetails__vendorRelationshipWithFederalGovernment__receivesContractsAndGrants
# vendor__vendorSiteDetails__typeOfGovernmentEntity
vendor__vendorSiteDetails__typeOfGovernmentEntity__isAirportAuthority
vendor__vendorSiteDetails__typeOfGovernmentEntity__isCouncilOfGovernments
vendor__vendorSiteDetails__typeOfGovernmentEntity__isHousingAuthoritiesPublicOrTribal
vendor__vendorSiteDetails__typeOfGovernmentEntity__isInterstateEntity
vendor__vendorSiteDetails__typeOfGovernmentEntity__isPlanningCommission
vendor__vendorSiteDetails__typeOfGovernmentEntity__isPortAuthority
vendor__vendorSiteDetails__typeOfGovernmentEntity__isTransitAuthority
# vendor__vendorSiteDetails__vendorOrganizationFactors
vendor__vendorSiteDetails__vendorOrganizationFactors__isSubchapterSCorporation
vendor__vendorSiteDetails__vendorOrganizationFactors__isLimitedLiabilityCorporation
vendor__vendorSiteDetails__vendorOrganizationFactors__isForeignOwnedAndLocated
# vendor__vendorSiteDetails__vendorOrganizationFactors__profitStructure
vendor__vendorSiteDetails__vendorOrganizationFactors__profitStructure__isForProfitOrganization
vendor__vendorSiteDetails__vendorOrganizationFactors__profitStructure__isNonprofitOrganization
vendor__vendorSiteDetails__vendorOrganizationFactors__profitStructure__isOtherNotForProfitOrganization
vendor__vendorSiteDetails__vendorOrganizationFactors__isShelteredWorkshop
# vendor__vendorSiteDetails__typeOfEducationalEntity
vendor__vendorSiteDetails__typeOfEducationalEntity__is1862LandGrantCollege
vendor__vendorSiteDetails__typeOfEducationalEntity__is1890LandGrantCollege
vendor__vendorSiteDetails__typeOfEducationalEntity__is1994LandGrantCollege
vendor__vendorSiteDetails__typeOfEducationalEntity__isHistoricallyBlackCollegeOrUniversity
vendor__vendorSiteDetails__typeOfEducationalEntity__isMinorityInstitution
vendor__vendorSiteDetails__typeOfEducationalEntity__isPrivateUniversityOrCollege
vendor__vendorSiteDetails__typeOfEducationalEntity__isSchoolOfForestry
vendor__vendorSiteDetails__typeOfEducationalEntity__isStateControlledInstitutionofHigherLearning
vendor__vendorSiteDetails__typeOfEducationalEntity__isTribalCollege
vendor__vendorSiteDetails__typeOfEducationalEntity__isVeterinaryCollege
vendor__vendorSiteDetails__typeOfEducationalEntity__isAlaskanNativeServicingInstitution
vendor__vendorSiteDetails__typeOfEducationalEntity__isNativeHawaiianServicingInstitution
# vendor__vendorSiteDetails__vendorCertifications
vendor__vendorSiteDetails__vendorCertifications__isDOTCertifiedDisadvantagedBusinessEnterprise
vendor__vendorSiteDetails__vendorCertifications__isSelfCertifiedSmallDisadvantagedBusiness
vendor__vendorSiteDetails__vendorCertifications__isSBACertifiedSmallDisadvantagedBusiness
vendor__vendorSiteDetails__vendorCertifications__isSBACertified8AProgramParticipant
vendor__vendorSiteDetails__vendorCertifications__isSelfCertifiedHUBZoneJointVenture
vendor__vendorSiteDetails__vendorCertifications__isSBACertifiedHUBZone
vendor__vendorSiteDetails__vendorCertifications__isSBACertified8AJointVenture

"""
shortwanted = []
for shortthing in roughshortwanted.splitlines():
    shorterthing = shortthing.split("#")[0].strip()
    if len(shorterthing) > 3:  # Drop commented-out rows, drop comments
        shortwanted.append(shorterthing)


# In[ ]:


def deeper_field_clean(text):
    ## These are different from prefixes in that they don't create distinct columns that need to be consolidated
    ## they're just junk text that, for our purposes, unnecessarily lengthens colu
    subprefixes = [
        "vendor__vendorSiteDetails__entityIdentifiers__vendorUEIInformation__",
        "vendor__vendorSiteDetails__typeOfEducationalEntity__",
        "vendor__vendorSiteDetails__vendorCertifications__",
        "vendor__vendorSiteDetails__vendorOrganizationFactors__",
        "vendor__vendorSiteDetails__typeOfGovernmentEntity__",
        "vendor__vendorSiteDetails__vendorLineOfBusiness__",
        "vendor__vendorSiteDetails__vendorBusinessTypes__businessOrOrganizationType__",
        "vendor__vendorSiteDetails__vendorBusinessTypes__localGovernment__",
        "vendor__vendorSiteDetails__vendorBusinessTypes__federalGovernment__",
        "vendor__vendorSiteDetails__vendorBusinessTypes__",
        "vendor__vendorSiteDetails__vendorSocioEconomicIndicators__minorityOwned__",
        "content__award__vendor__vendorHeader__",
        "placeOfPerformance__",
        # Deeper cuts below
        "vendor__vendorSiteDetails__vendorSocioEconomicIndicators__",
        "vendor__vendorSiteDetails__",
        "awardID__",
        "purchaserInformation__",
        "vendor__vendorHeader__",
    ]
    for subprefix in subprefixes:
        text = text.replace(subprefix, "")
    return text


# In[ ]:


def in_production():
    if "GITHUB_RUN_ID" in os.environ or socket.gethostname() in [
        # "mikelight",
        "racknerd-26f61a",
    ]:
        return True
    else:
        return False


# In[ ]:


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
    bln_files = {}
    for f in project["files"]:
        bln_files[f["name"]] = f["updatedAt"]

    for basefilename in basefilenames:
        if (
            basefilename not in bln_files
            or basefilename.endswith(".csv")
            or basefilename.endswith(".zip")
        ):
            files_to_send.append(basefilename)

    logger.debug(f"{len(bln_files):,} files found on Big Local News.")
    logger.debug(f"{len(files_to_send):,} files to send to Big Local News.")
    if len(files_to_send) == 0:
        pass
    else:
        project_id = project["id"]
        for file_to_send in tqdm(files_to_send):
            bln.upload_file(project_id, datadir + file_to_send)
    return


# In[ ]:


def send_dashboard_data():
    """Send limited-column data to Google Cloud Storage for dashboard

    Arguments:
        None
    Returns:
        None
    Uses:
        bln-gcs-key.json secret file
    """
    from google.cloud import storage
    from google.oauth2 import service_account

    bucket_name = "bln-data-public"
    targetfile = "terminated-fed-contracts/convenience--limited_cols.csv"
    localfile = "data/convenience--limited_cols.csv"
    service_account_file = "bln-gcs-key.json"

    credentials = service_account.Credentials.from_service_account_file(
        service_account_file
    )
    storage_client = storage.Client(credentials=credentials)
    bucket = storage_client.bucket(bucket_name)

    blob = bucket.blob(targetfile)
    blob.upload_from_filename(localfile)

    return


# In[ ]:


def get_zip_lookup():
    """Build a ZIP/ZCTA lookup table, if needed

    Arguments:
        None
    Returns:
        global dictionary named ziplookup
    Uses:
        zip-lookup.csv from mable-raw.csv via parse-zips.ipynb
    """
    if "ziplookup" in globals():
        pass  # ZIP lookup table already initialized
    else:
        logger.debug("ZIP lookup table being initialized")
        global ziplookup
        ziplookup = {}
        with open("zip-lookup.csv", "r", encoding="utf-8") as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                ziplookup[row["zip_code"]] = row
    return ()


# In[ ]:


def dedupe_by_contract_id(records):
    """Keep only the most recent record for each unique contract combination"""
    from collections import defaultdict

    grouped = defaultdict(list)

    for record in records:
        # Create the unique key from the three contract ID fields
        key = (
            record.get("awardContractID__agencyID"),
            record.get("awardContractID__PIID"),
            record.get("awardContractID__modNumber"),
        )

        # Parse the date for comparison
        record["_parsed_date"] = datetime.datetime.strptime(
            record["modified"], "%Y-%m-%d %H:%M:%S"
        )
        grouped[key].append(record)

    # Keep only the most recent record from each group
    deduped_records = []
    for key in grouped:
        records_group = grouped[key]
        if key[1] == None and key[2] == None:
            for line in records_group:
                # Clean up the temporary field
                del line["_parsed_date"]
                deduped_records.append(line)
        else:
            most_recent = max(records_group, key=lambda x: x["_parsed_date"])
            # Clean up the temporary field
            del most_recent["_parsed_date"]
            deduped_records.append(most_recent)

    return deduped_records


# In[ ]:


def add_county_details(row: dict):
    """Take a list returned from the API or read from a CSV, and append geographic details.

    Arguments:
        row, a dictionary
    Returns:
        row, still a dictionary
    """
    get_zip_lookup()  # Read in table ## why are we doing this every single row?
    if (
        "geo_fips" not in row or row["geo_fips"] == "Unknown"
    ):  # If we need to do a lookup
        if not row["placeOfPerformanceZIPCode"]:
            for item in ["geo_fips", "geo_county_name", "geo_zip_name"]:
                row[item] = "Unknown"
        else:
            rowzip = row["placeOfPerformanceZIPCode"][
                0:5
            ]  # Lose the extension for 9-digit ZIP codes
            if rowzip not in ziplookup:  # If we can't look up
                for item in ["geo_fips", "geo_county_name", "geo_zip_name"]:
                    row[item] = "Unknown"
            else:  # We need to look up, and we can look up
                row["geo_fips"] = ziplookup[rowzip]["zip_fips"]
                row["geo_county_name"] = ziplookup[rowzip]["zip_county_name"]
                row["geo_zip_name"] = ziplookup[rowzip]["zip_place_name"]
    return row


def county_from_zip(zip9):
    if zip9 is None:
        return "Unknown"
    zip5 = zip9[:5]
    if zip5 in ziplookup:
        loc_data = ziplookup[zip5]
        geo_county_name = loc_data["zip_county_name"]
        return geo_county_name[:-3]  # Truncating out the state code
    return "Unknown"


# In[ ]:


## Eric's categories -- I'll review them
VENDOR_ATTR_COLS = [
    "isAmericanIndianOwned",
    "isIndianTribe",
    "isNativeHawaiianOwnedOrganizationOrFirm",
    "isTriballyOwnedFirm",
    "isSmallBusiness",
    "isVeteranOwned",
    "isServiceRelatedDisabledVeteranOwnedBusiness",
    "isWomenOwned",
    "isMinorityOwned",
    "isSubContinentAsianAmericanOwnedBusiness",
    "isAsianPacificAmericanOwnedBusiness",
    "isBlackAmericanOwnedBusiness",
    "isHispanicAmericanOwnedBusiness",
    "isNativeAmericanOwnedBusiness",
    "isOtherMinorityOwned",
    "isVerySmallBusiness",
    "isWomenOwnedSmallBusiness",
    "isEconomicallyDisadvantagedWomenOwnedSmallBusiness",
    "isJointVentureWomenOwnedSmallBusiness",
    "isJointVentureEconomicallyDisadvantagedWomenOwnedSmallBusiness",
    "isCommunityDevelopedCorporationOwnedFirm",
    "isLaborSurplusAreaFirm",
    "isFederalGovernment",
    "isFederallyFundedResearchAndDevelopmentCorp",
    "isFederalGovernmentAgency",
    "isStateGovernment",
    "isLocalGovernment",
    "isCityLocalGovernment",
    "isCountyLocalGovernment",
    "isInterMunicipalLocalGovernment",
    "isLocalGovernmentOwned",
    "isMunicipalityLocalGovernment",
    "isSchoolDistrictLocalGovernment",
    "isTownshipLocalGovernment",
    "isTribalGovernment",
    "isForeignGovernment",
    "isCorporateEntityNotTaxExempt",
    "isCorporateEntityTaxExempt",
    "isPartnershipOrLimitedLiabilityPartnership",
    "isSolePropreitorship",
    "isSmallAgriculturalCooperative",
    "isInternationalOrganization",
    "isUSGovernmentEntity",
    "isCommunityDevelopmentCorporation",
    "isDomesticShelter",
    "isEducationalInstitution",
    "isFoundation",
    "isHospital",
    "isManufacturerOfGoods",
    "isVeterinaryHospital",
    "isHispanicServicingInstitution",
    "vendorRelationshipWithFederalGovernment__receivesContracts",
    "vendorRelationshipWithFederalGovernment__receivesGrants",
    "vendorRelationshipWithFederalGovernment__receivesContractsAndGrants",
    "isAirportAuthority",
    "isCouncilOfGovernments",
    "isHousingAuthoritiesPublicOrTribal",
    "isInterstateEntity",
    "isPlanningCommission",
    "isPortAuthority",
    "isTransitAuthority",
    "isSubchapterSCorporation",
    "isLimitedLiabilityCorporation",
    "isForeignOwnedAndLocated",
    "profitStructure__isForProfitOrganization",
    "profitStructure__isNonprofitOrganization",
    "profitStructure__isOtherNotForProfitOrganization",
    "isShelteredWorkshop",
    "is1862LandGrantCollege",
    "is1890LandGrantCollege",
    "is1994LandGrantCollege",
    "isHistoricallyBlackCollegeOrUniversity",
    "isMinorityInstitution",
    "isPrivateUniversityOrCollege",
    "isSchoolOfForestry",
    "isStateControlledInstitutionofHigherLearning",
    "isTribalCollege",
    "isVeterinaryCollege",
    "isAlaskanNativeServicingInstitution",
    "isNativeHawaiianServicingInstitution",
    "isDOTCertifiedDisadvantagedBusinessEnterprise",
    "isSelfCertifiedSmallDisadvantagedBusiness",
    "isSBACertifiedSmallDisadvantagedBusiness",
    "isSBACertified8AProgramParticipant",
    "isSelfCertifiedHUBZoneJointVenture",
    "isSBACertifiedHUBZone",
    "isSBACertified8AJointVenture",
]


def roll_up_flags(row, flag_ls):
    compiled_flags = []
    for flag in flag_ls:
        if row[flag] == "true":
            compiled_flags.append(flag)
    return compiled_flags


# In[ ]:


# On DATE, VENDOR lost a AMOUNT-dollar contract with AGENCY, DEPARTMENT for DESCRIPTION

HIGHLIGHTED_COLUMNS_DICT = {
    "contract_id": None,
    "solicitation_id": None,
    "modification_number": None,
    "date_cancelled": None,
    "vendor": None,
    "amount_cancelled": None,
    "admin_agency": None,
    "contracting_agency_department": None,
    "funding_agency": None,
    "funding_agency_department": None,
    "product_or_service_description": None,
    "contract_requirement": None,
    "performance_country": None,
    "performance_state": None,
    "performance_county": None,
    "performance_zip9": None,
    "vendor_country": None,
    "vendor_state": None,
    "vendor_county": None,
    "vendor_city": None,
    "vendor_zip9": None,
    "vendor_address": None,
    "vendor_phone": None,
    "vendor_attributes": None,
    "reason_code": None,
    "reason": None,
    "filename": None,
    "filedate": None,
    "last_updated": None,
    "fpds_url": None,
}

# HIGHLIGHTED_COLUMNS_DICT.keys()


# In[ ]:


def invert(val):
    return float(val) * -1


# In[ ]:


# Now, composite the JSONs into CSVs.

jsonlist = list_archived_json()

extraheaders = []
for item in shortwanted:
    extraheaders.append(deeper_field_clean(item))
for reason in reasons:
    locallist = []
    with zipfile.ZipFile(archivefile, "r") as myzip:
        localfiles = [item for item in jsonlist if item.endswith(f"{reason}.json")]
        for basefilename in tqdm(localfiles, desc=f"code {reason}"):
            with myzip.open(basefilename) as myfile:
                rawjson = json.loads(myfile.read())
            filedate = basefilename.split("contracts-")[-1].split("_")[0]
            for entry in rawjson:
                localdict = HIGHLIGHTED_COLUMNS_DICT.copy()
                localdict["filedate"] = filedate
                localdict["reason_code"] = reason
                localdict["reason"] = f"{reason}: {reasons[reason]}"
                localdict["filename"] = basefilename

                prefix = prefixes[entry["contract_type"]]
                for item in extraheaders:
                    localdict[item] = None
                for field in entry:
                    fieldshort = field.replace(prefix, "")
                    if fieldshort in shortwanted:
                        localdict[deeper_field_clean(fieldshort)] = entry[field].strip()

                localdict = add_county_details(localdict)

                localdict["vendor_attributes"] = roll_up_flags(
                    localdict, VENDOR_ATTR_COLS
                )
                #            localdict["is_nonprofit"] = len(roll_up_flags(localdict,NON_PROFIT_COLS))>0

                # Now we need to fill in some blanks at the beginning

                localdict["contract_id"] = localdict["awardContractID__PIID"]
                localdict["solicitation_id"] = localdict["contractData__solicitationID"]

                localdict["modification_number"] = localdict[
                    "awardContractID__modNumber"
                ]
                localdict["performance_country"] = localdict[
                    "principalPlaceOfPerformance__countryCode__name"
                ]
                localdict["performance_state"] = localdict[
                    "principalPlaceOfPerformance__stateCode"
                ]

                # We might want to replace this with localdict["geo_county_name"] at some point
                # but we should confirm why we're overriding the underlying data
                localdict["performance_county"] = localdict[
                    "placeOfPerformanceZIPCode__county"
                ]
                localdict["performance_zip9"] = localdict["placeOfPerformanceZIPCode"]

                localdict["vendor_country"] = localdict[
                    "vendorLocation__countryCode__name"
                ]
                localdict["vendor_state"] = localdict["vendorLocation__state"]
                localdict["vendor_zip9"] = localdict["vendorLocation__ZIPCode"]
                localdict["vendor_county"] = county_from_zip(
                    localdict["vendorLocation__ZIPCode"]
                )
                localdict["vendor_city"] = localdict["vendorLocation__city"]
                localdict["vendor_address"] = localdict["vendorLocation__streetAddress"]
                localdict["vendor_phone"] = localdict["vendorLocation__phoneNo"]
                localdict["date_cancelled"] = localdict[
                    "relevantContractDates__signedDate"
                ]
                localdict["amount_cancelled"] = invert(
                    localdict["dollarValues__obligatedAmount"]
                )  # Invert
                localdict["vendor"] = localdict["UEILegalBusinessName"]
                localdict["admin_agency"] = localdict["awardContractID__agencyID__name"]
                localdict["contracting_agency_department"] = localdict[
                    "contractingOfficeAgencyID__departmentName"
                ]

                localdict["funding_agency"] = localdict[
                    "fundingRequestingAgencyID__name"
                ]
                localdict["funding_agency_department"] = localdict[
                    "fundingRequestingAgencyID__departmentName"
                ]

                localdict["fpds_url"] = localdict["link__href"]
                localdict["contract_requirement"] = localdict[
                    "contractData__descriptionOfContractRequirement"
                ]
                localdict["product_or_service_description"] = localdict[
                    "productOrServiceInformation__productOrServiceCode__description"
                ]
                localdict["last_updated"] = localdict["modified"]
                locallist.append(localdict)

    # Now we need to deduplicate by contract ID
    logger.debug(f"Before deduping: {len(locallist):,} records")
    locallist = dedupe_by_contract_id(locallist)
    logger.debug(f"After deduping: {len(locallist):,} records")

    # Let's get some basic sorting in here
    locallist = sorted(locallist, key=lambda x: (x["filedate"]), reverse=True)

    filepath = f"{datadir}collected_{reason}.csv"
    reason_str = reasons_simplified[reason]
    filepath = f"{datadir}{reason_str}.csv"
    logger.debug(f"Writing {filepath}")
    if locallist:  # Make sure we have data, then write the data file
        with open(filepath, "w", encoding="utf-8", newline="") as outfile:
            writer = csv.writer(outfile)
            writer.writerow(list(locallist[0].keys()))  # Use first record for headers
            for line in locallist:
                writer.writerow(list(line.values()))
            logger.debug(f"Wrote {filepath}")

    if reason == "F":  # Process limited fields/columnss/keys
        limitedfile = f"{datadir}{reason_str}--limited_cols.csv"
        logger.debug(f"Writing to {limitedfile}")

        # Limit each dict in a list to specific keys/fields/columns
        limited_locallist = []
        limited_cols = list(HIGHLIGHTED_COLUMNS_DICT.keys()) + ["vendor_attributes"]

        for row in locallist:
            limited_locallist.append({k: row[k] for k in limited_cols if k in row})
        with open(limitedfile, "w", encoding="utf-8", newline="") as outfile:
            if locallist:
                writer = csv.writer(outfile)
                writer.writerow(list(limited_locallist[0].keys()))
                for row in limited_locallist:
                    writer.writerow(list(row.values()))
        logger.debug(f"Wrote {limitedfile}")

    locallist = None


# In[ ]:


# We should only run this if it's in production.
if in_production:
    logger.debug("We're in production")
    send_files()
    send_dashboard_data()


# In[ ]:


# In[ ]:
