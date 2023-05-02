import matplotlib.pyplot as plt
import os
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import seaborn as sns
import streamlit as st

# Usage:
# streamlit run app.py

# Make page content wider
st.set_page_config(layout='wide')

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
st.title('ESG Dashboard')
st.markdown('''Nathan Alakija, Nicole ElChaar, Mason Otley, Xiaozhe Zhang''')

# Use three main tabs: Description, Relationship Model, and Predictive Model
tab_list = ['Description', 'Report', 'Relationship Model', 'Predictive Model']
description_tab, report_tab, relationship_tab, predictive_tab = \
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
            'S&P Global ESG Rank', 'S&P Global Governance & Economic Dimension Rank',
            'S&P Global Environmental Dimension Rank', 'S&P Global Social Dimension Rank',
            'Yahoo Finance ESG Score', 'Yahoo Finance Environmental Score',
            'Yahoo Finance Social Score', 'Yahoo Finance Governance Score']
fin_cols = ['Monthly Return', 'Price', 'Credit Risk Indicator', 'Beta', 'Alpha',
            'Issuer Default Risk', '30 Day Volatility', 'P/E Ratio', 'Market Cap',
            'Historical Market Cap', 'EPS']
company_cols = ['Ticker', 'GICS Sector', 'GICS Industry', 'GICS Industry Group',
                'GICS Sub-Industry']
other_cols = ['Date', 'Month', 'Year']
# pred_cols = ['Monthly Return', 'Model 1 Prediction', 'Model 2 Prediction', ...] # TODO

# Description page
with description_tab:
  st.header('Description')
  st.markdown('''
  TODO: This page will describe the relationship between ESG scores and stock returns.
  
  The Report, Relationship Model, Predictive Model...
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
  headers = [h.replace('## ', '') for h in report.split('\n') if h.startswith('## ')]
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
  st.markdown('''
  TODO: This page will show the relationship model.
  ''')

  # Create columns
  select_col, display_col, desc_col = st.columns([1, 4, 1])
  # select_col, display_col = st.columns([2, 5])

  # Get user input
  with select_col:
    # Select whether to show at the company level or industry level
    st.subheader('Aggregation Level')
    agg_level = st.selectbox('Group By', ['Ticker', 'GICS Sector', 'GICS Industry','GICS Industry Group','GICS Sub-Industry']) # GICS Sector Name,GICS Industry Name,GICS Industry Group Name,GICS Sub-Industry Name

    # Select which ESG score for X axis
    st.subheader('ESG Score')
    esg_x = st.selectbox('Select ESG Score', esg_cols)

    # Select which dates to use for analysis
    st.subheader('Date Range')
    start_date = pd.Timestamp(st.date_input('Start Date', value=final_df['Date'].min()))
    end_date = pd.Timestamp(st.date_input('End Date', value=final_df['Date'].max()))

    # Filter to show only groupbys in at least 12 months
    rel_df = final_df[final_df[agg_level].isin(
        final_df.groupby(agg_level).filter(lambda x: len(x) >= 12)[agg_level])]
    
    # Filter to show only dates in the selected range
    rel_df = rel_df[(rel_df['Date'] >= start_date) & (rel_df['Date'] <= end_date)]
    
    # Group by agg_level selector and average monthly return by market cap
    rel_df['Average Monthly Return'] = rel_df['Monthly Return'] * rel_df['Market Cap']
    rel_df['Average Monthly Return'] = \
        rel_df.groupby([agg_level, 'Date'])['Average Monthly Return'].transform('sum') / \
        rel_df.groupby([agg_level, 'Date'])['Market Cap'].transform('sum')
    
    # Create average market-weighted score for each agg_level
    rel_df[f'Average {esg_x}'] = rel_df[esg_x] * rel_df['Market Cap']
    rel_df[f'Average {esg_x}'] = \
        rel_df.groupby(['GICS Sector', 'Date'])[f'Average {esg_x}'].transform('sum') / \
        rel_df.groupby(['GICS Sector', 'Date'])['Market Cap'].transform('sum')
    
    # Average both across all dates
    rel_df = rel_df.groupby([agg_level]) \
        .agg({'Average Monthly Return': 'mean', f'Average {esg_x}': 'mean'}) \
        .reset_index()
    
    # Select final sample
    if agg_level == 'GICS Sector':
      rel_df = rel_df[[f'Average {esg_x}', 'Average Monthly Return', 'GICS Sector']].drop_duplicates()
    else:
      # Join back Sector and select
      rel_df = rel_df.merge(final_df[['GICS Sector', agg_level]].drop_duplicates(), on=agg_level, how='left')
      rel_df = rel_df[[agg_level, f'Average {esg_x}', 'Average Monthly Return', 'GICS Sector']].drop_duplicates()

  with display_col:
    st.subheader(f'Average Monthly Return vs. {esg_x} by {agg_level}')

    # Scatterplot
    fig = px.scatter(
        rel_df,
        x=f'Average {esg_x}',
        y='Average Monthly Return',
        trendline='ols',
        trendline_scope='overall', # TODO: show only one trendline for all
        trendline_color_override='black',
        hover_data=[agg_level],
        color='GICS Sector',)
    fig.update_traces(marker=dict(opacity=0.4))
    fig.update_layout(scattermode='group')

    st.plotly_chart(fig, use_container_width=True, height=600)

  # Show desription below graph for wider columns
  with desc_col:
    st.subheader('Description')
    st.markdown('''
    This model displays the relationship between ESG scores and monthly returns.
    Scores and returns are aggregated by the average market-weighted value for
    each aggretation level, either by Ticker, GICS Industry, GICS Sub-Industry,
    GICS Industry Group, or GICS Sector.

    Dates can be filtered to any range, with the default range showing all dates
    in the dataset.
    ''')

  # Explain each ESG score
  st.subheader('ESG Scores')
  st.markdown('''
  #### ESG 1
  TODO: This column will describe ESG 1.
  ''')
  st.markdown('''
  #### ESG 2
  TODO: This column will describe ESG 2.
  ''')
  st.markdown('''
  #### ESG 3
  TODO: This column will describe ESG 3.
  ''')

  
  # Display summary stats
  # st.subheader('Summary Statistics')
  # st.text(f'Number of Companies: {len(rel_df)}')
  # st.dataframe(rel_df[[esg_x, 'Monthly Return']].describe())
  # st.text('Correlation')
  # st.dataframe(rel_df[[esg_x, 'Monthly Return']].corr())
  # st.text('Covariance')
  # st.dataframe(rel_df[[esg_x, 'Monthly Return']].cov())
  # st.text('Skewness')
  # st.dataframe(rel_df[[esg_x, 'Monthly Return']].skew())
  # st.text('Kurtosis')
  # st.dataframe(rel_df[[esg_x, 'Monthly Return']].kurtosis())

# Predictive Model page
with predictive_tab:
  st.header('Predictive Model')
  st.markdown('''
  TODO: This page will show the predictive model.
  ''')

  # # Create columns
  # select_col, display_col, desc_col = st.columns([1, 3, 1])

  # # Get user input
  # with select_col:
  #   st.subheader('Select Companies')
  #   # Separate div for scrolling
  #   scroll_div = st.container()
  #   with scroll_div:
  #     # Add checkbox to select all
  #     select_all = st.checkbox('Select All', value=True)

  #     # Create checkbox for each company
  #     company_list = zip(
  #         company_info['company_name'].tolist(), company_info['CIK'].tolist())
  #     company_checkbox_dict = {
  #         cik: st.checkbox(f"{name}", value=select_all) for name, cik in company_list}
  #     selected_companies = [
  #         cik for cik, selected in company_checkbox_dict.items() if selected]

  # # Display the graph
  # with display_col:
  #   st.header('Monthly Returns')
  #   if not selected_companies:
  #     st.markdown('Select companies to see their returns.')
  #   company_returns = monthly_returns[monthly_returns['CIK'].isin(selected_companies)].merge(company_info, on='CIK')
  #   st.line_chart(company_returns.groupby(['date', 'company_name'])['ret'].sum().unstack())

  # # Display the description
  # with desc_col:
  #   st.subheader('Description')
  #   st.divider()
  #   st.subheader('Interpretation')
  
  # # Show main descriptions under the graph
  # st.subheader('Description')
  # st.markdown('''
  # TODO: The predictive model...
  # ''')
