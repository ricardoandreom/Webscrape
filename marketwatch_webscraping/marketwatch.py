from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time
import os
import shutil
import pandas as pd

chrome_driver_path = "C:\\Users\\Admin\\Desktop\\chromedriver.exe"
service = Service(chrome_driver_path)

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
prefs = {"download.default_directory": "C:\\Users\\Admin\\Desktop\\idealista\\outputs"}
options.add_experimental_option("prefs", prefs)

driver = webdriver.Chrome(service=service, options=options)


def extract_country_bonds_from_marketwatch(tenor, country, startdate, enddate):
    try:
        url = f"https://www.marketwatch.com/investing/bond/tmbmk{country}-{tenor}y/downloaddatapartial?startdate={startdate}&enddate={enddate}&frequency=p1d&csvdownload=true&downloadpartial=false&newdates=false&countrycode=bx"

        driver.get(url)

        time.sleep(5)

        download_folder = "C:\\Users\\Admin\\Desktop\\idealista\\outputs"
        original_file = os.path.join(download_folder, "downloaddatapartial.csv")
        new_file_name = f"dados_tmbmk{country}_{tenor}y_{startdate.replace('/','-')}_{enddate.replace('/','-')}.csv"
        new_file = os.path.join(download_folder, new_file_name)

        time.sleep(2)
        if os.path.exists(original_file):
            shutil.move(original_file, new_file)

    except Exception as e:
        print(f"Ocorreu um erro: {e}")

    finally:
        driver.quit()

# usage example
extract_country_bonds_from_marketwatch('02', 'it', '09/22/2024', '09/30/2024')
