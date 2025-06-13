"""
Things to (possibly) update or add:
- Flesh out the footer (see bottom of this script)
- PullQuote style numbers
- Add clickable links to the table that go to contract pages
- Loading from remote CSV file(s)
- Optimize data loading with st.cache_data, where needed
- Methodology page
- Data dictionary page

"""
from pathlib import Path

import streamlit as st
import altair as alt
import pandas

def country_performance_select(df):
    """Display a selectbox for country performance."""
    country_options = sorted(df['principalPlaceOfPerformance__countryCode__name'].dropna().unique().tolist())
    country_options.sort(key=lambda x: (x != "UNITED STATES", x))
    selected_country = st.sidebar.selectbox(
        "Filter by Performance Country:",
        options=["All"] + country_options
    )
    return selected_country

def state_performance_select(df):
    """Display a selectbox for state performance."""
    state_options = sorted(df['state'].dropna().unique().tolist())
    selected_state = st.sidebar.selectbox(
        "Filter by Performance State:",
        options=["All"] + state_options
    )
    return selected_state

def county_performance_select(df, selected_state):
    """Display a selectbox for county performance based on selected state."""
    counties = df[df['state'] == selected_state]['placeOfPerformanceZIPCode__county'].dropna().unique().tolist()
    with st.sidebar.expander(f"Counties in {selected_state}", expanded=True):
        selected_county = st.sidebar.selectbox(
            "Filter by Performance County:",
            options=["All"] + sorted(counties)
        )
    return selected_county

def disp_performance_filters(df):
    selected_state = "All"
    selected_county = "All"
    selected_country = "All"

    """Display filters for performance location."""
    # sort list but put "United States" at the top
    selected_country = country_performance_select(df)
    print(f"Selected country: {selected_country}")
    if (selected_country == "UNITED STATES"):
        selected_state = state_performance_select(df)
        # IF selected_state != "All", then filter counties by that state
        if selected_state != "All":
            selected_county = county_performance_select(df, selected_state)
    return selected_country, selected_state, selected_county

def filter_by_performance_location(df, selected_country, selected_state, selected_county):
    """Filter the DataFrame based on performance location selections."""
    if selected_country != "All":
        df = df[df['principalPlaceOfPerformance__countryCode__name'] == selected_country]
    if selected_state != "All":
        df = df[df['state'] == selected_state]
    if selected_county != "All":
        df = df[df['placeOfPerformanceZIPCode__county'] == selected_county]
    return df

def country_vendor_select(df):
    """Display a selectbox for vendor country."""
    country_options = sorted(df['vendorLocation__countryCode__name'].dropna().unique().tolist())
    country_options.sort(key=lambda x: (x != "UNITED STATES", x))
    selected_country = st.sidebar.selectbox(
        "Filter by Vendor Country:",
        options=["All"] + country_options
    )
    return selected_country

def state_vendor_select(df, selected_country):
    """Display a selectbox for vendor state."""
    state_options = sorted(df[df['vendorLocation__countryCode__name'] == selected_country]['vendorLocation__state'].dropna().unique().tolist())
    print(f"State options for {selected_country}: {state_options}")
    selected_state = st.sidebar.selectbox(
        "Filter by Vendor State:",
        options=["All"] + state_options
    )
    return selected_state

# def zip_vendor_select(df, selected_state):
#     """Display a selectbox for vendor ZIP code based on selected state."""
#     zip_codes = df[df['vendorLocation__state'] == selected_state]['vendorLocation__ZIPCode_5'].dropna().unique().tolist()
#     with st.sidebar.expander(f"ZIP Codes in {selected_state}", expanded=True):
#         selected_zip = st.sidebar.selectbox(
#             "Filter by Vendor ZIP Code:",
#             options=["All"] + sorted(zip_codes)
#         )
#     return selected_zip

def disp_vendor_filters(df):
    selected_state = "All"
    selected_zip = "All"
    selected_country = "All"

    """Display filters for vendor location."""
    # sort list but put "United States" at the top
    selected_country = country_vendor_select(df)
    print(f"Selected country: {selected_country}")
    if (selected_country == "UNITED STATES"):
        selected_state = state_vendor_select(df,selected_country)
        # IF selected_state != "All", then filter zip codes by that state
        # if selected_state != "All":
        #     selected_zip = zip_vendor_select(df, selected_state)
    return selected_country, selected_state #, selected_zip

def filter_by_vendor_location(df, selected_country, selected_state):
    """Filter the DataFrame based on vendor location selections."""
    if selected_country != "All":
        df = df[df['vendorLocation__countryCode__name'] == selected_country]
    if selected_state != "All":
        df = df[df['vendorLocation__state'] == selected_state]
    # if selected_zip != "All":
    #     df = df[df['vendorLocation__ZIPCode_5'] == selected_zip]
    return df

st.title("Cancelled Fed Contracts")

remote_data = "https://storage.googleapis.com/bln-data-public/terminated-fed-contracts/collected_F.filtered.csv"
df = pandas.read_csv(remote_data)

## Toggle one set of location dropdowns if the user wants to filter by Performance Location or Vendor Location
location_type = st.sidebar.radio(
    "Location type to filter by:",
    options=["Performance Location (where the work took place)", "Vendor Location (where the vendor is based)"]
)

if location_type == "Performance Location (where the work took place)":

    selected_country, selected_state, selected_county = disp_performance_filters(df)
    # Filter the DataFrame based on performance location selections
    df = filter_by_performance_location(df, selected_country, selected_state, selected_county)

else:
    selected_country, selected_state  = disp_vendor_filters(df)
    selected_county = "All"
    # Filter the DataFrame based on vendor location selections
    df = filter_by_vendor_location(df, selected_country, selected_state)


# Search vendor name -- multiselect from dropdown but type to search
selected_vendor = st.sidebar.multiselect(
    "Filter by Vendor Name:",
    options=sorted(df['business'].dropna().unique().tolist()),
    default=[]
)

# Search department name -- multiselect from dropdown but type to search
selected_department = st.sidebar.multiselect(
    "Filter by Department Name:",
    options=sorted(df['contractingOfficeAgencyID__departmentName'].dropna().unique().tolist()),
    default=[]
)

if selected_department:
    df = df[df['contractingOfficeAgencyID__departmentName'].isin(selected_department)]

# Search agency name -- multiselect from dropdown but type to search
selected_agency = st.sidebar.multiselect(
    "Filter by Agency Name:",
    options=sorted(df['agency'].dropna().unique().tolist()),
    default=[]
)

# Keyword search general_service_description and contract_requirement
selected_keyword = st.sidebar.text_input(
    "Search by Keyword:",
    placeholder="Search service description & contract requirement. E.g., 'weapon', 'janitor', etc.",
)
# Filter the DataFrame based on vendor selection
if selected_vendor:
    df = df[df['business'].isin(selected_vendor)]
# Filter the DataFrame based on agency selection
if selected_agency:
    df = df[df['agency'].isin(selected_agency)]
# Filter the DataFrame based on keyword search
if selected_keyword:
    keyword_lower = selected_keyword.lower()
    df = df[df['general_service_description'].str.lower().str.contains(keyword_lower, na=False) |
            df['contract_requirement'].str.lower().str.contains(keyword_lower, na=False)]
# Filter the DataFrame based on county selection



st.markdown("""
This dashboard lets you explore and download data about canceled federal contracts.

- :point_left: Use the dropdowns in the sidebar to filter the data by performance location or vendor location.
- :arrow_down: Hover on the table to download the filtered data.

""")

# # Filter the DataFrame based on selection
# if selected_state == "All":
#     filtered_df = df
#     # When showing all states, aggregate by state
#     group_by_column = 'state'
#     chart_title = 'States by Amount'
#     y_axis_title = 'State'
# else:
#     filtered_df = df[df['state'] == selected_state]
#     # When filtering by a specific state, aggregate by county
#     group_by_column = 'county'
#     chart_title = f'Counties in {selected_state} by Amount'
#     y_axis_title = 'County'

# Create aggregated data based on the grouping column
# chart_data = filtered_df.groupby(group_by_column).agg({
#     'amount': 'sum',
#     group_by_column: 'count'
# }).rename(columns={group_by_column: 'count'}).reset_index()

# chart_data = chart_data.sort_values('amount', ascending=False)

# max_items = min(5, len(chart_data))
# num_items = st.slider(f"Number of top {y_axis_title.lower()}s to display:", 1, len(chart_data), max_items)

# display_data = chart_data.head(num_items)

# # Create horizontal bar chart with Altair
# chart = alt.Chart(display_data).mark_bar().encode(
#     x=alt.X('amount:Q', title='Total Amount ($)'),
#     y=alt.Y(f'{group_by_column}:N', sort='-x', title=y_axis_title),
#     tooltip=[f'{group_by_column}:N', 'amount:Q', 'count:Q']
# ).properties(
#     title=chart_title,
#     width=600,
#     height=max(200, num_items * 30)
# )

# st.altair_chart(chart, use_container_width=True)


st.dataframe(df)


st.markdown("""

> TK Add links to platform, BLN, fed data portal, etc.
> NOTE: This data is a subset of the [Big Local News Federal Contracts dataset](https://biglocalnews.org/federal-contracts/). It includes only select columns about contracts that were "Terminated for Convenience" (Collected_F.csv), and it is updated daily.


&copy; Big Local News (2025)

""")

