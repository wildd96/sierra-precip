import os, sys
import pandas as pd
import numpy as np
from statsmodels.tsa.seasonal import seasonal_decompose

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
from database import db_operations


#TODO: THE RETURNED DATATYPE IS BEING MIXED AROUND, DETERMINE WHAT DATATYPE I WANT IT TO END AS AND ENFORCE IT WITH ->

class DataProcessed:
    def __init__(self):
        self.data = None
        self.shift_dict = {}
        self.y = None
        self.X = None
    
    def pull(self):
        data_retrieval = db_operations.Database(
            project_id=os.getenv("PROJECT_ID"),
            region=os.getenv("REGION"),
            instance_name=os.getenv("INSTANCE_NAME"),
            db_user=os.getenv("DB_USER"),
            db_pass=os.getenv("DB_PASS"),
            db_name=os.getenv("DB_NAME")
        )

        snotel = pd.DataFrame(data_retrieval.pull_table("ao_pdo_enso.mytable"))
        #snotel = snotel.resample('MS', on='DATE').mean() 
        snotel = snotel.reset_index()
        snotel['DATE'] = pd.to_datetime(snotel['DATE']).dt.date
        
        climate_indices = pd.DataFrame(data_retrieval.pull_table("ao_pdo_enso.climate_indices")).replace(-9999, np.nan)
        climate_indices['DATE']=pd.to_datetime(climate_indices['DATE']).dt.date

        self.data = climate_indices.merge(snotel).iloc[:, 1:]
        self.data = self.data.drop(columns=['index', 'FIELD1'])
        
        return None
    
    def auto_corr(self, target, feature, steps = 36):
        df = self.data[[target, feature]].copy()
        corrs = []
        
        for i in range(-steps, steps + 1):
            shifted_df = df.copy()
            shifted_df[feature] = shifted_df[feature].shift(periods = i)
            correlation = shifted_df.dropna().corr().iloc[0,1]
            corrs.append((i, correlation))
            
        return corrs
    
    def remove_seasonality(self, target_only=True, resid=False):
        target_cols = [col for col in self.data.columns if 'SNOTEL' in col]
        
        if target_only == False:
            target_cols = self.data.columns
            
        df = self.data
        df = df.set_index(pd.date_range('1985-01-01', '2024-08-01', freq='MS'))
        for i in target_cols:
            if resid == False:
                x = df[i].dropna()
                #ind = pd.date_range('1985-01-01',periods=len(x) , freq='MS')
                hold = seasonal_decompose(x, period=12)
                df[i] = hold.trend
            else:
                df[i] = df[i].dropna()
                hold = seasonal_decompose(df[i], period = 12)
                df[i] = hold.trend + hold.resid
            
            
        self.data = df
        
        return None
    
    def shift_for_correlation(self, target_column, steps=48):
        features = [col for col in self.data.columns if col != target_column]
        for feat in features:
            corrs = [(i, self.data[[feat, target_column]].shift(i).dropna().corr().iloc[0, 1]) for i in range(-steps, steps)]
            max_shift = max(corrs, key=lambda x: abs(x[1]))[0]
            self.data[feat] = self.data.loc[:, feat].shift(max_shift)
            self.shift_dict[feat] = max_shift
        return None

        
    def single_target(self, target):
        target_cols = [col for col in self.data.columns if 'SNOTEL' not in col]
        x1 = self.data.loc[:, target_cols]
        x2 = self.data.iloc[:, target]
        
        self.data = x1.join(x2)
        
        return None
        
    def drop_na(self):
        self.data = self.data.dropna()
        
        return None
    
    def seperate_y(self):
        target_cols = [col for col in self.data.columns if 'SNOTEL' in col]
        feature_cols = [col for col in self.data.columns if not 'SNOTEL' in col]


        self.y = self.data[target_cols]
        self.X = self.data[feature_cols]

        
        return None