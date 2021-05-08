import pandas as pd
import numpy as np
import math as mt
from collections import Counter
np.seterr(divide='ignore', invalid='ignore')

class Discretizer:

    def discretize(self, df, atributos, reference, max_int, nombre_archivo):
        result = {}
        for atributo in atributos:
            chi, intervalos, counter = self.chi_merge(data = df, atributo = atributo, label = reference, max_intervalos = int(max_int))
            rangos = [element[0] for element in intervalos]
            rangos.append(intervalos[len(intervalos) - 1][1] + 1)
            df['rangos_' + atributo] = pd.cut(df[atributo], rangos, right = False)
            df = df.drop([atributo], axis = 1)
            result[atributo] = chi, rangos
        df.to_csv('static/generated/discreting.csv', index = False)
        return result, counter

    def chi_merge(self, data, atributo, label, max_intervalos):
        counter = 0
        valores_diferentes = sorted(set(data[atributo]))
        # Se obtienen todas las categorías del atributo referencia
        labels = sorted(set(data[label]))
        #Inicializa un contador
        empty_count = {l: 0 for l in labels}
        intervalos = [[valores_diferentes[i], valores_diferentes[i]] for i in range(len(valores_diferentes))]
        while len(intervalos) > max_intervalos: 
            counter += 1
            chi = []
            for i in range(len(intervalos)-1):
                # Se calcula el valor de ChiCuadrado
                obs0 = data[data[atributo].between(intervalos[i][0], intervalos[i][1])]
                obs1 = data[data[atributo].between(intervalos[i+1][0], intervalos[i+1][1])]
                total = len(obs0) + len(obs1)
                count_0 = np.array([v for i, v in {**empty_count, **Counter(obs0[label])}.items()])
                count_1 = np.array([v for i, v in {**empty_count, **Counter(obs1[label])}.items()])
                count_total = count_0 + count_1
                esperado_0 = count_total*sum(count_0)/total
                esperado_1 = count_total*sum(count_1)/total
                chi_ = (count_0 - esperado_0)**2/esperado_0 + (count_1 - esperado_1)**2/esperado_1
                chi_ = np.nan_to_num(chi_) 
                chi.append(sum(chi_)) 
            min_chi = min(chi) 
            for i, v in enumerate(chi):
                if v == min_chi:
                    min_chi_index = i 
                    break
            new_intervalos = [] 
            skip = False
            done = False
            for i in range(len(intervalos)):
                if skip:
                    skip = False
                    continue
                if i == min_chi_index and not done:
                    t = intervalos[i] + intervalos[i+1]
                    new_intervalos.append([min(t), max(t)])
                    skip = True
                    done = True
                else:
                    new_intervalos.append(intervalos[i])
            intervalos = new_intervalos

        chi = []
        for i in range(len(intervalos)-1):
            obs0 = data[data[atributo].between(intervalos[i][0], intervalos[i][1])]
            obs1 = data[data[atributo].between(intervalos[i+1][0], intervalos[i+1][1])]
            total = len(obs0) + len(obs1)
            count_0 = np.array([v for i, v in {**empty_count, **Counter(obs0[label])}.items()])
            count_1 = np.array([v for i, v in {**empty_count, **Counter(obs1[label])}.items()])
            count_total = count_0 + count_1
            esperado_0 = count_total*sum(count_0)/total
            esperado_1 = count_total*sum(count_1)/total
            chi_ = (count_0 - esperado_0)**2/esperado_0 + (count_1 - esperado_1)**2/esperado_1
            chi_ = np.nan_to_num(chi_) 
            chi.append(sum(chi_))
        return chi, intervalos, counter