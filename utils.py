# Cached utils for the dashboard
import pandas as pd
import plotly.express as px
import streamlit as st

# Set up list of financial, ESG, and company info columns
esg_cols = [
    "Bloomberg ESG Score",
    "Bloomberg Environmental Pillar",
    "Bloomberg Governance Pillar",
    "Bloomberg Social Pillar",
    "S&P Global ESG Rank",
    "S&P Global Governance & Economic Dimension Rank",
    "S&P Global Environmental Dimension Rank",
    "S&P Global Social Dimension Rank",
    "Yahoo Finance ESG Score",
    "Yahoo Finance Environmental Score",
    "Yahoo Finance Social Score",
    "Yahoo Finance Governance Score",
]
fin_cols = [
    "Monthly Return",
    "Price",
    "Credit Risk Indicator",
    "Beta",
    "Alpha",
    "Issuer Default Risk",
    "30 Day Volatility",
    "P/E Ratio",
    "Market Cap",
    "Historical Market Cap",
    "EPS",
]
company_cols = [
    "Ticker",
    "GICS Sector",
    "GICS Industry",
    "GICS Industry Group",
    "GICS Sub-Industry",
]
other_cols = ["Date", "Month", "Year"]
pred_cols = ["Monthly Return", "Lasso Model"]  # TODO: Use, add more


# Load in final dataset
@st.cache_data
def get_final_df(winsorize=0):
    """
    Load in the final dataset and winsorize top and bottom % of returns

    :param float winsorize: Percent of returns to winsorize. Default 0.
    :return: Final dataset
    :rtype: pd.DataFrame
    :raises ValueError: If winsorize value is not within bounds [0, 1)
    :raises TypeError: If winsorize value is not a float
    """
    # Check input
    if not isinstance(winsorize, float):
        TypeError("Winsorize value must be a float")
    if winsorize >= 1 or winsorize < 0:
        ValueError("Winsorize value must be between 0 and 1")

    # Load in final dataset
    final_df = pd.read_csv("inputs/final_dataset.csv")
    final_df["Date"] = pd.to_datetime(final_df["Date"])

    # Winsorize top and bottom % of returns
    if winsorize:
        top = final_df["Monthly Return"].quantile(1 - winsorize)
        bottom = final_df["Monthly Return"].quantile(winsorize)
        final_df["Monthly Return"] = final_df["Monthly Return"].clip(bottom, top)

    return final_df


# Cache filtered dataset
@st.cache_data
def get_rel_df(final_df, start_date, end_date):
    # Filter to show only dates in the selected range
    rel_df = final_df[(final_df["Date"] >= start_date) & (final_df["Date"] <= end_date)]

    # Multiply to get numerator for weighted average
    cap_esg_labels = [f"Cap {esg}" for esg in esg_cols]
    rel_df[cap_esg_labels] = rel_df[esg_cols].multiply(rel_df["Market Cap"], axis=0)
    rel_df["Cap Monthly Return"] = rel_df["Monthly Return"] * rel_df["Market Cap"]

    return rel_df


# Aggregate by agg_level and ESG score, TODO no real reason to cache
@st.cache_data
def get_rel_df_agg(rel_df, agg_level, esg_x):
    # Average by agg_level
    rel_df["Average Monthly Return"] = rel_df.groupby([agg_level, "Date"])[
        "Cap Monthly Return"
    ].transform("sum") / rel_df.groupby([agg_level, "Date"])["Market Cap"].transform(
        "sum"
    )

    # Create average market-weighted score for each agg_level
    rel_df[f"Average {esg_x}"] = rel_df.groupby([agg_level, "Date"])[
        f"Cap {esg_x}"
    ].transform("sum") / rel_df.groupby([agg_level, "Date"])["Market Cap"].transform(
        "sum"
    )

    # Aggregate and select columns
    if agg_level == "GICS Sector":
        rel_df = (
            rel_df.groupby([agg_level])
            .agg({"Average Monthly Return": "mean", f"Average {esg_x}": "mean"})
            .reset_index()
            .drop_duplicates()
        )
    else:
        rel_df = (
            rel_df.groupby([agg_level])
            .agg(
                {
                    "Average Monthly Return": "mean",
                    f"Average {esg_x}": "mean",
                    "GICS Sector": "first",
                }
            )
            .reset_index()
            .drop_duplicates()
        )

    return rel_df


@st.cache_data
def get_corr_fig(final_df):
    corr_df = final_df[esg_cols].corr()
    corr_fig = px.imshow(
        corr_df,
        x=corr_df.columns,
        y=corr_df.columns,
        color_continuous_scale="RdBu",
        zmin=-1,
        zmax=1,
    )
    corr_fig.update_layout(height=600)
    return corr_fig


@st.cache_data
def get_dist_fig(final_df):
    # Create interactive distribution plot
    dist_df = final_df.melt(
        id_vars=["Date", "Ticker"],
        value_vars=esg_cols,
        var_name="ESG",
        value_name="Score",
    )

    # Set the score Source
    dist_df["Source"] = dist_df["ESG"].apply(
        lambda x: (
            "Bloomberg"
            if "Bloomberg" in x
            else (
                "S&P Global"
                if "S&P Global" in x
                else "Yahoo Finance" if "Yahoo Finance" in x else "Unknown"
            )
        )
    )
    dist_df = dist_df[dist_df["Source"] != "Unknown"]
    dist_df = dist_df.sort_values(by=["Source", "ESG"])

    dist_fig = px.histogram(
        dist_df,
        x="Score",
        color="Source",
        facet_col="ESG",
        facet_col_wrap=4,
        facet_row_spacing=0.16,
        facet_col_spacing=0.08,
    )

    dist_fig.for_each_yaxis(lambda y: y.update(showticklabels=True, matches=None))
    dist_fig.for_each_xaxis(lambda x: x.update(showticklabels=True, matches=None))
    for annotation in dist_fig.layout.annotations:
        annotation.text = annotation.text.split("=")[1]
        # Remove Bloomberg, S&P Global, and Yahoo Finance from the facet titles
        annotation.text = annotation.text.replace("Bloomberg ", "")
        annotation.text = annotation.text.replace("S&P Global ", "")
        annotation.text = annotation.text.replace("Yahoo Finance ", "")
    dist_fig.update_layout(height=800)
    return dist_fig


# Show description tab
@st.cache_data
def show_description_tab():
    # Load the README into markdown format
    with open("README.md", "r") as f:
        report = f.read()

    # Show only ## headers for TOC
    headers = [h.replace("## ", "") for h in report.split("\n") if h.startswith("## ")]
    toc = st.expander("Table of Contents")
    with toc:
        for h in headers:
            st.markdown(f'- [{h}](#{h.lower().replace(" ", "-")})')

    # Add two header levels to the report and display it
    report = report.replace("# ", "## ")
    st.markdown(report)


# Show ESG metric tab
@st.cache_data
def show_correlation_tab(final_df):
    # Get slow loading figures
    corr_fig = get_corr_fig(final_df)
    dist_fig = get_dist_fig(final_df)

    # Describe
    st.header("ESG Metric Details")
    st.markdown(
        """
  This page shows the relationship between each set of ESG metrics. Because
  the metrics are calculated by different providers, they are not
  directly comparable. However, we should still see a relationship between
  the scores as they are all measuring similar underlying factors.
  """
    )

    # Show heatmap of ESG metric correlations
    st.subheader("Correlation Heatmap")
    st.markdown(
        """
  In the heatmap, we see that Bloomberg scores are most distinct from one
  another, while S&P Global and Yahoo Finance scores are very similar to other
  scores from the same source.  As S&P Global creates rankings rather than
  scores, we would expect a negative correlation between S&P Global ranks
  and Yahoo Finance and Bloomberg scores.
  
  Of the inter-source pillars, Yahoo Finance Governance and Yahoo Finance
  Environmental scores are the most similar to one another with a correlation
  of 0.94.

  While Bloomberg scores and S&P Global scores have weak positive correlations
  with one another, Yahoo Finance scores have a weak negative correlation with
  both Bloomberg and S&P Global scores.  The highest cross-source correlation
  is between Bloomberg Environmental and S&P Global Environmental scores at
  0.47.  The lowest cross-source correlation is between Yahoo Finance
  Environmental and Bloomberg ESG scores at -0.31.
  """
    )

    st.plotly_chart(corr_fig, use_container_width=True)

    # Show distribution of ESG metrics
    st.subheader("Distribution of ESG Metrics")
    st.markdown(
        """
  Looking at the distribution of metrics, we see that Bloomberg scores are more
  concentrated around the mean than S&P Global and Yahoo Finance scores.
  We see the uniform distribution of S&P Global rankings, as expected of a rank
  measure.  Yahoo Finance scores show a bimodal distributions.
  """
    )

    st.plotly_chart(dist_fig, use_container_width=True)


# Cache relationship tab
def show_relationship_tab(final_df):
    st.header("Relationship Model")

    # Create columns
    select_col, display_col, desc_col = st.columns([1, 4, 1])

    # Get user input
    with select_col:
        # Select whether to show at the company level or industry level
        st.subheader("Aggregation Level")
        agg_level = st.selectbox(
            "Group By",
            [
                "Ticker",
                "GICS Sector",
                "GICS Industry",
                "GICS Industry Group",
                "GICS Sub-Industry",
            ],
        )

        # Select which ESG score for X axis
        st.subheader("ESG Metric")
        esg_x = st.selectbox("Select ESG Metric", esg_cols)

        # Select which dates to use for analysis
        st.subheader("Date Range")
        start_date = pd.Timestamp(
            st.date_input("Start Date", value=final_df["Date"].min())
        )
        end_date = pd.Timestamp(st.date_input("End Date", value=final_df["Date"].max()))

        # Get the filtered, market-cap scores, computing only on date change
        rel_df = get_rel_df(final_df, start_date, end_date)

        # Aggregate by agg_level selector and average monthly return by market cap
        rel_df = get_rel_df_agg(rel_df, agg_level, esg_x)

    with display_col:
        st.subheader(f"Average Monthly Return vs. {esg_x} by {agg_level}")

        # Scatterplot
        with st.spinner("Updating plot..."):
            dist_fig = px.scatter(
                rel_df,
                x=f"Average {esg_x}",
                y="Average Monthly Return",
                trendline="ols",
                trendline_scope="overall",
                trendline_color_override="black",
                hover_data=[agg_level],
                color="GICS Sector",
            )
            dist_fig.update_traces(marker=dict(opacity=0.4))
            dist_fig.update_layout(scattermode="group")

            st.plotly_chart(dist_fig, use_container_width=True, height=600)

    # Show desription below graph for wider columns
    with desc_col:
        st.subheader("Description")
        st.markdown(
            """
    This model displays the relationship between ESG metrics and monthly
    returns.  Metrics and returns are aggregated by the average market-weighted
    value for each aggregation level, either by Ticker, GICS Industry, GICS
    Sub-Industry, GICS Industry Group, or GICS Sector.

    Dates can be filtered to any range, with the default range set to all dates
    in the dataset.
    """
        )

    # Create columns for explanations and summary stats
    st.markdown("---")
    exp_col, stat_col = st.columns([1, 1])

    with exp_col:
        # Explain each ESG score
        st.subheader("ESG Metric Descriptions")
        st.markdown(
            """
    **Bloomberg**
    - Covering 12,000 companies, or 88% of the global equity market, 
    Bloomberg ESG scores analyze the corporate social responsibility reports to
    generate comparable metrics. 
    Recent and detailed information about these scores was relatively difficult
    to find.
    More on the methodology of ESG scoring can be found
    in Bloomberg's most recent [materiality assessment](
    https://data.bloomberglp.com/company/sites/28/2017/01/17_0419_Materiality-Assessment.pdf)
    
    **Standard & Poor's (S&P)**
    - S&P uses a weighted model on all levels of their ESG analysis. 
    The three dimensions of ESG are weighted based on controversies. 
    Within each dimension, questions and criteria are weighted depending on
    industry-specific approaches.
    About 1,000 data points are used for each of the 8,000 companies covered by
    S&P ESG scores.
    [Learn more here.](
    https://www.spglobal.com/esg/solutions/data-intelligence-esg-scores)
    
    **Yahoo Finance**
    - A two-dimensional framework is used to examine two factors of companies. 
    First, how exposed is a company to industry-specific ESG risk factors?
    Second, how well is the company doing at managing those ESG risks?
    The total ESG score is a total of the scores given to each ESG dimension and
    is scored on a scale of 1-100.
    """
        )

    with stat_col:
        # Show summary stats
        st.subheader("Summary Statistics")

        # Show summary stats
        st.write(rel_df.describe())


def show_predictive_tab(final_df):
    st.header("Predictive Model")

    # Create columns
    select_col, display_col, desc_col = st.columns([1, 3, 1])

    # Get user input
    with select_col:
        st.subheader("Select Industry")
        # Create checkbox for each industry, removing nan
        industries = final_df["GICS Sector"].unique()
        industries = industries[~pd.isna(industries)].tolist()
        industries.append("All Industries")
        industries.sort()
        selected_industry = st.selectbox("Select Industry", industries)

        st.subheader("Smoothing")
        smoothing = st.slider(
            "Months to Smooth", min_value=0, max_value=12, value=6, step=1
        )

        # Filter to selected industries
        if selected_industry == "All Industries":
            pred_df = final_df
        else:
            pred_df = final_df[final_df["GICS Sector"] == selected_industry]

    # Display the graph
    with display_col:
        st.subheader(f"Predicted Monthly Returns in {selected_industry}")
        # Sort by date
        pred_df = pred_df.sort_values(by="Date")

        # Create market weighted return by date, grouped by industry
        pred_df["Monthly Return"] = pred_df["Monthly Return"] * pred_df["Market Cap"]
        pred_df["Lasso Model Return"] = pred_df["Lasso Model"] * pred_df["Market Cap"]
        if selected_industry == "All Industries":
            pred_df["Monthly Return"] = pred_df.groupby(["Date"])[
                "Monthly Return"
            ].transform("sum") / pred_df.groupby(["Date"])["Market Cap"].transform(
                "sum"
            )
            pred_df["Lasso Model Return"] = pred_df.groupby(["Date"])[
                "Lasso Model Return"
            ].transform("sum") / pred_df.groupby(["Date"])["Market Cap"].transform(
                "sum"
            )
        else:
            pred_df["Monthly Return"] = pred_df.groupby(["GICS Sector", "Date"])[
                "Monthly Return"
            ].transform("sum") / pred_df.groupby(["GICS Sector", "Date"])[
                "Market Cap"
            ].transform(
                "sum"
            )
            pred_df["Lasso Model Return"] = pred_df.groupby(["GICS Sector", "Date"])[
                "Lasso Model Return"
            ].transform("sum") / pred_df.groupby(["GICS Sector", "Date"])[
                "Market Cap"
            ].transform(
                "sum"
            )

        # Drop duplicates
        pred_df = pred_df[
            ["Date", "Monthly Return", "Lasso Model Return"]
        ].drop_duplicates()

        # Smooth the data
        if smoothing:
            pred_df["Monthly Return"] = (
                pred_df["Monthly Return"].rolling(smoothing).mean()
            )
            pred_df["Lasso Model Return"] = (
                pred_df["Lasso Model Return"].rolling(smoothing).mean()
            )

        # Winsorize
        top_5 = pred_df["Lasso Model Return"].quantile(0.99)
        bottom_5 = pred_df["Lasso Model Return"].quantile(0.01)
        pred_df["Lasso Model Return"] = pred_df["Lasso Model Return"].clip(
            bottom_5, top_5
        )

        # Pivot to long format
        pred_df_long = pred_df.melt(
            id_vars=["Date"],
            value_vars=["Monthly Return", "Lasso Model Return"],
            var_name="Return Type",
            value_name="Return",
        )

        # Line chart grouped by ticker
        with st.spinner("Updating plot..."):
            dist_fig = px.line(
                pred_df_long,
                x="Date",
                y="Return",
                color="Return Type",
                # line_dash='Return Type'
            )
            dist_fig.update_traces(opacity=0.8)

            st.plotly_chart(dist_fig, use_container_width=True, height=600)

    # Display the description
    with desc_col:
        st.subheader("Description")
        st.markdown(
            """
    In this model, we display our predicted monthly returns for each industry
    against the actual monthly returns. The predicted returns are calculated
    ticker-by-ticker for each company in the S&P 500 at the end of each month,
    using a time-series based train test split. The predicted returns are then
    aggregated by GICS Industry and displayed against the actual monthly returns
    for each industry.
    """
        )

    # Create cols to explain models and show summary stats
    st.markdown("---")
    exp_col, stats_col = st.columns([1, 1])

    # Show main descriptions under the graph
    with exp_col:
        st.subheader("Model Descriptions")
        # TODO how sad
        st.markdown(
            """
    The simple Lasso model uses lagging ESG scores and economic indicators to
    predict the next month's return.  We see that the model performs very poorly
    in predicting the next month's return, assuming returns are mostly random
    with an average predicted value less than the absolute value of 1%.
    """
        )

    # Show summary stats under the graph
    with stats_col:
        st.subheader("Summary Statistics")

        # Show summary stats
        st.write(pred_df.describe())


# TODO
print("Imported utils.py")
