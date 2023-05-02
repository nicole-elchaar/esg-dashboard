import matplotlib.pyplot as plt
import os
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
import seaborn as sns
import streamlit as st
from plotly.subplots import make_subplots

# Usage:
# streamlit run app.py

# Make page content wider
st.set_page_config(
    page_title="ESG x Market Performance",
    page_icon=":earth_americas:",
    layout="wide",)

# Allow long selection columns to scroll
st.markdown(
    '''
      <style>
          [data-testid="column"] > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div {
          overflow: auto;
          max-height: 90vh;
        }
      </style>
    ''',
    unsafe_allow_html=True)

# Hide the streamlit backend features in serve
st.markdown(
    '''
      <style>
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
      </style>
    ''',
    unsafe_allow_html=True)

# Set up paths
input_path = 'inputs/'

# Set the title
st.title('ESG x Market Performance :earth_americas:')
st.markdown('''Nathan Alakija, Nicole ElChaar, Mason Otley, Xiaozhe Zhang''')

# Use three main tabs: Description, Relationship Model, and Predictive Model
tab_list = ['Description','Report','ESG Score Details','Relationship Model',
            'Predictive Model']
description_tab,report_tab,correlation_tab,relationship_tab,predictive_tab = \
    st.tabs(tab_list)
    # st.tabs([s.center(25, '\u2001') for s in tab_list])

# Load in final dataset
final_df = pd.read_csv(input_path + 'final_dataset.csv')
final_df['Date'] = pd.to_datetime(final_df['Date'])

# TODO Keep only first 100 rows for testing
# final_df = final_df.iloc[:100]

# Remove extreme outliers in monthly return > 99% and < 1%
top_5 = final_df['Monthly Return'].quantile(0.99)
bottom_5 = final_df['Monthly Return'].quantile(0.01)
final_df = final_df[final_df['Monthly Return'] < top_5]
final_df = final_df[final_df['Monthly Return'] > bottom_5]

# Set up list of financial, ESG, and company info columns
esg_cols = ['Bloomberg ESG Score', 'Bloomberg Environmental Pillar',
            'Bloomberg Governance Pillar', 'Bloomberg Social Pillar',
            'S&P Global ESG Rank',
            'S&P Global Governance & Economic Dimension Rank',
            'S&P Global Environmental Dimension Rank',
            'S&P Global Social Dimension Rank',
            'Yahoo Finance ESG Score', 'Yahoo Finance Environmental Score',
            'Yahoo Finance Social Score', 'Yahoo Finance Governance Score']
fin_cols = ['Monthly Return', 'Price', 'Credit Risk Indicator', 'Beta', 'Alpha',
            'Issuer Default Risk', '30 Day Volatility', 'P/E Ratio',
            'Market Cap', 'Historical Market Cap', 'EPS']
company_cols = ['Ticker', 'GICS Sector', 'GICS Industry', 'GICS Industry Group',
                'GICS Sub-Industry']
other_cols = ['Date', 'Month', 'Year']
# pred_cols = ['Monthly Return', 'Model 1 Prediction', ...]  # TODO

# Description page
with description_tab:
  st.header('Description')
  st.markdown('''
  In this dashboard, we compare ESG scores from Bloomberg, S&P Global, and
  Yahoo Finance with market performance.
  
  We also compare the ESG scores to each other to see if they are correlated.
  The title of 
  ''')

  st.header('Usage')

  st.markdown('''
  Maybe replace this tab with readme.md?
  ''')

with report_tab:
  st.header('Report')

  # Load the report into markdown format
  with open('report.md', 'r') as f:
    report = f.read()

  # Expect ## to be max header found in report, add TOC
  headers = [
      h.replace('## ', '') for h in report.split('\n') if h.startswith('## ')]
  toc = st.expander('Table of Contents')
  with toc:
    for h in headers:
      st.markdown(f'- [{h}](#{h.lower().replace(" ", "-")})')

  # Add two header levels to the report and display it
  report = report.replace('# ', '## ')
  st.markdown(report)

# Relationship Model page
with relationship_tab:
  st.header('Relationship Model')
  # st.markdown('''
  # TODO: This page will show the relationship model.
  # ''')

  # Create columns
  select_col, display_col, desc_col = st.columns([1, 4, 1])
  # select_col, display_col = st.columns([2, 5])

  # Get user input
  with select_col:
    # Select whether to show at the company level or industry level
    st.subheader('Aggregation Level')
    agg_level = st.selectbox('Group By',
        ['Ticker','GICS Sector','GICS Industry','GICS Industry Group',
         'GICS Sub-Industry'])

    # Select which ESG score for X axis
    st.subheader('ESG Score')
    esg_x = st.selectbox('Select ESG Score', esg_cols)

    # Select which dates to use for analysis
    st.subheader('Date Range')
    start_date = pd.Timestamp(st.date_input(
        'Start Date', value=final_df['Date'].min()))
    end_date = pd.Timestamp(st.date_input(
        'End Date', value=final_df['Date'].max()))

    # Filter to show only groupbys in at least 12 months
    rel_df = final_df[final_df[agg_level].isin(
        final_df.groupby(agg_level).filter(lambda x: len(x) >= 12)[agg_level])]
    
    # Filter to show only dates in the selected range
    rel_df = rel_df[
        (rel_df['Date'] >= start_date) & (rel_df['Date'] <= end_date)]
    
    # Group by agg_level selector and average monthly return by market cap
    rel_df['Average Monthly Return'] = \
        rel_df['Monthly Return'] * rel_df['Market Cap']
    rel_df['Average Monthly Return'] = \
        rel_df.groupby(
            [agg_level, 'Date'])['Average Monthly Return'].transform('sum') / \
        rel_df.groupby([agg_level, 'Date'])['Market Cap'].transform('sum')
    
    # Create average market-weighted score for each agg_level
    rel_df[f'Average {esg_x}'] = rel_df[esg_x] * rel_df['Market Cap']
    rel_df[f'Average {esg_x}'] = \
        rel_df.groupby(
            ['GICS Sector', 'Date'])[f'Average {esg_x}'].transform('sum') / \
        rel_df.groupby(['GICS Sector', 'Date'])['Market Cap'].transform('sum')
    
    # Average both across all dates
    rel_df = rel_df.groupby([agg_level]) \
        .agg({'Average Monthly Return': 'mean', f'Average {esg_x}': 'mean'}) \
        .reset_index()
    
    # Select final sample
    if agg_level == 'GICS Sector':
      rel_df = rel_df[[
          f'Average {esg_x}','Average Monthly Return','GICS Sector']] \
          .drop_duplicates()
    else:
      # Join back Sector and select
      rel_df = rel_df.merge(final_df[[
          'GICS Sector',agg_level]].drop_duplicates(), on=agg_level, how='left')
      rel_df = rel_df[[
          agg_level,
          f'Average {esg_x}','Average Monthly Return','GICS Sector']] \
          .drop_duplicates()

  with display_col:
    st.subheader(f'Average Monthly Return vs. {esg_x} by {agg_level}')

    # Scatterplot
    with st.spinner('Updating plot...'):
      dist_fig = px.scatter(
          rel_df,
          x=f'Average {esg_x}',
          y='Average Monthly Return',
          trendline='ols',
          trendline_scope='overall', # TODO: show only one trendline for all
          trendline_color_override='black',
          hover_data=[agg_level],
          color='GICS Sector',)
      dist_fig.update_traces(marker=dict(opacity=0.4))
      dist_fig.update_layout(scattermode='group')

      st.plotly_chart(dist_fig, use_container_width=True, height=600)

  # Show desription below graph for wider columns
  with desc_col:
    st.subheader('Description')
    st.markdown('''
    This model displays the relationship between ESG scores and monthly returns.
    Scores and returns are aggregated by the average market-weighted value for
    each aggretation level, either by Ticker, GICS Industry, GICS Sub-Industry,
    GICS Industry Group, or GICS Sector.

    Dates can be filtered to any range, with the default range set to all dates
    in the dataset.
    ''')

  # Create columns for explanations and summary stats
  st.markdown('---')
  exp_col, stat_col = st.columns([1, 1])

  with exp_col:
    # Explain each ESG score
    st.subheader('Score Descriptions')
    st.markdown('''
    
    ''')

  with stat_col:
    # Show summary stats
    st.subheader('Summary Statistics')
    
    # Show summary stats
    st.write(rel_df.describe())

# Predictive Model page
with predictive_tab:
  st.header('Predictive Model')
  # st.markdown('''
  # TODO: This page will show the predictive model.
  # ''')

  # Create columns
  select_col, display_col, desc_col = st.columns([1, 3, 1])

  # Get user input
  with select_col:
    st.subheader('Select Industries')
    # Create checkbox for each industry, removing nan
    industries = final_df['GICS Sector'].unique()
    industries = industries[~pd.isna(industries)]
    selected_industry = st.selectbox(
        'Select Industry',
        industries)
    
    st.subheader('Smoothing')
    smoothing = st.slider(
        'Months to Smooth',
        min_value=0,
        max_value=12,
        value=6,
        step=1)
    
    # Filter to selected industries
    pred_df = final_df[final_df['GICS Sector'] == selected_industry]

  # Display the graph
  with display_col:
    st.subheader(f'Predicted Monthly Returns in {selected_industry}')
    # Sort by date
    pred_df = pred_df.sort_values(by='Date')

    # Create market weighted return by date, grouped by industry
    pred_df['Monthly Return'] = \
        pred_df['Monthly Return'] * pred_df['Market Cap']
    pred_df['Monthly Return'] = \
        pred_df.groupby([
            'GICS Sector', 'Date'])['Monthly Return'].transform('sum') / \
        pred_df.groupby(['GICS Sector', 'Date'])['Market Cap'].transform('sum')
    
    pred_df = pred_df[[
        'Date', 'Monthly Return', 'GICS Sector']].drop_duplicates()

    # Smooth the data
    if smoothing:
      pred_df['Monthly Return'] = \
          pred_df['Monthly Return'].rolling(smoothing).mean()

    # TODO simulating predictive model while waiting
    pred_df['Logistic Regression Prediction'] = pred_df['Monthly Return'] * 0.5

    # Pivot to long format
    pred_df_long = pred_df.melt(
        id_vars=['Date', 'GICS Sector'],
        value_vars=['Monthly Return', 'Logistic Regression Prediction'],
        var_name='Return Type',
        value_name='Return')

    # Line chart grouped by ticker
    with st.spinner('Updating plot...'):
      dist_fig = px.line(
          pred_df_long,
          x='Date',
          y='Return',
          color='Return Type',
          # line_dash='Return Type',
          hover_data='GICS Sector')
      dist_fig.update_traces(opacity=0.8)
      
      st.plotly_chart(dist_fig, use_container_width=True, height=600)
   
  # Display the description
  with desc_col:
    st.subheader('Description')
    st.markdown('''
    In this model, we display our predicted monthly returns for each industry
    against the actual monthly returns. The predicted returns are calculated
    ticker-by-ticker for each company in the S&P 500 at the end of each month,
    using a time-series based train test split. The predicted returns are then
    aggregated by GICS Industry and displayed against the actual monthly returns
    for each industry.
    ''')

  # Create cols to explain models and show summary stats
  st.markdown('---')
  exp_col, stats_col = st.columns([1, 1])
  
  # Show main descriptions under the graph
  with exp_col:
    st.subheader('Model Descriptions')
    st.markdown('''
    TODO: This model...
    ''')

  # Show summary stats under the graph
  with stats_col:
    st.subheader('Summary Statistics')

    # Show summary stats
    st.write(pred_df.describe())
  
  # Show ESG score details
  with correlation_tab:
    st.header('ESG Score Details')
    st.markdown('''
    This page shows the relationship between each set of ESG scores. Because
    the scores are calculated by different providers, the scores are not
    directly comparable. However, we should still see a relationship between
    the scores as they are all measuring similar underlying factors.
    ''')

    # Create heatmap of correlations
    st.subheader('Correlation Heatmap')
    st.markdown('''
    In the heatmap, we see that Bloomberg scores are most distinct from one
    another, while S&P Global and Yahoo Finance scores are very similar to other
    scores from the same source.  Yahoo Finance Governance and Yahoo Finance
    Environmental scores are the most similar to one another with a correlation
    of 0.94.

    While Bloomberg scores and S&P Global scores have weak positive correlations
    with one another, Yahoo Finance scores have a weak negative correlation with
    both Bloomberg and S&P Global scores.  The highest cross-source correlation
    is between Bloomberg Environmental and S&P Global Environmental scores at
    0.47.  The lowest cross-source correlation is between Yahoo Finance
    Environmental and Bloomberg ESG scores at -0.31.
    ''')

    with st.spinner('Updating plot...'):
      corr_df = final_df[esg_cols].corr()
      corr_fig = px.imshow(
          corr_df,
          x=corr_df.columns,
          y=corr_df.columns,
          color_continuous_scale='RdBu',
          zmin=-1,
          zmax=1)
      corr_fig.update_layout(height=600)
      st.plotly_chart(corr_fig, use_container_width=True)

    # Create interactive distribution plot
    dist_df = final_df.melt(
        id_vars=['Date', 'Ticker'],
        value_vars=esg_cols,
        var_name='ESG',
        value_name='Score')
    # Set the score Source
    dist_df['Source'] = dist_df['ESG'].apply(
        lambda x: 'Bloomberg' if 'Bloomberg' in x \
            else 'S&P Global' if 'S&P Global' in x \
            else 'Yahoo Finance' if 'Yahoo Finance' in x \
            else 'Unknown')
    dist_df = dist_df[dist_df['Source'] != 'Unknown']
    dist_df = dist_df.sort_values(by=['Source', 'ESG'])

    st.subheader('Distribution of ESG Scores')
    st.markdown('''
    Looking at the distribution of scores, we see that Bloomberg scores are more
    concentrated around the mean than S&P Global and Yahoo Finance scores.
    We also see that S&P Global Scores have a fairly uniform distribution while
    Yahoo Finance scores have bimodal distributions.
    ''')

    with st.spinner('Updating plot...'):
      dist_fig = px.histogram(
          dist_df,
          x='Score',
          color='Source',
          facet_col='ESG',
          facet_col_wrap=4,
          facet_row_spacing=0.16,
          facet_col_spacing=0.08,
      )
      dist_fig.for_each_yaxis(
          lambda y: y.update(showticklabels=True,matches=None))
      dist_fig.for_each_xaxis(
          lambda x: x.update(showticklabels=True,matches=None))
      for annotation in dist_fig.layout.annotations:
        annotation.text = annotation.text.split('=')[1]
        # Remove Bloomberg, S&P Global, and Yahoo Finance from the facet titles
        annotation.text = annotation.text.replace('Bloomberg ', '')
        annotation.text = annotation.text.replace('S&P Global ', '')
        annotation.text = annotation.text.replace('Yahoo Finance ', '')
      dist_fig.update_layout(height=800)

      st.plotly_chart(dist_fig, use_container_width=True)