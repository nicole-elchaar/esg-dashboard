# Usage:
# streamlit run app.py

import streamlit as st
from utils import get_final_df, show_description_tab, show_correlation_tab, \
    show_relationship_tab, show_predictive_tab

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

# Store the final df for manipulation across all tabs
final_df = get_final_df()

# Description page
with description_tab:
  show_description_tab()

# Show ESG score details
with correlation_tab:
  show_correlation_tab(final_df)

# Relationship Model page
with relationship_tab:
  show_relationship_tab(final_df)

# Predictive Model page
with predictive_tab:
  show_predictive_tab(final_df)