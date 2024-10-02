import sys
import os
import pandas as pd
from ocean_data_scraper import OceanDataScraper

url='https://www.cpc.ncep.noaa.gov/data/indices/sstoi.indices'
enso_prec = OceanDataScraper(webpage_url=url)
data = enso_prec.scrape()

data['DATE'] = pd.date_range(start='1982-01-01', periods=len(data), freq="ME")
data.index = data['DATE'].apply(lambda x: x.replace(day=1))
data = data.drop(columns={"YR","MON","DATE"})

if __name__=="__main__":
    print("enso_scraper.py is functioning")
    pd.DataFrame(data).to_csv("enso_2024-10-01.csv")
    