# Contracts Dashboard

Demo of a [streamlit](https://docs.streamlit.io) data dashboard that includes:

- filtering by state
- a basic horizontal bar chart that tallies amounts by states/counties
- scrollable table that allows for data download

We should be able to deploy this to [Streamlit Cloud](https://streamlit.io/cloud) or use some other hosting option.

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

Prep a data file for the streamlit app by downloading it and
placing it in the `dashboards/` directory.

Then process the data to produce a simplified version that has been
deduplicated, keeping only the most recent update for each contract.

```
cd sync-fed-contracts/

uv run python filter_most_recent.py collected_F.py
```

## Run dashboard

```bash
cd sync-fed-contracts/

# Run the dashboard
uv run streamlit run dashboard/app.py
```
