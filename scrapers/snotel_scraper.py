import ulmo
import pandas as pd
import numpy as np
from datetime import datetime
import sys 
import os



wsdlurl = 'https://hydroportal.cuahsi.org/Snotel/cuahsi_1_1.asmx?WSDL'

#https://snowex-2021.hackweek.io/tutorials/geospatial/SNOTEL_query.html
#API requests from python basically all the code below is from this website

sites = ulmo.cuahsi.wof.get_sites(wsdlurl)
sites_df=pd.DataFrame.from_dict(sites, orient='index').dropna()
sites_ca = sites_df[(sites_df.index.str.contains('CA'))]

sites_ca_location = sites_ca.copy()
sites_ca_location.loc[:, 'latitude'] = sites_ca_location['location'].apply(lambda loc: float(loc['latitude']))
sites_ca_location.loc[:, 'longitude'] = sites_ca_location['location'].apply(lambda loc: float(loc['longitude']))

#ulmo.cuahsi.wof.get_site_info(wsdlurl, sites_ca.index[0])['series'].keys()

#The above gets all of the available keys
#They are:
# ['SNOTEL:BATT_D', 'SNOTEL:BATT_H', 'SNOTEL:PRCP_y', 
# 'SNOTEL:PRCP_sm', 'SNOTEL:PRCP_m', 'SNOTEL:PRCP_wy', 'SNOTEL:PRCPSA_y', 
# 'SNOTEL:PRCPSA_D', 'SNOTEL:PRCPSA_sm', 'SNOTEL:PRCPSA_m', 'SNOTEL:PRCPSA_wy', 
# 'SNOTEL:PREC_sm', 'SNOTEL:PREC_m', 'SNOTEL:PREC_wy', 'SNOTEL:SNWD_D', 'SNOTEL:SNWD_sm', 
# 'SNOTEL:SNWD_H', 'SNOTEL:SNWD_m', 'SNOTEL:TAVG_y', 'SNOTEL:TAVG_D', 'SNOTEL:TAVG_sm', 
# 'SNOTEL:TAVG_m', 'SNOTEL:TAVG_wy', 'SNOTEL:TMAX_y', 'SNOTEL:TMAX_D', 'SNOTEL:TMAX_sm', 
# 'SNOTEL:TMAX_m', 'SNOTEL:TMAX_wy', 'SNOTEL:TMIN_y', 'SNOTEL:TMIN_D', 'SNOTEL:TMIN_sm', 
# 'SNOTEL:TMIN_m', 'SNOTEL:TMIN_wy', 'SNOTEL:TOBS_D', 'SNOTEL:TOBS_sm', 'SNOTEL:TOBS_H', 
# 'SNOTEL:TOBS_m', 'SNOTEL:WTEQ_D', 'SNOTEL:WTEQ_sm', 'SNOTEL:WTEQ_H', 'SNOTEL:WTEQ_m'])

#Get current datetime
today = datetime.today().strftime('%Y-%m-%d')

def snotel_fetch(sitecode, variablecode='SNOTEL:WTEQ_sm', start_date='1985-01-01', end_date=today):
    values_df = None
    try:
        site_values = ulmo.cuahsi.wof.get_values(wsdlurl, sitecode, variablecode, start=start_date, end=end_date)
        values_df = pd.DataFrame.from_dict(site_values['values'])
        values_df['datetime'] = pd.to_datetime(values_df['datetime'], utc=True)
        values_df = values_df.set_index('datetime')
        values_df['value'] = pd.to_numeric(values_df['value']).replace(-9999, np.nan)
        values_df = values_df[values_df['quality_control_level_code'] == '1']
    except:
        print("Unable to fetch %s" % variablecode)

    return values_df


values_dict = {}
for i in sites_ca.index:
    try:
        values_dict[f'{i}_SWE']=snotel_fetch(i)['value']
    except Exception as e:
        print(i)
        print(e)
        
values_df=pd.DataFrame(values_dict)
print(values_dict)


class SNOTELVariable:
    def __init__(self,code,name):
        self.code=code
        self.name=name
        
    def fetch_data(self, scraper, site_code, start_date='1950-01-01',end_date=datetime.today().strftime('%Y-%m-%d')):
        return scraper.snotel_fetch(site_code, f"SNOTEL:{self.code}", start_date, end_date)
    
class SnowDepth(SNOTELVariable):
    def __init__(self):
        super().__init__("SNWD_D", "Snow depth")
    
class SnowWaterEquivalent(SNOTELVariable):
    def __init__(self):
        super().__init__("WTEQ_sm", "Snow Water Equivalent")
        
class Precipitation(SNOTELVariable):
    def __init__(self):
        super().__init__("PREC_D", "Precipitation")
        
class Temperature(SNOTELVariable):
    def __init__(self):
        super().__init__("TAVG_D", "Avg temperature")
            
class SNOTELScraper:
    def __init__(self, wsdlurl = 'https://hydroportal.cuahsi.org/Snotel/cuahsi_1_1.asmx?WSDL'):
        self.wsdlurl=wsdlurl
        self.sites = None
        self.variables = {
            'snow_depth': SnowDepth(),
            'swe': SnowWaterEquivalent(),
            'precipitation': Precipitation(),
            'temperature': Temperature()
        }
        
    def fetch_sites(self):
        self.sites = ulmo.cuahsi.wof.get_sites(self.wsdlurl)
        sites_df = pd.DataFrame.from_dict(self.sites, orient='index').dropna()
        sites_ca = sites_df[(sites_df.index.str.contains('CA'))]
        
        self.sites = sites_ca.copy()
        self.sites.loc[:, 'latitude'] = self.sites['location'].apply(lambda loc: float(loc['latitude']))
        self.sites.loc[:, 'longitude'] = self.sites['location'].apply(lambda loc: float(loc['longitude']))

    def snotel_fetch(self, sitecode, variablecode, start_date='1950-10-01', end_date=None):
        if end_date is None:
            end_date = datetime.today().strftime('%Y-%m-%d')
        
        try:
            site_values = ulmo.cuahsi.wof.get_values(self.wsdlurl, sitecode, variablecode, start=start_date, end=end_date)
            values_df = pd.DataFrame.from_dict(site_values['values'])
            values_df['datetime'] = pd.to_datetime(values_df['datetime'], utc=True)
            values_df = values_df.set_index('datetime')
            values_df['value'] = pd.to_numeric(values_df['value']).replace(-9999, np.nan)
            values_df = values_df[values_df['quality_control_level_code'] == '1']
            return values_df
        except Exception as e:
            print(f"Unable to fetch {variablecode} for site {sitecode}: {str(e)}")
            return None

    def fetch_variable_data(self, variable_name, site_code, start_date, end_date):
        if variable_name not in self.variables:
            raise ValueError(f"Unknown variable: {variable_name}")
        
        variable = self.variables[variable_name]
        return variable.fetch_data(self, site_code, start_date, end_date)

    def fetch_all_variables(self, site_code, start_date, end_date):
        data = {}
        for var_name, variable in self.variables.items():
            data[var_name] = variable.fetch_data(self, site_code, start_date, end_date)
        return data

    def get_ca_sites(self):
        return self.sites

def main():
    return None



if __name__ == "__main__":
    main()