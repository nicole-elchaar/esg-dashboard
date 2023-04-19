import matplotlib.pyplot as plt
import os
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import seaborn as sns
import streamlit as st

# disable vegalite warning
st.set_option('deprecation.showPyplotGlobalUse', False)

# Usage:
# streamlit run app.py

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

# Make page content wider
st.set_page_config(layout='wide')

# Set the title
st.title('ESG Dashboard')
st.markdown('''Nathan Alakija, Nicole ElChaar, Mason Otley, Xiaozhe Zhang''')

# Use three main tabs: Description, Relationship Model, and Predictive Model
list_tabs = ['Description', 'Relationship Model', 'Predictive Model', 'Time Series EXAMPLE']
description_tab, relationship_tab, predictive_tab, time_series_tab = \
    st.tabs([s.center(25, '\u2001') for s in list_tabs])

# Description page
with description_tab:
  st.header('Description')
  st.markdown('''
  TODO: This page will describe the relationship between ESG scores and stock returns.
  ''')

  # Set up table of contents and report
  toc = st.expander('Table of Contents')
  with toc:
    st.markdown('''
    - [Introduction](#introduction)
    - [Data](#data)
    - [Methodology](#methodology)
    - [Results](#results)
    - [Conclusion](#conclusion)
    ''')


  st.markdown('''
  ### Introduction


  ### Data


  ### Methodology


  ### Results


  ### Conclusion


  ''')

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
  # print(company_returns)

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

  # Join the company info and returns
  company_returns = monthly_returns.merge(company_info, on='CIK')
  # print(company_returns)

  # Get user input
  with select_col:
    # Select model to display
    st.subheader('Model')
    option_list = ['Model 1', 'Model 2', 'Model 3']
    model_checkbox_dict = {option: st.checkbox(f"{option}", value=True) for option in option_list}
    selected_models = [option for option, selected in model_checkbox_dict.items() if selected]

    # Choose range of ESG score to use
    # Find the minimum of all selected and maximum of all selected models
    min_esg = min([company_info[f'esg{model.split()[1]}'].min() for model in selected_models])
    max_esg = max([company_info[f'esg{model.split()[1]}'].max() for model in selected_models])
    # Create a slider
    st.subheader('ESG Range')
    esg_range = st.slider('ESG Score', min_esg, max_esg, (min_esg, max_esg))
    print(esg_range)

    # Filter the company info by the selected ESG score range
    company_returns_filtered = company_returns[
        (company_returns['esg1'] >= esg_range[0]) & (company_returns['esg1'] <= esg_range[1])]

  # Display the graph
  with display_col:
    # X axis as ESG score
    # Y axis as stock return
    # Color as model
    # Size as number of companies
    # Heatmap
    st.header('ESG Score vs. Stock Return')
    if not selected_models:
      st.markdown('Select models to see their results.')

    # # Create and display the graph with Matplotlib
    # fig, ax = plt.subplots()
    # for model in selected_models:
    #   ax.scatter(data=company_returns, x='esg1', y=f'pred_ret{model.split()[1]}')
    # ax.set_xlabel('ESG Score')
    # ax.set_ylabel('Stock Return')
    # ax.legend(selected_models)
    # st.pyplot(fig)

    # # Create and display the graph with Seaborn
    # fig, ax = plt.subplots()
    # for model in selected_models:
    #   sns.regplot(data=company_returns, x='esg1', y=f'pred_ret{model.split()[1]}',
    #               scatter_kws={'alpha': 0.2})
    # ax.set_xlabel('ESG Score')
    # ax.set_ylabel('Stock Return')
    # ax.legend(selected_models)
    # st.pyplot(fig)
    
    # # Create and display the graph with Plotly Figure Factory
    # fig = ff.create_2d_density(x=company_returns['esg1'], y=company_returns['pred_ret1'])
    # # add axis labels
    # fig.update_layout(
    #     xaxis_title='ESG Score',
    #     yaxis_title='Stock Return',
    #     # title='ESG Score vs. Stock Return Density Plot',
    # )
    # st.plotly_chart(fig)

    # Create and display the graph with Plotly Express
    # Create a plot and regression line for each model
    # for model in selected_models:
    alpha = 0.3
    color_dict = {
        'ret': f'rgba(180, 180, 180, {alpha})',
        'pred_ret1': f'rgba(180, 0, 0, {alpha})',
        'pred_ret2': f'rgba(0, 180, 0, {alpha})',
        'pred_ret3': f'rgba(0, 0, 180, {alpha})'}
    fig = px.scatter(
        company_returns_filtered,
        x='esg1',
        y=['ret'] + [f'pred_ret{model.split()[1]}' for model in selected_models],
        trendline='ols',
        color_discrete_map=color_dict)
    # Add axis labels
    fig.update_layout(
        xaxis_title='ESG Score',
        yaxis_title='Stock Return',
        # title='ESG Score vs. Stock Return',
    )
    st.plotly_chart(fig)

  with desc_col:
    st.header('Description')
    st.markdown('''
    This graph shows the relationship between ESG score and stock return. Each model is represented by a different color.
    ''')

    with st.container():
      st.subheader('Model 1')
      st.markdown('''TODO: Describe model 1''')
    with st.container():
      st.subheader('Model 2')
      st.markdown('''TODO: Describe model 2''')
    with st.container():
      st.subheader('Model 3')
      st.markdown('''TODO: Describe model 3''')

# Time Series EXAMPLE
with time_series_tab:
  st.header('Time Series EXAMPLE')
  st.markdown('''This is an example of a time series plot. It shows the monthly returns of the selected companies.''')

  # Create columns
  select_col, display_col, desc_col = st.columns([1, 3, 1])
  
  # Get user input
  with select_col:
    st.subheader('Select Companies')
    toggle_select_all = st.empty()
    company_list = zip(company_info['company_name'].tolist(), company_info['CIK'].tolist())
    company_checkbox_dict = {cik: st.checkbox(f"{name}") for name, cik in company_list}
    selected_companies = [cik for cik, selected in company_checkbox_dict.items() if selected]

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

# # Sidebar
# with st.sidebar:
#     st.header('Select Companies')
#     company_list = zip(company_info['company_name'].tolist(), company_info['CIK'].tolist())
#     company_checkbox_dict = {cik: st.checkbox(f"{name}") for name, cik in company_list}
#     selected_companies = [cik for cik, selected in company_checkbox_dict.items() if selected]

# # Set up the main page
# st.title('ESG Dashboard')

# Display the list of companies as options in the sidebar (multiselect)
# st.sidebar.header('Select Companies')

# state = st.sidebar.selectbox('Select State', company_info['state'].unique())

# # If button is clicked, select all or none
# if st.sidebar.button('**Select all**', key='select_all'):
#     selected_companies = {cik: True for cik in company_info['CIK'].tolist()}
# elif st.sidebar.button('**Select none**', key='select_none'):
#     selected_companies = {cik: False for cik in company_info['CIK'].tolist()}


# Add a checkbox for each company
# company_list = zip(company_info['company_name'].tolist(), company_info['CIK'].tolist())
# company_checkbox_dict = {cik: st.sidebar.checkbox(f"{name}") for name, cik in company_list}
# selected_companies = [cik for cik, selected in company_checkbox_dict.items() if selected]



# Based on the selected companies, group by CIK, then plot date vs. returns
# # Show line plot whether any are selected or not
# st.header('Monthly Returns')
# company_returns = monthly_returns[monthly_returns['CIK'].isin(selected_companies)].merge(company_info, on='CIK')

# st.line_chart(company_returns.groupby(['date', 'company_name'])['ret'].sum().unstack())
