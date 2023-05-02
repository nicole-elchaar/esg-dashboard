# Setup
import pandas as pd

# Load in final dataset
final_df = pd.read_csv('inputs/Final_Merged_Analyzing_Data.csv')

# Create map for named columns to display names
col_to_display_esg = {
  'BESG ESG Score': 'Bloomberg ESG Score',
  'BESG Environmental Pillar Score': 'Bloomberg Environmental Pillar',
  'BESG Governance Pillar Score': 'Bloomberg Governance Pillar',
  'BESG Social Pillar Score': 'Bloomberg Social Pillar',
  'S&P Global ESG Rank': 'S&P Global ESG Rank',
  'S&P Global Governance & Economic Dimension Rank': 'S&P Global Governance & Economic Dimension Rank',
  'S&P Global Environmental Dimension Rank': 'S&P Global Environmental Dimension Rank',
  'S&P Global Social Dimension Rank': 'S&P Global Social Dimension Rank',
  'yf_ESG_Score': 'Yahoo Finance ESG Score',
  'yf_E_Score': 'Yahoo Finance Environmental Score',
  'yf_S_Score': 'Yahoo Finance Social Score',
  'yf_G_Score': 'Yahoo Finance Governance Score',
  'ret': 'Monthly Return',
  'Last Price': 'Price',
  'Credit Benchmark Credit Risk Indicator': 'Credit Risk Indicator',
  'Overridable Adjusted Beta': 'Beta',
  'Overridable Alpha': 'Alpha',
  'Bloomberg Issuer Default Risk': 'Issuer Default Risk',
  'Volatility 30 Day': '30 Day Volatility',
  'Price Earnings Ratio (P/E)': 'P/E Ratio',
  'Current Market Cap': 'Market Cap',
  # What is Historical Market Cap
  'Basic Earnings per Share': 'EPS',
  'GICS Sector Name': 'GICS Sector',
  'GICS Industry Name': 'GICS Industry',
  'GICS Industry Group Name': 'GICS Industry Group',
  'GICS Sub-Industry Name': 'GICS Sub-Industry',
}

# Transform columns
final_df.rename(columns=col_to_display_esg, inplace=True)

# Export
final_df.to_csv('inputs/final_dataset.csv', index=False)