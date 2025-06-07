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


st.title("Canceled Fed Contracts")

infile = Path(__file__).parent.joinpath("collected_F.filtered.csv")
df = pandas.read_csv(infile)


selected_state = st.sidebar.selectbox(
    "Filter by State:",
    options=["All"] + sorted(df['state'].dropna().unique().tolist())
)

# Filter the DataFrame based on selection
if selected_state == "All":
    filtered_df = df
else:
    filtered_df = df[df['state'] == selected_state]


st.markdown("""
This dashboard lets you explore and download data about canceled federal contracts.

- :point_left: Select a state from the sidebar to filter the data.
- :arrow_down: Hover on the table to download the whole data set (or a filtered selection).
- &harr; Use the slider below (:point_down:) to adjust the number of rows displayed in the chart.

""")

# Filter the DataFrame based on selection
if selected_state == "All":
    filtered_df = df
    # When showing all states, aggregate by state
    group_by_column = 'state'
    chart_title = 'States by Amount'
    y_axis_title = 'State'
else:
    filtered_df = df[df['state'] == selected_state]
    # When filtering by a specific state, aggregate by county
    group_by_column = 'county'
    chart_title = f'Counties in {selected_state} by Amount'
    y_axis_title = 'County'

# Create aggregated data based on the grouping column
chart_data = filtered_df.groupby(group_by_column).agg({
    'amount': 'sum',
    group_by_column: 'count'
}).rename(columns={group_by_column: 'count'}).reset_index()

chart_data = chart_data.sort_values('amount', ascending=False)

max_items = min(5, len(chart_data))
num_items = st.slider(f"Number of top {y_axis_title.lower()}s to display:", 1, len(chart_data), max_items)

display_data = chart_data.head(num_items)

# Create horizontal bar chart with Altair
chart = alt.Chart(display_data).mark_bar().encode(
    x=alt.X('amount:Q', title='Total Amount ($)'),
    y=alt.Y(f'{group_by_column}:N', sort='-x', title=y_axis_title),
    tooltip=[f'{group_by_column}:N', 'amount:Q', 'count:Q']
).properties(
    title=chart_title,
    width=600,
    height=max(200, num_items * 30)
)

st.altair_chart(chart, use_container_width=True)


st.dataframe(filtered_df)


st.markdown("""

> TK Add links to platform, BLN, fed data portal, etc.

&copy; Big Local News (2025)

""")

