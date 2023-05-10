import matplotlib.pyplot as plt
import os
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
import seaborn as sns
import streamlit as st
from plotly.subplots import make_subplots

from utils import *

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

# Set the title
st.title('ESG x Market Performance :earth_americas:')
st.markdown('''Nathan Alakija, Nicole ElChaar, Mason Otley, Xiaozhe Zhang''')

# Use three main tabs: Description, Relationship Model, and Predictive Model
tab_list = ['Description','ESG Metric Details','Relationship Model',
            'Predictive Model']
description_tab,correlation_tab,relationship_tab,predictive_tab = \
    st.tabs(tab_list)

final_df = get_final_df()

# Description page
with description_tab:
  show_description_tab()

# Relationship Model page
with relationship_tab:
  st.header('Relationship Model')

  # Create columns
  select_col, display_col, desc_col = st.columns([1, 4, 1])

  # Get user input
  with select_col:
    # Select whether to show at the company level or industry level
    st.subheader('Aggregation Level')
    agg_level = st.selectbox('Group By',
        ['Ticker','GICS Sector','GICS Industry','GICS Industry Group',
         'GICS Sub-Industry'])

    # Select which ESG score for X axis
    st.subheader('ESG Metric')
    esg_x = st.selectbox('Select ESG Metric', esg_cols)

    # Select which dates to use for analysis
    st.subheader('Date Range')
    start_date = pd.Timestamp(st.date_input(
        'Start Date', value=final_df['Date'].min()))
    end_date = pd.Timestamp(st.date_input(
        'End Date', value=final_df['Date'].max()))

    # Get the filtered, market-cap scores, computing only on date change
    rel_df = get_rel_df(final_df, start_date, end_date) 

    # Aggregate by agg_level selector and average monthly return by market cap
    rel_df = get_rel_df_agg(rel_df, agg_level, esg_x)

  with display_col:
    st.subheader(f'Average Monthly Return vs. {esg_x} by {agg_level}')

    # Scatterplot
    with st.spinner('Updating plot...'):
      dist_fig = px.scatter(
          rel_df,
          x=f'Average {esg_x}',
          y='Average Monthly Return',
          trendline='ols',
          trendline_scope='overall',
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
    This model displays the relationship between ESG metrics and monthly
    returns.  Metrics and returns are aggregated by the average market-weighted
    value for each aggregation level, either by Ticker, GICS Industry, GICS
    Sub-Industry, GICS Industry Group, or GICS Sector.

    Dates can be filtered to any range, with the default range set to all dates
    in the dataset.
    ''')

  # Create columns for explanations and summary stats
  st.markdown('---')
  exp_col, stat_col = st.columns([1, 1])

  with exp_col:
    # Explain each ESG score
    st.subheader('ESG Metric Descriptions')
    st.markdown('''
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
    ''')

  with stat_col:
    # Show summary stats
    st.subheader('Summary Statistics')
    
    # Show summary stats
    st.write(rel_df.describe())

# Predictive Model page
with predictive_tab:
  st.header('Predictive Model')

  # Create columns
  select_col, display_col, desc_col = st.columns([1, 3, 1])

  # Get user input
  with select_col:
    st.subheader('Select Industry')
    # Create checkbox for each industry, removing nan
    industries = final_df['GICS Sector'].unique()
    industries = industries[~pd.isna(industries)].tolist()
    industries.append('All Industries')
    industries.sort()
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
    if selected_industry == 'All Industries':
      pred_df = final_df
    else:
      pred_df = final_df[final_df['GICS Sector'] == selected_industry]

  # Display the graph
  with display_col:
    st.subheader(f'Predicted Monthly Returns in {selected_industry}')
    # Sort by date
    pred_df = pred_df.sort_values(by='Date')

    # Create market weighted return by date, grouped by industry
    pred_df['Monthly Return'] = \
        pred_df['Monthly Return'] * pred_df['Market Cap']
    pred_df['Lasso Model Return'] = \
        pred_df['Lasso Model'] * pred_df['Market Cap']
    if selected_industry == 'All Industries':
      pred_df['Monthly Return'] = \
          pred_df.groupby(['Date'])['Monthly Return'].transform('sum') / \
          pred_df.groupby(['Date'])['Market Cap'].transform('sum')
      pred_df['Lasso Model Return'] = \
          pred_df.groupby(['Date'])['Lasso Model Return'].transform('sum') / \
          pred_df.groupby(['Date'])['Market Cap'].transform('sum')
    else:
      pred_df['Monthly Return'] = \
          pred_df.groupby([
              'GICS Sector', 'Date'])['Monthly Return'].transform('sum') / \
          pred_df.groupby(['GICS Sector','Date'])['Market Cap'].transform('sum')
      pred_df['Lasso Model Return'] = \
          pred_df.groupby([
              'GICS Sector', 'Date'])['Lasso Model Return'].transform('sum') / \
          pred_df.groupby(['GICS Sector','Date'])['Market Cap'].transform('sum')
    
    # Drop duplicates
    pred_df = pred_df[[
        'Date', 'Monthly Return','Lasso Model Return']].drop_duplicates()

    # Smooth the data
    if smoothing:
      pred_df['Monthly Return'] = \
          pred_df['Monthly Return'].rolling(smoothing).mean()
      pred_df['Lasso Model Return'] = \
          pred_df['Lasso Model Return'].rolling(smoothing).mean()

    # Winsorize
    top_5 = pred_df['Lasso Model Return'].quantile(0.99)
    bottom_5 = pred_df['Lasso Model Return'].quantile(0.01)
    pred_df['Lasso Model Return'] = \
        pred_df['Lasso Model Return'].clip(bottom_5, top_5)    

    # Pivot to long format
    pred_df_long = pred_df.melt(
        id_vars=['Date'],
        value_vars=['Monthly Return', 'Lasso Model Return'],
        var_name='Return Type',
        value_name='Return')

    # Line chart grouped by ticker
    with st.spinner('Updating plot...'):
      dist_fig = px.line(
          pred_df_long,
          x='Date',
          y='Return',
          color='Return Type',
          # line_dash='Return Type'
          )
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
    # TODO how sad
    st.markdown('''
    The simple Lasso model uses lagging ESG scores and economic indicators to
    predict the next month's return.  We see that the model performs very poorly
    in predicting the next month's return, assuming returns are mostly random
    with an average predicted value less than the absolute value of 1%.
    ''')

  # Show summary stats under the graph
  with stats_col:
    st.subheader('Summary Statistics')

    # Show summary stats
    st.write(pred_df.describe())
  
  # Show ESG score details
  with correlation_tab:
    show_correlation_tab(final_df)
