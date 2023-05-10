# Cached utils for the dashboard
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

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
pred_cols = ['Monthly Return', 'Lasso Model']  # TODO: Use, add more

# Load in final dataset
@st.cache_data
def get_final_df():
  # Load in final dataset
  final_df = pd.read_csv('inputs/final_dataset.csv')
  final_df['Date'] = pd.to_datetime(final_df['Date'])

  # Remove extreme outliers in monthly return > 99% and < 1%
  top_5 = final_df['Monthly Return'].quantile(0.99)
  bottom_5 = final_df['Monthly Return'].quantile(0.01)
  final_df = final_df[final_df['Monthly Return'] < top_5]
  final_df = final_df[final_df['Monthly Return'] > bottom_5]
  
  return final_df

# Cache filtered dataset
@st.cache_data
def get_rel_df(final_df, start_date, end_date):
  # Filter to show only dates in the selected range
  rel_df = final_df[
      (final_df['Date'] >= start_date) & (final_df['Date'] <= end_date)]
  
  # Multiply to get numerator for weighted average
  cap_esg_labels = [f'Cap {esg}' for esg in esg_cols]
  rel_df[cap_esg_labels] = \
      rel_df[esg_cols].multiply(rel_df['Market Cap'], axis=0)
  rel_df['Cap Monthly Return'] = \
      rel_df['Monthly Return'] * rel_df['Market Cap']
  
  return rel_df

# Aggregate by agg_level and ESG score, TODO no real reason to cache
@st.cache_data
def get_rel_df_agg(rel_df, agg_level, esg_x):
  # Average by agg_level
  rel_df['Average Monthly Return'] = \
      rel_df.groupby(
          [agg_level, 'Date'])['Cap Monthly Return'].transform('sum') / \
      rel_df.groupby([agg_level, 'Date'])['Market Cap'].transform('sum')
  
  # Create average market-weighted score for each agg_level
  rel_df[f'Average {esg_x}'] = \
      rel_df.groupby(
          [agg_level, 'Date'])[f'Cap {esg_x}'].transform('sum') / \
      rel_df.groupby([agg_level, 'Date'])['Market Cap'].transform('sum')

  # Aggregate and select columns
  if agg_level == 'GICS Sector':
    rel_df = rel_df.groupby([agg_level]) \
        .agg({'Average Monthly Return': 'mean', f'Average {esg_x}': 'mean'}) \
        .reset_index() \
        .drop_duplicates()
  else:
    rel_df = rel_df.groupby([agg_level]) \
        .agg({
            'Average Monthly Return': 'mean',
            f'Average {esg_x}': 'mean',
            'GICS Sector': 'first'}) \
        .reset_index() \
        .drop_duplicates()
  
  return rel_df

# Cache description tab
@st.cache_data
def show_description_tab():
  # Load the README into markdown format
  with open('README.md', 'r') as f:
    report = f.read()

  # Show only ## headers for TOC
  headers = [
      h.replace('## ', '') for h in report.split('\n') if h.startswith('## ')]
  toc = st.expander('Table of Contents')
  with toc:
    for h in headers:
      st.markdown(f'- [{h}](#{h.lower().replace(" ", "-")})')

  # Add two header levels to the report and display it
  report = report.replace('# ', '## ')
  st.markdown(report)

@st.cache_data
def get_corr_fig(final_df):
  corr_df = final_df[esg_cols].corr()
  corr_fig = px.imshow(
      corr_df,
      x=corr_df.columns,
      y=corr_df.columns,
      color_continuous_scale='RdBu',
      zmin=-1,
      zmax=1)
  corr_fig.update_layout(height=600)
  return corr_fig

@st.cache_data
def get_dist_fig():
  # Create interactive distribution plot
  final_df = get_final_df()
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

  dist_fig = px.histogram(
      dist_df,
      x='Score',
      color='Source',
      facet_col='ESG',
      facet_col_wrap=4,
      facet_row_spacing=0.16,
      facet_col_spacing=0.08,)
  
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
  return dist_fig

# Cache entire ESG metric tab
@st.cache_data
def show_correlation_tab(final_df):
  # Get slow loading figures
  corr_fig = get_corr_fig(final_df)
  dist_fig = get_dist_fig()

  st.header('ESG Metric Details')
  st.markdown('''
  This page shows the relationship between each set of ESG metrics. Because
  the metrics are calculated by different providers, they are not
  directly comparable. However, we should still see a relationship between
  the scores as they are all measuring similar underlying factors.
  ''')

  # Create heatmap of correlations
  st.subheader('Correlation Heatmap')
  st.markdown('''
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
  ''')

  # with st.spinner('Updating plot...'):
  st.plotly_chart(corr_fig, use_container_width=True)

  st.subheader('Distribution of ESG Metrics')
  st.markdown('''
  Looking at the distribution of metrics, we see that Bloomberg scores are more
  concentrated around the mean than S&P Global and Yahoo Finance scores.
  We see the uniform distribution of S&P Global rankings, as expected.
  Yahoo Finance scores show a bimodal distributions.
  ''')

  st.plotly_chart(dist_fig, use_container_width=True)