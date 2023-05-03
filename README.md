# Description

In this dashboard, we visualize the ESG scores and market performance of S&P 500 companies from 2015 to 2023.  The dashboard is deployed using Streamlit at [this link](https://nicole-elchaar-esg-dashboard-app-mpiwio.streamlit.app), and the source repo is available on Github [here](https://github.com/nicole-elchaar/esg-dashboard).

## Visualizations

All plots are interactive through Plotly and can be found on the respective tabs.

### The Relationship Model

In our relationship model, we display average market-weighted monthly returns by company, GICS Sector, GICS Industry, GICS Industry Group, or GICS Sub-Industry against twelve possible ESG metrics.  Users can select any time period in which to examine this relationship.

### The Predictive Model

In our predictive model, we see if ESG scores have any impact on performance.  We use a Lasso model to predict the monthly returns of a company based on its ESG scores and selected financial metrics, comparing predicted returns from our model against actual returns.

The coefficients of each model are shown below the plot.

### ESG Metric Exploration

In the ESG Metric Details tab, we view the distribution of ESG metrics and the relationships between them.

## Data

Data is sourced from Bloomberg, and our final set is available in the *inputs* folder.  Each row is unique by ticker and date, representing a snapshot at the end of each month for companies in the S&P 500 from 2015 to 2023.

## Usage

### Running Locally

To run from your own machine, clone the repo and install requirements of *requirements.txt* to a new environment.

```bash
conda create --name esg-dashboard
conda activate esg-dashboard
python -m pip install -r requirements.txt
```

From the main directory, run the following from the main repository to start the app:

```bash
streamlit run app.py
```

# Credits

Many thanks to [@donbowen](https://bowen.finance) for the guidance throughout!
