from io import StringIO
import pandas as pd
import requests

class OceanDataScraper: 
    def __init__(self, webpage_url, start_date='1982-01-01', skiprows=0):
        self.webpage_url = webpage_url
        self.start_date= start_date
        self.skiprows = skiprows
        self.data = None
        
    def scrape(self):
        try:
            webpage=requests.get(self.webpage_url)
            self.data=pd.read_csv(StringIO(webpage.text), sep='\s+', skiprows=self.skiprows)
            
            print("data scraped")

            return self.data
        except requests.RequestException as e:
            print(f'Error: {e}')
            return None
            
if __name__=="__main__":
    print("utils.py is functioning")