import pandas as pd
import numpy as np
import math as mt

class Selector:

    def apply_numeric_selection(self, df):
        n_result = {}
        n_entropies = []
        total_entropy = round(self.select_numeric_attributes(df), 3)
        n_result['Características'] = 'Entropías'
        n_result['General'] = total_entropy
        for i in df.columns:
            entropy = round(self.select_numeric_attributes(df.drop(i, axis = 1).copy()),3)
            n_entropies.append(entropy)
            n_result['Sin ' + i] = entropy

        n_entropies = np.array(n_entropies)
        to_substract = np.ones(len(n_entropies))
        to_substract *= total_entropy
        substracts = np.abs(to_substract - n_entropies)
        min_sub = substracts.min()
        indexes = np.where(substracts == min_sub)
        attrs = list(df.columns[indexes])
        attr_to_erase = attrs[0]
        df = df.drop([attr_to_erase], axis = 1).copy()
        df.to_csv('static/generated/selecting.csv', index = False)
        return n_result, attr_to_erase, substracts

    def apply_categoric_selection(self, df, filename):
        c_select_for_num = False
        c_result = {}
        c_entropies = []
        c_num_attrs = []
        total_entropy = round(self.select_categoric_attributes(df), 3)
        c_result['Características'] = ['Entropías', 'Número de categorías']
        c_result['General'] = [self.select_categoric_attributes(df), 0]
        for i in df.columns:
            info = []
            entropy = round(self.select_categoric_attributes(df.drop(i, axis = 1).copy()), 3)
            num_attrs = df[i].value_counts().count()
            c_num_attrs.append(num_attrs)
            c_entropies.append(entropy)
            info.append(entropy)
            info.append(num_attrs)
            c_result['Sin ' + i] = info
        c_entropies = np.array(c_entropies)
        to_substract = np.ones(len(c_entropies))
        to_substract *= total_entropy
        substracts = np.abs(to_substract - c_entropies)
        min_entropy = substracts.min()
        indexes = np.where(substracts == min_entropy)
        attrs = df.columns[indexes]
        attrs = list(attrs)
        attr_to_erase = attrs[0]
        if(len(attrs) > 1):
            c_num_attrs = np.array(c_num_attrs)
            num_attrs_to_compare = c_num_attrs[indexes]
            max_num = num_attrs_to_compare.max()
            index_to_erase = np.where(num_attrs_to_compare == max_num)
            attr_to_erase = attrs[index_to_erase[0][0]]
            c_select_for_num = True
        df = df.drop([attr_to_erase], axis = 1).copy()
        df.to_csv('static/generated/selecting.csv', index = False)
        return c_result, attr_to_erase, c_select_for_num, substracts

    def select_numeric_attributes(self, df):
        np_array = df.values
        max_values = []
        for i in range(0, len(np_array[0,:])):
            max_values.append(np_array[:,i].max())
        entropy_matrix = np.zeros((df.shape[0],df.shape[0]))
            
        for i in range(0, len(entropy_matrix[0])):
            for j in range(0, len(entropy_matrix[0])):
                if(j > i):
                    distance_result = ((((np_array[i,:] - np_array[j,:]) / max_values) ** 2).sum()) ** (1/2)
                    similarity_result = np.exp(-0.5 * distance_result)
                    n = similarity_result
                    if(n != 0 and n!= 1):
                        entropy_matrix[i][j] = n * np.log2(n) + (1 - n) * np.log2(1 - n)
        
        n_entropy = entropy_matrix.sum() * -1
        return n_entropy


    def select_categoric_attributes(self, df):
        similarity_matrix = np.zeros((len(df), len(df)))
        entropy_matrix = similarity_matrix.copy()
        for i in range(0, len(similarity_matrix[0])):
            for j in range(0, len(similarity_matrix)):
                if(j > i):
                    similarity_matrix[i][j] = ((df.iloc[i,:] == df.iloc[j,:]).sum())/len(df.iloc[i,:])
                    n = similarity_matrix[i][j]
                    if(n != 0 and n!= 1):
                        entropy_matrix[i][j] = n * np.log2(n) + (1 - n) * np.log2(1 - n)                  
        
        c_entropy = entropy_matrix.sum() * -1
        return c_entropy