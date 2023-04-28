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
# company_info_path = input_path + 'company_info.csv'
# company_themes_path = input_path + 'company_themes.csv'
# monthly_returns_path = input_path + 'monthly_returns.csv'

# # Import the ESG Data
# company_info = pd.read_csv(company_info_path)
# company_themes = pd.read_csv(company_themes_path)
# monthly_returns = pd.read_csv(monthly_returns_path)

# Load in final dataset
final_df = pd.read_csv(input_path + 'final_dataset.csv')

# Set the title
st.title('ESG Dashboard')
st.markdown('''Nathan Alakija, Nicole ElChaar, Mason Otley, Xiaozhe Zhang''')

# Use three main tabs: Description, Relationship Model, and Predictive Model
tab_list = ['Description', 'Report', 'Relationship Model', 'Predictive Model']
description_tab, report_tab, relationship_tab, predictive_tab = \
    st.tabs(tab_list)
    # st.tabs([s.center(25, '\u2001') for s in tab_list])

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
  select_col, display_col, desc_col = st.columns([1, 3, 1])

  # # Join the company info and returns
  # company_returns = monthly_returns.merge(company_info, on='CIK')

  # Get user input
  with select_col:
    # Select whether to show at the company level or industry level
    st.subheader('Aggregation Level')
    agg_level = st.radio('Group By', ['Ticker', 'Sector'])

    # Select which ESG score for X axis
    st.subheader('ESG Score')
    option_list = ['ESG Score','ESG Rank','MCSI ESG Rating','BESG Score','ESG Score SYN','YFin E','YFin S','YFin G']
    esg_x = st.radio('Select ESG Score', option_list)

    # Filter to show only groupbys in at least 12 months
    rel_df = final_df[final_df[agg_level].isin(
        final_df.groupby(agg_level).filter(lambda x: len(x) >= 12)[agg_level])]
    # Select columns needed
    if agg_level == 'Sector':
      print('Sector')
      print('esg_x', esg_x)
      if esg_x == 'MCSI ESG Rating':
        # TODO Aggregate returns by Sector and Rating
        # Assign ratings to scores
        rel_df[esg_x] = rel_df[esg_x].replace({
            'AAA': 10,
            'AA': 9,
            'A': 8,
            'BBB': 7,
            'BB': 6,
            'B': 5,
            'CCC': 4,
            'CC': 3,
            'C': 2,
            'D': 1,
        })
        # Create average market-weighted return for each sector
        rel_df[esg_x] = rel_df[esg_x] * rel_df['Market Cap']
        rel_df[esg_x] = \
            rel_df.groupby(['Sector', 'Date'])[esg_x].transform('sum') / \
            rel_df.groupby(['Sector', 'Date'])['Market Cap'].transform('sum')
        # Transform back to ratings
        rel_df[esg_x] = rel_df[esg_x].round().replace({
            10: 'AAA',
            9: 'AA',
            8: 'A',
            7: 'BBB',
            6: 'BB',
            5: 'B',
            4: 'CCC',
            3: 'CC',
            2: 'C',
            1: 'D',
        })
        # Rename industry return to return
        rel_df = rel_df \
            .drop(columns=['Average Return']) \
            .rename(columns={'Average Sector Return': 'Average Return'})
      else:
        # Create average market-weighted return for each sector
        rel_df[f'Average {esg_x}'] = rel_df[esg_x] * rel_df['Market Cap']
        rel_df[f'Average {esg_x}'] = \
            rel_df.groupby(['Sector', 'Date'])[f'Average {esg_x}'].transform('sum') / \
            rel_df.groupby(['Sector', 'Date'])['Market Cap'].transform('sum')

        # Rename industry return to return
        rel_df = rel_df \
            .drop(columns=['Average Return', esg_x]) \
            .rename(columns={'Average Sector Return': 'Average Return', f'Average {esg_x}': esg_x})

      rel_df = rel_df[[agg_level, esg_x, 'Average Return']]
    else:
      rel_df = rel_df[[agg_level, esg_x, 'Average Return', 'Sector']]

  with display_col:
    st.subheader(f'{agg_level} Monthly Return vs. {esg_x}')
    if agg_level == 'Sector':
      # Boxplot
      fig = px.box(
          rel_df,
          x=esg_x,
          y='Average Return',
          hover_data=[agg_level],
          color='Sector',
          width=800,)

    else:
      # Scatterplot
      fig = px.scatter(
          rel_df,
          x=esg_x,
          y='Average Return',
          trendline='ols', # TODO: show only one trendline for all
          trendline_scope='overall',
          trendline_color_override='black',
          hover_data=[agg_level],
          color='Sector')
      fig.update_layout(scattermode='group')

    if esg_x == 'MCSI ESG Rating':
      fig.update_xaxes(
          categoryorder='array',
          categoryarray=['AAA', 'AA', 'A', 'BBB', 'BB', 'B', 'CCC', 'CC', 'CCC', 'D'])
    
    st.plotly_chart(fig)

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

  
  # Display summary stats
  st.subheader('Summary Statistics')
  # st.text(f'Number of Companies: {len(rel_df)}')
  # st.dataframe(rel_df[[esg_x, 'Average Return']].describe())
  # st.text('Correlation')
  # st.dataframe(rel_df[[esg_x, 'Average Return']].corr())
  # st.text('Covariance')
  # st.dataframe(rel_df[[esg_x, 'Average Return']].cov())
  # st.text('Skewness')
  # st.dataframe(rel_df[[esg_x, 'Average Return']].skew())
  # st.text('Kurtosis')
  # st.dataframe(rel_df[[esg_x, 'Average Return']].kurtosis())

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
