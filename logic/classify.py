import pandas as pd
import numpy as np
import math as mt
from collections import Counter
np.seterr(divide='ignore', invalid='ignore')

class Discretizer:

    def discretize(self, df, attrs, reference, max_int, filename):
        result = {}
        for attr in attrs:
            chi, intervals, counter = self.chi_merge(data = df, attr = attr, label = reference, max_intervals = int(max_int))
            ranges = [element[0] for element in intervals]
            ranges.append(intervals[len(intervals) - 1][1] + 1)
            df['rangos_' + attr] = pd.cut(df[attr], ranges, right = False)
            df = df.drop([attr], axis = 1)
            result[attr] = chi, ranges
        df.to_csv('static/generated/discreting.csv', index = False)
        return result, counter
        


    def chi_merge(self, data, attr, label, max_intervals):
        counter = 0
        distinct_vals = sorted(set(data[attr]))
        # Se obtienen todas las categorías del atributo referencia
        labels = sorted(set(data[label]))
        #Inicializa un contador
        empty_count = {l: 0 for l in labels}
        intervals = [[distinct_vals[i], distinct_vals[i]] for i in range(len(distinct_vals))]
        while len(intervals) > max_intervals: 
            counter += 1
            chi = []
            for i in range(len(intervals)-1):
                # Se calcula el valor de ChiCuadrado
                obs0 = data[data[attr].between(intervals[i][0], intervals[i][1])]
                obs1 = data[data[attr].between(intervals[i+1][0], intervals[i+1][1])]
                total = len(obs0) + len(obs1)
                count_0 = np.array([v for i, v in {**empty_count, **Counter(obs0[label])}.items()])
                count_1 = np.array([v for i, v in {**empty_count, **Counter(obs1[label])}.items()])
                count_total = count_0 + count_1
                expected_0 = count_total*sum(count_0)/total
                expected_1 = count_total*sum(count_1)/total
                chi_ = (count_0 - expected_0)**2/expected_0 + (count_1 - expected_1)**2/expected_1
                chi_ = np.nan_to_num(chi_) 
                chi.append(sum(chi_)) 
            min_chi = min(chi) 
            for i, v in enumerate(chi):
                if v == min_chi:
                    min_chi_index = i 
                    break
            new_intervals = [] 
            skip = False
            done = False
            for i in range(len(intervals)):
                if skip:
                    skip = False
                    continue
                if i == min_chi_index and not done:
                    t = intervals[i] + intervals[i+1]
                    new_intervals.append([min(t), max(t)])
                    skip = True
                    done = True
                else:
                    new_intervals.append(intervals[i])
            intervals = new_intervals

        chi = []
        for i in range(len(intervals)-1):
            obs0 = data[data[attr].between(intervals[i][0], intervals[i][1])]
            obs1 = data[data[attr].between(intervals[i+1][0], intervals[i+1][1])]
            total = len(obs0) + len(obs1)
            count_0 = np.array([v for i, v in {**empty_count, **Counter(obs0[label])}.items()])
            count_1 = np.array([v for i, v in {**empty_count, **Counter(obs1[label])}.items()])
            count_total = count_0 + count_1
            expected_0 = count_total*sum(count_0)/total
            expected_1 = count_total*sum(count_1)/total
            chi_ = (count_0 - expected_0)**2/expected_0 + (count_1 - expected_1)**2/expected_1
            chi_ = np.nan_to_num(chi_) 
            chi.append(sum(chi_))
        return chi, intervals, counter