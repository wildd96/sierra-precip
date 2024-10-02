import sys
import os
import pandas as pd
from ocean_data_scraper import OceanDataScraper

url='https://www.cpc.ncep.noaa.gov/products/precip/CWlink/daily_ao_index/monthly.ao.index.b50.current.ascii.table'
ao_prec = OceanDataScraper(webpage_url=url)
data = ao_prec.scrape()

aodf = data.reset_index(names="Year")
df_melted = aodf.melt(id_vars=['Year'], var_name='Month', value_name='ao_value')
df_melted['DATE'] = pd.to_datetime(df_melted['Year'].astype(str) + '-' + df_melted['Month'], format='%Y-%b')
df_melted = df_melted.drop(columns=['Year', 'Month'])
df_melted = df_melted[['DATE', 'ao_value']]
data=df_melted.sort_values(by='DATE').reset_index(drop=True)
data=data.set_index(data['DATE'])
data=data.drop(columns='DATE')

if __name__=="__main__":
    print("ao_scraper.py is functioning")
    pd.DataFrame(aodf).to_csv("ao_2024-10-01.csv")
    