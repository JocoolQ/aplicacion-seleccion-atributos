import pandas as pd
import numpy as np

class Checker:

    def check_attributes(self, df):
        checking = {}
        for i in df.columns:
            if df[i].dtype == 'object':
                checking[i] = 'Categórico'
            elif(df[i].value_counts().count() < len(df[i])/2):
                checking[i] = 'Categórico'
            else:
                checking[i] = 'Numérico'
        return checking