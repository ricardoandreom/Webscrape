# base configurations
from config import *
# data processing libraries
import pandas as pd
import numpy as np
# data viz libraries
import seaborn as np
import matplotlib.pyplot as plt
import plotly as pl
import altair
# statistics libraries
import statsmodels as sm
import scipy 
# scraping libraries
from pyjstat import pyjstat
from ecbdata import ecbdata
import requests
from bs4 import BeautifulSoup

import os
import re
# hide warnings
import warnings
warnings.filterwarnings("ignore")


def extract_data_from_bank_pt(series_id, variable_name):
    """ 
    Function to extract data from BPSTAT API.

    Arguments: series_id int
             variable_name str.
             If variable_name is None, variable_name is set to urls label.

    Returns:   pandas dataframe with Date and variable_name columns
    """
    
    BPSTAT_API_URL="https://bpstat.bportugal.pt/data/v1"

    url = f"{BPSTAT_API_URL}/series/?lang=EN&series_ids={series_id}"
    series_info = requests.get(url).json()[0]

    domain_id = series_info["domain_ids"][0]
    dataset_id = series_info["dataset_id"]

    dataset_url = f"{BPSTAT_API_URL}/domains/{domain_id}/datasets/{dataset_id}/?lang=EN&series_ids={series_id}"
    dataset = pyjstat.Dataset.read(dataset_url)
    df = dataset.write('dataframe')

    df['Date'] = pd.to_datetime(df['Date'])
    if variable_name is None:
        variable_name = series_info['label']

    df = df.rename(columns={'value': variable_name})
    df = df[['Date', variable_name]]

    return df



def KRI_analysis_risk_parameters_annex(year):
  # URL of the EBA risk parameters page
  url = 'https://www.eba.europa.eu/risk-analysis-and-data/risk-dashboard'

  # Send a GET request to the URL
  response = requests.get(url)
  response.raise_for_status()  # Ensure we got a valid response

  # Parse the HTML content using BeautifulSoup
  soup = BeautifulSoup(response.content, 'html.parser')

  # Find the link to the XLS file
  xlsx_link = None
  for a in soup.find_all('a', href=True):
      if ('https' in a['href']) and ('%20' + str(year) + '.xlsx' in a['href']):
          xlsx_link = a['href']
          quarter = xlsx_link[-14:-12]
          break

  if not xlsx_link:
      print("Could not find the xlsx link on the page.")
  else:
      # If the link is relative, make it absolute
      if not xlsx_link.startswith('http'):
          xlsx_link = 'https://www.eba.europa.eu' + xlsx_link

      # Send a GET request to the XLS link
      xlsx_response = requests.get(xlsx_link)
      xlsx_response.raise_for_status()  # Ensure we got a valid response

      filename = f'KRI - Risk parameters annex - {quarter} {year}.xlsx'
      # Save the content to a file
      with open(filename, 'wb') as f:
        f.write(xlsx_response.content)

      print(f"File downloaded successfully as {filename}.")
      print("\n")
      print("If it'didnt downloaded the right file, please download it manually for the right specific year and quarter on the url below:\n\
      https://www.eba.europa.eu/risk-and-data-analysis/risk-analysis/risk-monitoring/risk-dashboard")



