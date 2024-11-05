#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
from bs4 import BeautifulSoup
import yfinance as yf
from ecbdata import ecbdata
from pyjstat import pyjstat
from fredapi import Fred

import pandas as pd
import numpy as np
import scipy

import matplotlib.pyplot as plt
import seaborn as sns
import altair as alt
import plotly.graph_objects as go
import plotly.express as px

from datetime import datetime

import warnings
warnings.filterwarnings("ignore")


# In[2]:


# nb default colors for plots and excel
nb_default_color1 = '#179297'
nb_default_color2 = '#BFCE28'

# API Key Alphavantage
alpha_api_key = 'EW4A338V8YGLZI3G'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Connection': 'keep-alive',
}

save_pathx = '....'


# In[3]:


def extract_discount_rates_from_mercer():
    
    """
    Function to extract data from Mercer('https://www.mercer.com/de-de/insights/betriebliche-altersversorgung-und-risikomanagement/discount-rate-for-ifrs-us-gaap-hgb-valuations/').
    It returns 4 dataframes.
    With this function we are able to extract about the following topics in the correspoding order.
    
    - DISCOUNT RATES OVER THE LAST YEARS
    - interest rates can be derived from the MYC for different durations through an interpolation
    - HISTORY OF HGB DISCOUNT RATES 15-YEAR PERIOD
    - forecasted interest rates 
    """
    
    url = 'https://www.mercer.com/de-de/insights/betriebliche-altersversorgung-und-risikomanagement/discount-rate-for-ifrs-us-gaap-hgb-valuations/'    

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        tables = soup.find_all('table')
        
        df_table0 = pd.read_html(str(tables[0]))[0]
        df_table1 = pd.read_html(str(tables[1]))[0]
        df_table2 = pd.read_html(str(tables[2]))[0]
        df_table3 = pd.read_html(str(tables[3]))[0]
        
        # ETL processes specific to each table
        
        ############
        df_table3.columns = df_table3.iloc[0]
        df_table3 = df_table3[1:]
        ############
        df_table2.attrs['name'] = df_table2.iloc[0][0] #HISTORY OF HGB DISCOUNT RATES 15-YEAR PERIOD
        df_table2.columns = df_table2.iloc[1]
        df_table2 = df_table2.iloc[2:, 0:3]
        
        df_table2['DATE'] = df_table2['DATE'].str.replace('  ', ' ', regex=False)
        df_table2['DATE'] = df_table2['DATE'].str.replace(',', '', regex=False)
        df_table2['DATE'] = df_table2['DATE'].str.replace(' ', '', regex=False)
        df_table2['DATE'] = pd.to_datetime(df_table2['DATE'], format='%B%d%Y', errors='coerce').dt.date
        ############
        df_table1.columns = df_table1.iloc[0]
        df_table1 = df_table1[2:]
        ############
        df_table0.columns = df_table0.iloc[1]
        df_table0.attrs['name'] = df_table0.iloc[0][0] #DISCOUNT RATES OVER THE LAST YEARS
        df_table0 = df_table0[2:]
        
        df_table0['DATE'] = df_table0['DATE'].str.replace('  ', ' ', regex=False)
        df_table0['DATE'] = df_table0['DATE'].str.replace(',', '', regex=False)
        df_table0['DATE'] = df_table0['DATE'].str.replace(' ', '', regex=False)
        df_table0['DATE'] = pd.to_datetime(df_table0['DATE'], format='%B%d%Y', errors='coerce').dt.date
        
    return df_table0, df_table1, df_table2, df_table3


# In[4]:


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


# In[5]:


def extract_data_from_ecb(key, start_date='2020-01'):
    """ 
    Function to extract data from ECB.

    Arguments: key str: URL key
               start_date str:  start date

    Returns:   pandas dataframe with TIME_PERIOD and OBS_VALUE columns
    """
    
    df = ecbdata.get_series(key,
                        start=start_date, detail='dataonly')
    
    df.TIME_PERIOD = pd.to_datetime(df.TIME_PERIOD)
    df = df[['TIME_PERIOD', 'OBS_VALUE']]
    
    return df


# In[6]:


def get_data_from_yf(tickers, start_date, end_date, col):
    
    """
    Downloads historical stock data for the given tickers from Yahoo Finance.

    Parameters:
    - tickers (str or list): The ticker symbol(s) of the asset(s) to download. 
                             Can be a single ticker as a string or multiple tickers as a list of strings.
    - start_date (str): The start date for the data in 'YYYY-MM-DD' format.
    - end_date (str): The end date for the data in 'YYYY-MM-DD' format.
    - col (str): The column to extract from the data (e.g., 'Adj Close', 'Open', 'High', 'Low', 'Close', 'Volume').

    Returns:
    - pandas.DataFrame: A DataFrame containing the historical data for the specified tickers and column within the date range.

    Example:
    >>> get_data_from_yf('AAPL', '2022-01-01', '2022-12-31', 'Adj Close')
    """
    
    data = yf.download(tickers, start=start_date, end=end_date)[col]
    return data


# In[7]:


def get_fx_data(from_currency, to_currency, start_date='1900-01-01', api_key=alpha_api_key):
    """
    Function to extract FX rates
    
    Parameters: api_key: str alpha vantage key (optional)
                from_currency: str
                to_currency: str
                start_date: str YY-MM-DD, if not defined it will retrieve since the beginning
    
    Returns a pandas DataFrame with Date and FX rates columns
    """

    url = f'https://www.alphavantage.co/query?function=FX_DAILY&from_symbol={from_currency}&to_symbol={to_currency}&outputsize=full&apikey={api_key}'
    response = requests.get(url)
    data = response.json()
    
    time_series = data['Time Series FX (Daily)']
    df = pd.DataFrame.from_dict(time_series, orient='index')
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    df = df.reset_index()
    
    df[df.columns[1:]] = df[df.columns[1:]].astype(float)
    df = df.rename(columns={'index' : 'Date'})
    
    df = df[df['Date'] >= start_date]
    
    return df


# In[8]:


def extract_data_from_alphavantage(key, api_key=alpha_api_key):
    
    """
    Function to extract data (US related) from alphavantage website
    
    Parameters:
        key: str
        api_key: str alphavantage apikey (optional)
        choose one string of the list ['UNEMPLOYMENT', 'CPI', REAL_GDP_PER_CAPITA', 'INFLATION']  
    
    Returns: pandas DataFrame with Date column e key column
    """
    
    url = f'https://www.alphavantage.co/query?function={key}&apikey={api_key}'
    r = requests.get(url)
    data = r.json()
    
    df = pd.DataFrame(data['data'])
    df['date'] = pd.to_datetime(df['date'])
    df['value'] = df['value'].astype(float)
    df.columns = ['Date', key]
    #df = df[df['Date'] >= '2020-01-01']
    #df.set_index('Date', inplace=True)
    
    return df


# In[9]:


def extract_euribor_1Y_next_three_years():
    
    """
    Extracts the 1-year Euribor interest rate forecast for the next three years from the website 'longforecast.com'.
    
    No Params.
    
    Returns:
    - pandas.DataFrame: A DataFrame with the following columns:
      - 'Date': The first day of the forecasted month (in 'YYYY-MM-DD' format).
      - 'Year': The forecasted year.
      - 'Month': The forecasted month in numeric form (e.g., '01' for January).
      - 'Open': The opening rate at the beginning of the month.
      - 'Min': The minimum forecasted rate for the month.
      - 'Max': The maximum forecasted rate for the month.
      - 'Rate': The final forecasted rate for the month.
      - 'Change': The forecasted change in the rate for the month.

    Example:
    >>> df = extract_euribor_1Y_next_three_years()

    Notes:
    - The function scrapes data from 'https://longforecast.com/euribor-forecast-2017-2018-2019'
    """
    
    url = 'https://longforecast.com/euribor-forecast-2017-2018-2019'

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        forecast_div = soup.find('div', class_='col2')

        table = forecast_div.find('table')

        data = []
        rows = table.find_all('tr')
        current_year = None
        for row in rows:
            cols = row.find_all('td')
            if len(cols) == 1:
                current_year = cols[0].text.strip()
            elif len(cols) == 5:
                month_data = [col.text.strip() for col in cols]
                data.append([current_year] + month_data)

        columns = ['Year', 'Month', 'Open', 'Min-Max,%', 'Rate', 'Change']
        df = pd.DataFrame(data[1:], columns=columns)

        df[['Min', 'Max']] = df['Min-Max,%'].str.split('-', expand=True)

        df = df.drop(columns=['Min-Max,%'])

        columns_to_convert = ['Change', 'Open', 'Rate', 'Min', 'Max']
        for col in columns_to_convert:
            df[col] = df[col].str.replace('+', '').astype(float)

            month_map = {
            'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
            'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
            'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
        }
        df['Month'] = df['Month'].map(month_map)


        df['Date'] = pd.to_datetime(df['Year'] + '-' + df['Month'] + '-01')

        df = df[['Date', 'Year', 'Month', 'Open', 'Min','Max', 'Rate', 'Change']]
        
        return df


# In[10]:


def extract_euribor_3M_next_three_years():
    
    """
    Extracts the 3-month Euribor interest rate forecast for the next three years from the website 'longforecast.com'.

    No Params.
    
    Returns:
    - pandas.DataFrame: A DataFrame with the following columns:
      - 'Date': The first day of the forecasted month (in 'YYYY-MM-DD' format).
      - 'Year': The forecasted year.
      - 'Month': The forecasted month in numeric form (e.g., '01' for January).
      - 'Open': The opening rate at the beginning of the month.
      - 'Min': The minimum forecasted rate for the month.
      - 'Max': The maximum forecasted rate for the month.
      - 'Rate': The final forecasted rate for the month.
      - 'Change': The forecasted change in the rate for the month.

    Example:
    >>> df = extract_euribor_3M_next_three_years()

    Notes:
    - The function scrapes data from 'https://longforecast.com/euribor-3m'.
    """
    
    
    url = 'https://longforecast.com/euribor-3m'

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        forecast_div = soup.find('div', class_='col2')

        table = forecast_div.find('table')

        data = []
        rows = table.find_all('tr')
        current_year = None
        for row in rows:
            cols = row.find_all('td')
            if len(cols) == 1:
                current_year = cols[0].text.strip()
            elif len(cols) == 5:
                month_data = [col.text.strip() for col in cols]
                data.append([current_year] + month_data)

        columns = ['Year', 'Month', 'Open', 'Min-Max,%', 'Rate', 'Change']
        df = pd.DataFrame(data[1:], columns=columns)

        df[['Min', 'Max']] = df['Min-Max,%'].str.split('-', expand=True)

        df = df.drop(columns=['Min-Max,%'])

        columns_to_convert = ['Change', 'Open', 'Rate', 'Min', 'Max']
        for col in columns_to_convert:
            df[col] = df[col].str.replace('+', '').astype(float)

            month_map = {
            'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
            'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
            'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
        }
        df['Month'] = df['Month'].map(month_map)


        df['Date'] = pd.to_datetime(df['Year'] + '-' + df['Month'] + '-01')

        df = df[['Date', 'Year', 'Month', 'Open', 'Min','Max', 'Rate', 'Change']]
        
        return df


# In[11]:


def extract_ecb_interest_rate_next_three_years():
    
    """
    Extracts the European Central Bank (ECB) interest rate forecast for the next three years from the website '30rates.com'.

    No Params.

    Returns:
    - pandas.DataFrame: A DataFrame with the following columns:
      - 'Date': The first day of the forecasted month (in 'YYYY-MM-DD' format).
      - 'Year': The forecasted year.
      - 'Month': The forecasted month in numeric form (e.g., '01' for January).
      - 'Open': The opening rate at the beginning of the month.
      - 'Min': The minimum forecasted rate for the month.
      - 'Max': The maximum forecasted rate for the month.
      - 'Rate': The final forecasted rate for the month.
      - 'Change': The forecasted change in the rate for the month.

    Example:
    >>> df = extract_ecb_interest_rate_next_three_years()

    Notes:
    - The function scrapes data from the 'https://30rates.com/ecb-rate' page.
    """
    
    url = 'https://30rates.com/ecb-rate'

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        forecast_div = soup.find('div', class_='col2')

        table = forecast_div.find('table')

        data = []
        rows = table.find_all('tr')
        current_year = None
        for row in rows:
            cols = row.find_all('td')
            if len(cols) == 1:
                current_year = cols[0].text.strip()
            elif len(cols) == 5:
                month_data = [col.text.strip() for col in cols]
                data.append([current_year] + month_data)

        columns = ['Year', 'Month', 'Open', 'Min-Max,%', 'Rate', 'Change']
        df = pd.DataFrame(data[1:], columns=columns)

        df[['Min', 'Max']] = df['Min-Max,%'].str.split('-', expand=True)

        df = df.drop(columns=['Min-Max,%'])

        columns_to_convert = ['Change', 'Open', 'Rate', 'Min', 'Max']
        for col in columns_to_convert:
            df[col] = df[col].str.replace('+', '').astype(float)

            month_map = {
            'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
            'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
            'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
        }
        df['Month'] = df['Month'].map(month_map)


        df['Date'] = pd.to_datetime(df['Year'] + '-' + df['Month'] + '-01')

        df = df[['Date', 'Year', 'Month', 'Open', 'Min','Max', 'Rate', 'Change']]
        
        return df


# In[12]:


def extract_fed_next_three_years():
    
    """
    Extracts the Federal Reserve interest rate forecast for the next three years from the website '30rates.com'.

    Returns:
    - pandas.DataFrame: A DataFrame with the following columns:
      - 'Date': The first day of the forecasted month (in 'YYYY-MM-DD' format).
      - 'Year': The forecasted year.
      - 'Month': The forecasted month in numeric form (e.g., '01' for January).
      - 'Open': The opening rate at the beginning of the month.
      - 'Min': The minimum forecasted rate for the month.
      - 'Max': The maximum forecasted rate for the month.
      - 'Rate': The final forecasted rate for the month.
      - 'Change': The forecasted change in the rate for the month.

    Example:
    >>> df = extract_fed_next_three_years()

    Notes:
    - The function scrapes data from the 'https://30rates.com/fed-rate' page.
    """
    
    
    url = 'https://30rates.com/fed-rate'

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        forecast_div = soup.find('div', class_='col2')

        table = forecast_div.find('table')

        data = []
        rows = table.find_all('tr')
        current_year = None
        for row in rows:
            cols = row.find_all('td')
            if len(cols) == 1:
                current_year = cols[0].text.strip()
            elif len(cols) == 5:
                month_data = [col.text.strip() for col in cols]
                data.append([current_year] + month_data)

        columns = ['Year', 'Month', 'Open', 'Min-Max,%', 'Rate', 'Change']
        df = pd.DataFrame(data[1:], columns=columns)

        df[['Min', 'Max']] = df['Min-Max,%'].str.split('-', expand=True)

        df = df.drop(columns=['Min-Max,%'])

        columns_to_convert = ['Change', 'Open', 'Rate', 'Min', 'Max']
        for col in columns_to_convert:
            df[col] = df[col].str.replace('+', '').astype(float)

            month_map = {
            'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
            'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
            'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
        }
        df['Month'] = df['Month'].map(month_map)


        df['Date'] = pd.to_datetime(df['Year'] + '-' + df['Month'] + '-01')

        df = df[['Date', 'Year', 'Month', 'Open', 'Min','Max', 'Rate', 'Change']]
        
        return df


# In[13]:


def extract_euribor_data_from_ecb(tenor, start_date):
    """
    Function to extract Euribor data.
    Extracted from ECB.
    Returns a dataframe with euribor data for a defined tenor from start_date until now.
    
    Params: 
        - tenor (str): '3M' or '6M' or '1M' or '1Y'
        - startdate (str)

    Returns a dataframe with euribor data for the specified tenor from start_date until now.

    >>> Usage example:  extract_euribor_data_from_ecb('1Y', '2020-01-01') 
    """

    dict_keys = {
        '3M': 'FM.M.U2.EUR.RT.MM.EURIBOR6MD_.HSTA',
        '6M': 'FM.M.U2.EUR.RT.MM.EURIBOR3MD_.HSTA',
        '1M': 'FM.M.U2.EUR.RT.MM.EURIBOR1MD_.HSTA',
        '1Y': 'FM.M.U2.EUR.RT.MM.EURIBOR1YD_.HSTA'
    }

    df = extract_data_from_ecb(dict_keys[tenor], start_date)
    df.columns = ['Date', 'Euribor ' + tenor]

    return df


# In[14]:


def extract_euribors(start_date):
    
    """
    Function to extract Euribor data for several tenors ('3M','6M','1M','1Y').
    Extracted from ECB.
    
    Params: 
        - start_date (str)

    Returns a dataframe with euribor data for several tenor from start_date until now. 

    >>> Usage example:  extract_euribors('2020-01-01')
    """
    
    dict_keys = {
        '3M': 'FM.M.U2.EUR.RT.MM.EURIBOR6MD_.HSTA',
        '6M': 'FM.M.U2.EUR.RT.MM.EURIBOR3MD_.HSTA',
        '1M': 'FM.M.U2.EUR.RT.MM.EURIBOR1MD_.HSTA',
        '1Y': 'FM.M.U2.EUR.RT.MM.EURIBOR1YD_.HSTA'
    }

    df_aux = extract_data_from_ecb(dict_keys['1M'], start_date)
    df_aux.columns = ['Date', 'Euribor 1M']

    for tenor in ['3M', '6M', '1Y']:
        df_aux1 = extract_data_from_ecb(dict_keys[tenor], start_date)
        df_aux1.columns = ['Date', 'Euribor ' + tenor]

        df_aux = df_aux.merge(df_aux1, on='Date', how='left')

    return df_aux


# In[15]:


def write_data_in_excel(output_path, dataframes_sheets):
    """
    Guarda múltiplos DataFrames em um arquivo Excel, cada um em uma sheet diferente,
    e aplica formatação ao cabeçalho.

    Parameters:
    - output_path (str): Caminho do arquivo de saída (.xlsx).
    - dataframes_sheets (dict): Dicionário onde as chaves são os nomes das sheets e os valores são os DataFrames.

    >>>>> Exemplo de uso:
    dataframes_sheets = {
        'Sheet1': df1,
        'Sheet2': df2
    }
    write_data_in_excel('excelname.xlsx', dataframes_sheets)
    """
    with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
        for sheet_name, df in dataframes_sheets.items():
            df.to_excel(writer, sheet_name=sheet_name, index=True)
            
            workbook  = writer.book
            worksheet = writer.sheets[sheet_name]

            # Define a formatação para o cabeçalho
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'center',
                'align': 'center',
                'fg_color': nb_default_color1,  # Cor de fundo
                'font_color': '#FFFFFF',  # Cor do texto (branco)
            })

            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num + 1, value, header_format)


# In[16]:


def KRI_analysis_risk_parameters_annex(year):
    """
    Downloads the latest KRI_analysis_risk_parameters_annex from:
            'https://www.eba.europa.eu/risk-analysis-and-data/risk-dashboard',
    given the year parameter.
    
    (IMPROVEMENT: IMPLEMENT SAVE PATH IN THE FUTURE)
    
    Params:
        year: int

    Returns: - None
             - it downloads and saves a file

    Usage example: KRI_analysis_risk_parameters_annex(2020)
    """
    
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
        print("If it didn't download the right file, please download it manually for the right specific year and quarter on the url below:\n        https://www.eba.europa.eu/risk-and-data-analysis/risk-analysis/risk-monitoring/risk-dashboard")


# In[17]:


def calculate_sum_npv(df, cf_column, discount_rate):
    """
    Calculates NPV, given a dataframe with cashflows and year column and a constante discount rate.
    It applies the discount yearly and then sums up the npvs.
    
    Params: 
        - cashflows columns (str)
        - df (pandas DataFrame)
        - discount rate float, (value between 0 and 1)
    
    Returns the sum of NPVs.

    >>> Usage example:  calculate_sum_npv(df, 'cashflows', 0.0345)
    """

    df['ano_aux'] = df.index + 1
    df['NPV'] = df[cf_column] / (1 + discount_rate)**df['ano_aux']
    
    sum_npv = int(df['NPV'].sum())
    
    return sum_npv



def calculate_annual_npv(df, cf_column, discount_rate):
    """
    Calculates NPV, given a dataframe with cashflows and year column and a constante discount rate.
    It applies the discount yearly.
    
    Params: 
        - cashflows columns (str)
        - df (pandas DataFrame)
        - discount rate float, (value between 0 and 1)
    
    Returns the given dataframe with the annual NPVs column added.

    >>> Usage example:  calculate_annual_npv(df, 'cashflows', 0.0345)
    """

    df['ano_aux'] = df.index + 1
    df['NPV'] = df[cf_column] / (1 + discount_rate)**df['ano_aux']
    
    return df



def extract_AAA_rated_yield_curves():
    """
    No Params.
    
    Extrai e combina curvas de rendimento ('yield curves') de títulos com rating AAA da zona do Euro
    a partir do banco de dados do Banco Central Europeu (ECB) para diferentes prazos de maturidade (tenors).

    A função extrai dados de rendimentos para diferentes tenors (1 ano, 2 anos, 5 anos, 10 anos, 15 anos,
    20 anos e 30 anos) e combina os dados em um único DataFrame, contendo a taxa de rendimento para 
    cada maturidade em cada data.

    Retorna:
    --------
    pandas.DataFrame
        Um DataFrame contendo as colunas:
        - 'Date': a data de observação dos rendimentos;
        - 'Rate1Y': a taxa de rendimento para o tenor de 1 ano;
        - 'Rate2Y': a taxa de rendimento para o tenor de 2 anos;
        - 'Rate5Y': a taxa de rendimento para o tenor de 5 anos;
        - 'Rate10Y': a taxa de rendimento para o tenor de 10 anos;
        - 'Rate15Y': a taxa de rendimento para o tenor de 15 anos;
        - 'Rate20Y': a taxa de rendimento para o tenor de 20 anos;
        - 'Rate30Y': a taxa de rendimento para o tenor de 30 anos.

    Notas:
    ------
    - A função coleta dados a partir de janeiro de 2020.

    Exemplo de uso:
    ---------------
    >>> df_yield_curves = extract_AAA_rated_yield_curves()
    """
    
    dates = extract_data_from_ecb(f'YC.B.U2.EUR.4F.G_N_A.SV_C_YM.SR_1Y',
                            start_date='2020-01')['TIME_PERIOD']

    df_aa_yieldcurve = extract_data_from_ecb(f'YC.B.U2.EUR.4F.G_N_A.SV_C_YM.SR_1Y',
                            start_date='2020-01').rename(columns={'TIME_PERIOD': 'Date', 'OBS_VALUE': 'Rate'})

    df_combined = df_aa_yieldcurve.copy()

    for tenor in [2, 5, 10, 15, 20, 30]:

        df_aux = extract_data_from_ecb(f'YC.B.U2.EUR.4F.G_N_A.SV_C_YM.SR_{str(tenor)}Y',
                            start_date='2020-01')
        df_aux = df_aux.rename(columns={'TIME_PERIOD': 'Date', 'OBS_VALUE': 'Rate'})

        df_combined = df_combined.merge(df_aux, how='left', on='Date', suffixes=('', str(tenor) + 'Y'))
    
    df_combined.columns = ['Date','Rate1Y','Rate2Y', 'Rate5Y', 'Rate10Y', 'Rate15Y','Rate20Y', 'Rate30Y']  

    return df_combined


def extract_country_life_exp_index(sex='T', start_year=1900):
    
    """
    Extrai os dados da expectativa de vida para o país Portugal a partir do banco de dados
    do World Bank e calcula o percentual de crescimento da expectativa de vida ao longo dos anos.
    
    Parâmetros:
    -----------
    sex : str, opcional
        O sexo para o qual os dados de expectativa de vida serão extraídos. 
        As opções são:
        - 'T' para a população total (padrão),
        - 'M' para a população masculina,
        - 'F' para a população feminina.
        
    start_year : int, opcional
        O ano inicial a partir do qual os dados serão filtrados. 
        O valor padrão é 1900, ou seja, inclui todos os anos a partir de 1900.
    
    Retorna:
    --------
    pandas.DataFrame
        Um DataFrame contendo três colunas:
        - 'Ano' (int): o ano de referência;
        - 'Esperança média de vida' (float): a expectativa média de vida naquele ano;
        - '%crescimento' (float): a variação percentual na expectativa de vida em relação ao ano anterior.
    
    Exemplo de uso:
    ---------------
    >>> df = extract_country_life_exp_index(sex='T', start_year=2005)
    """

    if sex == 'T':
        indicator = {'SP.DYN.LE00.IN': 'Life Expectancy'}
    elif sex == 'M':
        indicator = {'SP.DYN.LE00.MA.IN': 'Life Expectancy'}
    elif sex == 'F':
        indicator = {'SP.DYN.LE00.FE.IN': 'Life Expectancy'}
    else:
        print('Invalid sex! Choose one of "T", "M", "F".')
              
    data = wbdata.get_dataframe(indicator, 
                                country='PRT').dropna().reset_index()
    data = data.sort_values(by='date', ascending=True)
    data.columns = ['Ano', 'Esperança média de vida']
    data['Ano'] = data['Ano'].astype(int)
    
    data['%crescimento'] = (data['Esperança média de vida'].pct_change() * 100).round(2)
    data = data[data['Ano'] >= start_year]
    
    return data



def extract_life_expectancy_by_year(age, country, sex, start_year=1900):
    
    """
    Extrai e processa os dados de expectativa de vida para um país específico a partir da API Eurostat,
    para uma idade, sexo e ano inicial fornecidos.

    Parâmetros:
    -----------
    age : int
        A idade a partir da qual a expectativa de vida será extraída.
        Se a idade for 0, será considerada a expectativa de vida ao nascer.
    
    country : str
        O código do país (ISO) para o qual os dados serão extraídos (por exemplo, 'PT' para Portugal).
    
    sex : str
        O sexo para o qual a expectativa de vida será extraída. As opções são:
        - 'M' para masculino,
        - 'F' para feminino,
        - 'T' para total (ambos os sexos).
    
    start_year : int, opcional
        O ano inicial a partir do qual os dados serão filtrados. O padrão é 1900, ou seja,
        inclui todos os anos desde 1900.

    Retorna:
    --------
    pandas.DataFrame
        Um DataFrame contendo:
        - 'Ano' (int): o ano de referência;
        - 'Esperança média de vida aos X anos (S)' (float): a expectativa de vida aos X anos, 
          onde X é a idade fornecida e S é o sexo.
        - '%crescimento' (float): a variação percentual na expectativa de vida em relação ao ano anterior.

    Notas:
    ------
    - Os dados são extraídos da API da Eurostat, e a URL é configurada dinamicamente com base nos parâmetros
      fornecidos (idade, país, sexo).
    - A função filtra os resultados a partir de um ano inicial (start_year) e calcula a variação percentual 
      da expectativa de vida ao longo dos anos.
    - Caso ocorra um erro na requisição à API (status diferente de 200), uma mensagem de erro será impressa.

    Exemplo de uso:
    ---------------
    >>> df = extract_life_expectancy_by_year(age=65, country='PT', sex='F', start_year=2000)
    """

    if age == 0:
        age = '_LT1'
        age_str = '0'
    else:
        age = str(age)
        age_str = str(age)
    
    # URL da API Eurostat com parâmetros corrigidos para a esperança de vida aos 65 anos, em Portugal
    url = f"https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/DEMO_R_MLIFEXP?age=Y{age}&geo={country}&sex={sex}&format=JSON"
    
    # Fazendo a requisição GET
    response = requests.get(url)

    # Verificando o status da requisição
    if response.status_code == 200:
        data = response.json()
    else:
        print(f"Erro ao acessar a API: {response.status_code}")


    years = list(data['dimension']['time']['category']['index'].keys())
    life_exp = list(data['value'].values())
    
    df_exp_age = pd.DataFrame({
        'Ano': years,
        f'Esperança média de vida aos {age_str} anos ({sex})' : life_exp 
                 })
    
    columns = df_exp_age.columns
    
    df_exp_age[columns[0]] = df_exp_age[columns[0]].astype(int)
    df_exp_age[columns[1]] = df_exp_age[columns[1]].astype(float)


    df_exp_age['%crescimento'] = (df_exp_age[columns[1]].pct_change() * 100).round(2)

    df_exp_age = df_exp_age[df_exp_age['Ano'] >= start_year]
    
    return df_exp_age


def extract_daily_ts_from_fred(key, obs_column_name, observation_start='2000-01-01', observation_end=None):

    """
    Function to extract a time series from FRED through the url key.
    
    Params: - url_key: str
            - obs_column_name: str (string you want to the observation value column)
            - observation_start: str (param optional)
            - observation_end: str (param optional)
    
    Returns: pandas dataframe with column 'Date' and obs_column_name
            
    >>> Usage example: 
            extract_daily_ts_from_fred('QPTR628BIS', 're_pt_index', observation_start='2008-01-01', observation_end='2023-12-31')
    """
    
    fred_api_key = 'eff3c719d275248bf5cdcfc836400e53'
    fred = Fred(api_key=fred_api_key)
    
    df = pd.DataFrame(fred.get_series(key, observation_start=observation_start, observation_end=observation_end)).reset_index()
    df.columns = ['Date', obs_column_name]

    return df


def plot_corr_matrix(df, cmap="Greens", annot=True, title=None, figsize=(6,4), fmt='.2f'):

    """
    Plots a correlation matrix heatmap for a given DataFrame.

    This function visualizes the pairwise correlation coefficients between columns
    in a DataFrame using a heatmap. It helps in identifying relationships and
    patterns in the data.

    Parameters:
    ----------
    df : pandas.DataFrame
        The input DataFrame for which the correlation matrix will be computed.
        
    cmap : str, optional
        The color map to be used for the heatmap. Default is "Greens".
        
    annot : bool, optional
        If True, the correlation coefficients will be displayed on the heatmap.
        Default is True.
        
    title : str, optional
        The title for the heatmap. If None, no title will be displayed.
        
    figsize : tuple, optional
        The size of the figure to be created, specified as (width, height).
        Default is (6, 4).
        
    fmt : str, optional
        The format for the annotation text on the heatmap. Default is '.2f' 
        (two decimal places).

    Example Usage:
    --------------
    plot_corr_matrix(df) 
    plot_corr_matrix(df, cmap="Coolwarm", title="Example", figsize=(12, 8))

    Returns:
    -------
    None
        This function does not return any value; it directly displays the heatmap.

    """
    
    plt.figure(figsize=figsize)

    if title:
        plt.title(title, fontsize=14, fontweight='bold', color=nb_default_color1)
    sns.heatmap(df.corr(), cmap=cmap, annot=annot, fmt=fmt', linewidths=0.5)
    plt.show()