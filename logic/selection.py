import pandas as pd
import numpy as np
import math as mt

class Selector:

    def aplicar_seleccion_numerica(self, df):
        n_result = {}
        n_entropias = []
        total_entropia = round(self.seleccionar_atributos_numericos(df), 3)
        n_result['Características'] = 'Entropías'
        n_result['General'] = total_entropia
        for i in df.columns:
            entropia = round(self.seleccionar_atributos_numericos(df.drop(i, axis = 1).copy()),3)
            n_entropias.append(entropia)
            n_result['Sin ' + i] = entropia

        n_entropias = np.array(n_entropias)
        to_substract = np.ones(len(n_entropias))
        to_substract *= total_entropia
        substracts = np.abs(to_substract - n_entropias)
        min_sub = substracts.min()
        indices = np.where(substracts == min_sub)
        atributos = list(df.columns[indices])
        atributos_a_eliminar = atributos[0]
        df = df.drop([atributos_a_eliminar], axis = 1).copy()
        df.to_csv('static/generated/selecting.csv', index = False)
        return n_result, atributos_a_eliminar, substracts

    def aplicar_seleccion_categorica(self, df, filename):
        c_select_for_num = False
        c_result = {}
        c_entropias = []
        c_num_atributos = []
        total_entropia = round(self.seleccionar_atributos_categoricos(df), 3)
        c_result['Características'] = ['Entropías', 'Número de categorías']
        c_result['General'] = [self.seleccionar_atributos_categoricos(df), 0]
        for i in df.columns:
            info = []
            entropia = round(self.seleccionar_atributos_categoricos(df.drop(i, axis = 1).copy()), 3)
            num_atributos = df[i].value_counts().count()
            c_num_atributos.append(num_atributos)
            c_entropias.append(entropia)
            info.append(entropia)
            info.append(num_atributos)
            c_result['Sin ' + i] = info
        c_entropias = np.array(c_entropias)
        to_substract = np.ones(len(c_entropias))
        to_substract *= total_entropia
        substracts = np.abs(to_substract - c_entropias)
        min_entropia = substracts.min()
        indices = np.where(substracts == min_entropia)
        atributos = df.columns[indices]
        atributos = list(atributos)
        atributos_a_eliminar = atributos[0]
        if(len(atributos) > 1):
            c_num_atributos = np.array(c_num_atributos)
            num_atributos_a_comparar = c_num_atributos[indices]
            max_num = num_atributos_a_comparar.max()
            index_to_erase = np.where(num_atributos_a_comparar == max_num)
            atributos_a_eliminar = atributos[index_to_erase[0][0]]
            c_select_for_num = True
        df = df.drop([atributos_a_eliminar], axis = 1).copy()
        df.to_csv('static/generated/selecting.csv', index = False)
        return c_result, atributos_a_eliminar, c_select_for_num, substracts

    def seleccionar_atributos_numericos(self, df):
        np_array = df.values
        max_values = []
        for i in range(0, len(np_array[0,:])):
            max_values.append(np_array[:,i].max()-np_array[:,i].min() )
        matriz_entropia = np.zeros((df.shape[0],df.shape[0]))
            
        for i in range(0, len(matriz_entropia[0])):
            for j in range(0, len(matriz_entropia[0])):
                if(j > i):
                    '''print ("j: "+ str(j)+", i: "+str(i))
                    print(" np[:i] " + str((np_array[i,:])))
                    print(" np[:j] " + str((np_array[j,:])))
                    print(" np[:i] - np[:j] " + str((np_array[i,:] - np_array[j,:])))
                    print ("max_values: "+ str(max_values))'''
                    resultado_distancia = ((((np_array[i,:] - np_array[j,:]) / max_values) ** 2).sum()) ** (1/2)
                    #print("resultado distancia"+str(resultado_distancia))
                    resultado_similitud = np.exp(-0.5 * resultado_distancia)
                    #print("resultado similitud"+str(resultado_similitud))
                    n = resultado_similitud
                    if(n != 0 and n!= 1):
                        matriz_entropia[i][j] = n * np.log2(n) + (1 - n) * np.log2(1 - n)
        n_entropia = matriz_entropia.sum() * -1
        #print(matriz_entropia)
        return n_entropia

    def seleccionar_atributos_categoricos(self, df):
        matriz_de_similitud = np.zeros((len(df), len(df)))
        matriz_entropia = matriz_de_similitud.copy()
        for i in range(0, len(matriz_de_similitud[0])):
            for j in range(0, len(matriz_de_similitud)):
                if(j > i):
                    matriz_de_similitud[i][j] = ((df.iloc[i,:] == df.iloc[j,:]).sum())/len(df.iloc[i,:])
                    n = matriz_de_similitud[i][j]
                    if(n != 0 and n!= 1):
                        matriz_entropia[i][j] = n * np.log2(n) + (1 - n) * np.log2(1 - n)                  
        
        c_entropia = matriz_entropia.sum() * -1
        return c_entropia