# Contracts Dashboard

This creates a [streamlit](https://docs.streamlit.io) data dashboard that includes:

- filtering by state
- a basic horizontal bar chart that tallies amounts by states/counties
- scrollable table that allows for data download


## Bootstrap

Assuming you're using `uv`...

```bash
cd sync-fed-contracts/
uv sync
```

Otherwise...

```bash
pip install streamlit altair pandas
```

## Prep data

Prep a data file for the streamlit app by running `extract-to-csvs.py`.

This will place a file called `convenience--limited_cols.csv` in `data/`.


## Run dashboard

```bash
cd sync-fed-contracts/

# Run the dashboard
uv run streamlit run dashboard/app.py
```
