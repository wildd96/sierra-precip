from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

def create_pipe1():
    return Pipeline([
        ('Scaler', StandardScaler()),
    ])