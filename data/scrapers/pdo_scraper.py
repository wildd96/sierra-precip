import sys
import os
import pandas as pd
from ocean_data_scraper import OceanDataScraper

url='https://www.ncei.noaa.gov/pub/data/cmb/ersst/v5/index/ersst.v5.pdo.dat'
pdo_prec = OceanDataScraper(webpage_url=url, skiprows=1)
data = pdo_prec.scrape()

df_melted = data.melt(id_vars=['Year'], var_name='Month', value_name='pdo_value')
df_melted['DATE'] = pd.to_datetime(df_melted['Year'].astype(str) + '-' + df_melted['Month'], format='%Y-%b')
df_melted = df_melted.drop(columns=['Year', 'Month'])
df_melted = df_melted[['DATE', 'pdo_value']]
data=df_melted.sort_values(by='DATE').reset_index(drop=True)
data=data.set_index(data['DATE'])
data=data.drop(columns='DATE')

if __name__=="__main__":
    print("enso_scraper.py is functioning")
    print(data)
    pd.DataFrame(data).to_csv("pdo_2024-10-01.csv")