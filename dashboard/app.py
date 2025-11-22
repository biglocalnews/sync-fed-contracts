"""
Things to (possibly) update or add:
- PullQuote style numbers
- Add clickable links to the table that go to contract pages
- Loading from remote CSV file(s)    # Implemented?
- Optimize data loading with st.cache_data, where needed
- Methodology page
- Data dictionary page     # Implemented? Point to columns file once that goes live in main

"""

# import datetime
from pathlib import Path

# import altair as alt
import pandas
import streamlit as st

# We're styling the currency column of the displayed df, so this limit comes into play
# Might want to adjust how we handle this as the number of rows grows over time
# pandas.set_option("styler.render.max_elements", 10**7)

DEFAULT_START_DATE = pandas.to_datetime(
    "01-20-2025"
)  # Default start date for the date range slider


def select_date_range(df):
    """Display a date range slider to filter the DataFrame with an optional default start date."""
    min_date = df["date_cancelled"].min()
    max_date = df["date_cancelled"].max()

    date_range = st.sidebar.date_input(
        "Select date range (Cancelled Date):",
        value=(DEFAULT_START_DATE, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    if len(date_range) == 2:
        start_date, end_date = date_range
        return start_date, end_date
    return date_range[0], max_date


def country_performance_select(df):
    """Display a selectbox for country performance."""
    country_options = sorted(df["performance_country"].dropna().unique().tolist())
    country_options.sort(key=lambda x: (x != "UNITED STATES", x))
    selected_country = st.sidebar.selectbox(
        "Filter by Performance Country:", options=["All"] + country_options
    )
    return selected_country


def state_performance_select(df):
    """Display a selectbox for state performance."""
    state_options = sorted(df["performance_state"].dropna().unique().tolist())
    selected_state = st.sidebar.selectbox(
        "Filter by Performance State:", options=["All"] + state_options
    )
    return selected_state


def county_performance_select(df, selected_state):
    """Display a selectbox for county performance based on selected state."""
    counties = (
        df[df["performance_state"] == selected_state]["performance_county"]
        .dropna()
        .unique()
        .tolist()
    )
    with st.sidebar.expander(f"Counties in {selected_state}", expanded=True):
        selected_county = st.sidebar.selectbox(
            "Filter by Performance County:", options=["All"] + sorted(counties)
        )
    return selected_county


def disp_performance_filters(df):
    selected_state = "All"
    selected_county = "All"
    selected_country = "All"
    # sort list but put "United States" at the top
    selected_country = country_performance_select(df)
    print(f"Selected country: {selected_country}")
    if selected_country == "UNITED STATES":
        selected_state = state_performance_select(df)
        # IF selected_state != "All", then filter counties by that state
        if selected_state != "All":
            selected_county = county_performance_select(df, selected_state)
    return selected_country, selected_state, selected_county


def filter_by_performance_location(
    df, selected_country, selected_state, selected_county
):
    """Filter the DataFrame based on performance location selections."""
    if selected_country != "All":
        df = df[df["performance_country"] == selected_country]
    if selected_state != "All":
        df = df[df["performance_state"] == selected_state]
    if selected_county != "All":
        df = df[df["performance_county"] == selected_county]
    return df


def country_vendor_select(df):
    """Display a selectbox for vendor country."""
    country_options = sorted(df["vendor_country"].dropna().unique().tolist())
    country_options.sort(key=lambda x: (x != "UNITED STATES", x))
    selected_country = st.sidebar.selectbox(
        "Filter by Vendor Country:", options=["All"] + country_options
    )
    return selected_country


def state_vendor_select(df, selected_country):
    """Display a selectbox for vendor state."""
    state_options = sorted(
        df[df["vendor_country"] == selected_country]["vendor_state"]
        .dropna()
        .unique()
        .tolist()
    )
    print(f"State options for {selected_country}: {state_options}")
    selected_state = st.sidebar.selectbox(
        "Filter by Vendor State:", options=["All"] + state_options
    )
    return selected_state


def county_vendor_select(df, selected_state):
    """Display a selectbox for vendor county code based on selected state."""
    zip_codes = (
        df[df["vendor_state"] == selected_state]["vendor_county"]
        .dropna()
        .unique()
        .tolist()
    )
    with st.sidebar.expander(f"Counties in {selected_state}", expanded=True):
        selected_zip = st.sidebar.selectbox(
            "Filter by Vendor county:", options=["All"] + sorted(zip_codes)
        )
    return selected_zip


def disp_vendor_filters(df):
    selected_state = "All"
    selected_county = "All"
    selected_country = "All"

    """Display filters for vendor location."""
    # sort list but put "United States" at the top
    selected_country = country_vendor_select(df)
    print(f"Selected country: {selected_country}")
    if selected_country == "UNITED STATES":
        selected_state = state_vendor_select(df, selected_country)
        # If selected_state != "All", then filter counties by that state
        if selected_state != "All":
            selected_county = county_vendor_select(df, selected_state)
    return selected_country, selected_state, selected_county


def filter_by_vendor_location(df, selected_country, selected_state, selected_county):
    """Filter the DataFrame based on vendor location selections."""
    if selected_country != "All":
        df = df[df["vendor_country"] == selected_country]
    if selected_state != "All":
        df = df[df["vendor_state"] == selected_state]
    if selected_county != "All":
        df = df[df["vendor_county"] == selected_county]
    return df


st.title("Federal Contracts Terminated for Convenience")

remote_data = "https://storage.googleapis.com/bln-data-public/terminated-fed-contracts/convenience--limited_cols.csv"
local_data = Path(__file__).parent / "../data/convenience--limited_cols.csv"  # not used
df = pandas.read_csv(remote_data)


start_date, end_date = select_date_range(df)
# Filter the DataFrame based on the selected date range
df["date_cancelled"] = pandas.to_datetime(df["date_cancelled"], errors="coerce")
df = df[
    (df["date_cancelled"] >= pandas.to_datetime(start_date))
    & (df["date_cancelled"] <= pandas.to_datetime(end_date))
]


# Toggle one set of location dropdowns if the user wants to filter by Performance Location or Vendor Location
location_type = st.sidebar.radio(
    "Location type to filter by:",
    options=[
        "Performance Location (where the work took place)",
        "Vendor Location (where the vendor is based)",
    ],
)


if location_type == "Performance Location (where the work took place)":

    selected_country, selected_state, selected_county = disp_performance_filters(df)
    # Filter the DataFrame based on performance location selections
    df = filter_by_performance_location(
        df, selected_country, selected_state, selected_county
    )

else:
    selected_country, selected_state, selected_county = disp_vendor_filters(df)
    selected_county = "All"
    # Filter the DataFrame based on vendor location selections
    df = filter_by_vendor_location(
        df, selected_country, selected_state, selected_county
    )


# Search vendor name -- multiselect from dropdown but type to search
selected_vendor = st.sidebar.multiselect(
    "Filter by Vendor Name:",
    options=sorted(df["vendor"].dropna().unique().tolist()),
    default=[],
)

# Search department name -- multiselect from dropdown but type to search

all_depts = (
    pandas.concat(
        [df["contracting_agency_department"], df["funding_agency_department"]]
    )
    .dropna()
    .unique()
    .tolist()
)
selected_departments = st.sidebar.multiselect(
    "Filter by Department Name:",
    options=sorted(all_depts),
    default=[],
)

if selected_departments:
    df = df[
        (df["contracting_agency_department"].isin(selected_departments))
        | (df["funding_agency_department"].isin(selected_departments))
    ]

# contracting_agency	contracting_agency_department	funding_agency	funding_agency_department


# Search agency name -- multiselect from dropdown but type to search
all_agencies = (
    pandas.concat([df["admin_agency"], df["funding_agency"]]).dropna().unique().tolist()
)
selected_agencies = st.sidebar.multiselect(
    "Filter by Agency Name:",
    options=sorted(all_agencies),
    default=[],
)

# Keyword search general_service_description and contract_requirement
selected_keyword = st.sidebar.text_input(
    "Search by Keyword:",
    placeholder="Search product/service description & contract requirement. E.g., 'weapon', 'janitor', etc.",
)
# Filter the DataFrame based on vendor selection
if selected_vendor:
    df = df[df["vendor"].isin(selected_vendor)]
# Filter the DataFrame based on agency selection
if selected_agencies:
    df = df[
        (df["admin_agency"].isin(selected_agencies))
        | (df["funding_agency"].isin(selected_agencies))
    ]
# Filter the DataFrame based on keyword search
if selected_keyword:
    keyword_lower = selected_keyword.lower()
    df = df[
        df["product_or_service_description"]
        .str.lower()
        .str.contains(keyword_lower, na=False)
        | df["contract_requirement"].str.lower().str.contains(keyword_lower, na=False)
    ]

st.markdown(
    """
This dashboard lets you explore and download data about canceled federal contracts.
:point_left: Use the dropdowns in the sidebar to filter the data by performance location or vendor location.
:arrow_down: Hover on the table to download the filtered data.

"""
)

st.info(
    """[Data dictionary](https://github.com/biglocalnews/sync-fed-contracts/blob/main/highlighted_columns.md)"""
)

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


st.dataframe(df, column_config={
    "amount_cancelled": st.column_config.NumberColumn(format="$ %.2f")
})

st.markdown(
    """


### The full "terminated for convenience" dataset has more columns.
We’ve limited the number of columns here and renamed them for clarity and ease of use. You can find a full list of original column names and definitions [here](https://www.fpds.gov/downloads/Version_1.5_specs/FPDS_DataDictionary_V1.5.pdf), and download the complete dataset — including renamed and original columns — as the [Big Local News Federal Contracts dataset](https://biglocalnews.org/#/project/UHJvamVjdDpjZjgyZTRkYS0xNTQ4LTQ4NGUtOTk2MC1mNzk4ZTg4NmY5ODM=) (accessible with a free account). The data was sourced from this [federal procurement portal](https://www.fpds.gov/fpdsng_cms/index.php/en/) using the code in [this GitHub repository](https://github.com/biglocalnews/sync-fed-contracts).

### We also track more cancellations data.
This dashboard shows only terminations “for convenience,” defined as "the exercise of the government’s right to completely or partially terminate performance of work under a contract when it is in the government’s interest." This excludes contracts terminated for cause, default, legal reasons, or administrative closeout, which are included separately in the [Big Local News Federal Contracts dataset](https://biglocalnews.org/#/project/UHJvamVjdDpjZjgyZTRkYS0xNTQ4LTQ4NGUtOTk2MC1mNzk4ZTg4NmY5ODM=). You can read more about how terminations are categorized [here](https://www.dau.edu/acquipedia-article/contract-termination).

### Date filters are based on the cancellation date.
Our system gathers contract termination records as they are reported to FPDS. We began collecting data on January 20, but users may see contracts canceled before that date due to reporting delays — for example, some Q4 terminations from the previous year were not reported until after 1/20.
Similarly, data from the current quarter may be incomplete due to lag in reporting. By default, the dashboard filters for contracts canceled on or after 1/20, but you can adjust the date filter to explore earlier records.

&copy; Big Local News (2025)

"""
)
