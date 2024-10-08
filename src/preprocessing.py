import os, sys
import pandas as pd
import numpy as np
import dotenv
from statsmodels.tsa.seasonal import seasonal_decompose
import jax.numpy as jnp

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from database import db_operations

from datetime import datetime

dotenv.load_dotenv(os.path.join(parent_dir, '.env'))



#TODO: THE RETURNED DATATYPE IS BEING MIXED AROUND, DETERMINE WHAT DATATYPE I WANT IT TO END AS AND ENFORCE IT WITH ->



class DataProcessed:
    def __init__(self):
        self.data = None
        self.shift_dict = {}
        self.y = None
        self.X = None
        self.ycolnames = None
        self.Xcolnames = None
        self.ydates = None
        self.Xdates = None
        self.db = db_operations.Database(
            project_id=os.getenv("PROJECT_ID"),
            region=os.getenv("REGION"),
            instance_name=os.getenv("INSTANCE_NAME"),
            db_user=os.getenv("DB_USER"),
            db_pass=os.getenv("DB_PASS"),
            db_name=os.getenv("DB_NAME")
        )

    @staticmethod
    def date_to_unix(date_array):
        timestamps = np.array([int(datetime.fromisoformat(date_string.rstrip('Z')).timestamp()) for date_string in date_array])
        return timestamps
    
    def pull(self):

        y = self.db.pull_table("ao_pdo_enso.mytable")
        self.ycolnames = pd.DataFrame(y).columns
        self.y = np.array([line[2:] for line in y], dtype=np.float32)
        #self.ydates = np.array([line[1] for line in y])
        
        self.ydates = self.date_to_unix([line[1] for line in y])
                
        x = self.db.pull_table("ao_pdo_enso.climate_indices")
        self.Xcolnames = pd.DataFrame(x).columns
        self.X = np.array([line[1:] for line in x], dtype=np.float32)
        #self.Xdates = np.array([line[0] for line in x])
        self.Xdates = self.date_to_unix([line[0].strftime('%Y-%m-%d 00:00:00+00:00') for line in x])

        x1 = np.r_[np.full((36,34), np.nan), self.y]
        self.data = np.c_[self.X, x1]
        return None
    def pull_table(self, table):
        return self.db.pull_table(table)
        
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


if __name__ == "__main__":
    x = DataProcessed()
    x.pull()
    print(x.X)
    print(x.y)
