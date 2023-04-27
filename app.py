import matplotlib.pyplot as plt
import os
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import seaborn as sns
import streamlit as st

# Usage:
# streamlit run app.py

# # disable vegalite warning
# st.set_option('deprecation.showPyplotGlobalUse', False)
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
output_path = 'output/'
company_info_path = input_path + 'company_info.csv'
company_themes_path = input_path + 'company_themes.csv'
monthly_returns_path = input_path + 'monthly_returns.csv'

# Import the ESG Data
company_info = pd.read_csv(company_info_path)
company_themes = pd.read_csv(company_themes_path)
monthly_returns = pd.read_csv(monthly_returns_path)

# Set the title
st.title('ESG Dashboard')
st.markdown('''Nathan Alakija, Nicole ElChaar, Mason Otley, Xiaozhe Zhang''')

# Use three main tabs: Description, Relationship Model, and Predictive Model
tab_list = ['Description', 'Report', 'Relationship Model', 'Predictive Model']
description_tab, report_tab, relationship_tab, predictive_tab = \
    st.tabs([s.center(25, '\u2001') for s in tab_list])
    # st.tabs(tab_list)

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

  # Add two header levels to the report
  report = report.replace('# ', '## ')

  # Expect ## to be max header found in report, add TOC
  headers = [h.replace('### ', '') for h in report.split('\n') if h.startswith('### ')]
  toc = st.expander('Table of Contents')
  with toc:
    for h in headers:
      st.markdown(f'- [{h}](#{h.lower().replace(" ", "-")})')

  # toc = st.expander('Table of Contents')
  # with toc:
  #   st.markdown('''
  #   - [Introduction](#introduction)
  #   - [Data](#data)
  #   - [Methodology](#methodology)
  #   - [Results](#results)
  #   - [Conclusion](#conclusion)
  #   ''')

  st.markdown(report)

# Relationship Model page
with relationship_tab:
  st.header('Relationship Model')
  st.markdown('''
  TODO: This page will show the relationship model.
  ''')

  # Create columns
  select_col, display_col, desc_col = st.columns([1, 3, 1])

  # Join the company info and returns
  company_returns = monthly_returns.merge(company_info, on='CIK')

  # Get user input
  with select_col:
    # Select model to display
    st.subheader('ESG Score')
    option_list = ['ESG 1', 'ESG 2', 'ESG 3']
    
    # Single select
    option = st.selectbox('Select ESG Score', option_list)
    
    # Set range of ESG score to use
    # Find the minimum of all selected and maximum of all selected models
    min_esg = company_info[f'esg{option.split()[1]}'].min()
    max_esg = company_info[f'esg{option.split()[1]}'].max()
    # Create a slider
    st.subheader('ESG Range')
    esg_range = st.slider('ESG Score', min_esg, max_esg, (min_esg, max_esg))
    
    # Filter the company info by the selected ESG score range
    company_returns_filtered = company_returns[
        (company_returns[f'esg{option.split()[1]}'] >= esg_range[0]) & (company_returns[f'esg{option.split()[1]}'] <= esg_range[1])]
    
  with display_col:
    # Display the graph with plotly
    st.subheader('ESG Score vs. Stock Return')
    fig = px.scatter(
        company_returns_filtered,
        x=f'esg{option.split()[-1]}',
        y='ret',
        trendline='ols')
    st.plotly_chart(fig)

    # Display summary stats
    st.subheader('Summary Statistics')
    st.dataframe(company_returns_filtered[['market_cap', f'esg{option.split()[1]}', 'ret']].describe())
    st.dataframe(company_returns_filtered[[f'esg{option.split()[1]}', 'ret']].corr())
    st.dataframe(company_returns_filtered[[f'esg{option.split()[1]}', 'ret']].cov())
    st.dataframe(company_returns_filtered[[f'esg{option.split()[1]}', 'ret']].skew())
    st.dataframe(company_returns_filtered[[f'esg{option.split()[1]}', 'ret']].kurtosis())
    st.dataframe(company_returns_filtered.describe())

  with desc_col:
    st.subheader('Description')
    st.markdown('''TODO: This column will describe the graph.''')
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

    with st.container():
      st.subheader('Interpretation')
      st.markdown('''TODO: This column will describe the metrics of the graph.''')
      st.dataframe(company_returns_filtered[f'esg{option.split()[1]}'].describe())

# Predictive Model page
with predictive_tab:
  st.header('Predictive Model')
  st.markdown('''
  TODO: This page will show the predictive model.
  ''')

  # Create columns
  select_col, display_col, desc_col = st.columns([1, 3, 1])

  # Get user input
  with select_col:
    st.subheader('Select Companies')
    # Separate div for scrolling
    scroll_div = st.container()
    with scroll_div:
      # Add checkbox to select all
      select_all = st.checkbox('Select All', value=True)

      # Create checkbox for each company
      company_list = zip(
          company_info['company_name'].tolist(), company_info['CIK'].tolist())
      company_checkbox_dict = {
          cik: st.checkbox(f"{name}", value=select_all) for name, cik in company_list}
      selected_companies = [
          cik for cik, selected in company_checkbox_dict.items() if selected]

  # Display the graph
  with display_col:
    st.header('Monthly Returns')
    if not selected_companies:
      st.markdown('Select companies to see their returns.')
    company_returns = monthly_returns[monthly_returns['CIK'].isin(selected_companies)].merge(company_info, on='CIK')
    st.line_chart(company_returns.groupby(['date', 'company_name'])['ret'].sum().unstack())

  # Display the description
  with desc_col:
    st.subheader('Description')
    st.divider()
    st.subheader('Interpretation')
  
  # Show main descriptions under the graph
  st.subheader('Description')
  st.markdown('''
  TODO: The predictive model...
  ''')
