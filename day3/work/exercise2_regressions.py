#!/usr/bin/env python

import csv, numpy, sys
import matplotlib.pyplot as plt
sys.path.append('..')
import ols

def read_csv(file_name, cols, check_reliable):
    reader = csv.DictReader(open(file_name, 'rU'))
    rows = {} # map "statename__countyname" to the column names in cols
    for row in reader:
        if check_reliable and row['Unreliable'] == "x": # discard unreliable data
            continue
        if row['County'] == "": # ignore the first entry for each state
            continue
        rname = "%s__%s" % (row['State'], row['County'])
        try: # if a row[col] is empty, float(row[col]) throws an exception
            rows[rname] = [float(row[col]) for col in cols]
        except:
            pass
    return rows

def get_arrs(dependent_cols, independent_cols):
    ypll = read_csv("../../datasets/county_health_rankings/ypll.csv", dependent_cols, True)
    measures = read_csv("../../datasets/county_health_rankings/additional_measures_cleaned.csv", independent_cols, False)

    ypll_arr = []
    measures_arr = []
    for key, value in ypll.iteritems():
        if key in measures: # join ypll and measures if county is in both
            ypll_arr.append(value[0])
            measures_arr.append(measures[key])
    return (numpy.array(ypll_arr), numpy.array(measures_arr))

def main():
    dependent_cols = ["YPLL Rate"]
    independent_cols = ["Population", "< 18", "65 and over", "African American",
                        "Female", "Rural", "%Diabetes" , "HIV rate",
                        "Physical Inactivity" , "mental health provider rate",
                        "median household income", "% high housing costs",
                        "% Free lunch", "% child Illiteracy", "% Drive Alone"]

    ypll_arr, measures_arr = get_arrs(dependent_cols, independent_cols)

    fig = plt.figure(figsize=(6, 8))

    subplot = fig.add_subplot(221)
    subplot.scatter(measures_arr[:,6], ypll_arr, color="#1f77b4") # :,6 means all rows of "diabetes"
    subplot.set_title("ypll vs. % of population with diabetes")

    subplot = fig.add_subplot(222)
    subplot.scatter(measures_arr[:,1], ypll_arr, color="#1f77b4") # 1 = age
    subplot.set_title("ypll vs. % population less than 18 years of age")

    subplot = fig.add_subplot(223)
    subplot.scatter(measures_arr[:,10], ypll_arr, color="#1f77b4") # 10 = income
    subplot.set_title("ypll vs. median household income")

    subplot = fig.add_subplot(224)
    subplot.scatter(measures_arr[:,12], ypll_arr, color="#1f77b4") 
    subplot.set_title("ypll vs. % free lunch")

    plt.savefig('scatterplots.png', format='png')

    def best_fit(m, b, x): # calculates y = mx + b
        return m*x + b

    model = ols.ols(ypll_arr, measures_arr[:,6], "YPLL Rate", ["% Diabetes"]) 
    model.summary()
    subplot = fig.add_subplot(221)
    line_ys = [best_fit(model.b[1], model.b[0], x) for x in measures_arr[:,6]]
    subplot.plot(measures_arr[:, 6], line_ys, color="#ff7f0e")

    model = ols.ols(ypll_arr, measures_arr[:,1], "YPLL Rate", ["< 18"])
    model.summary()
    subplot = fig.add_subplot(222)
    line_ys = [best_fit(model.b[1], model.b[0], x) for x in measures_arr[:,1]]
    subplot.plot(measures_arr[:, 1], line_ys, color="#ff7f0e")

    model = ols.ols(ypll_arr, measures_arr[:,10], "YPLL Rate", ["median household income"])
    model.summary()
    subplot = fig.add_subplot(223)
    line_ys = [best_fit(model.b[1], model.b[0], x) for x in measures_arr[:,10]]
    subplot.plot(measures_arr[:, 10], line_ys, color="#ff7f0e")

    model = ols.ols(ypll_arr, measures_arr[:,12], "YPLL Rate", ["free lunch"])
    model.summary()
    subplot = fig.add_subplot(223)
    line_ys = [best_fit(model.b[1], model.b[0], x) for x in measures_arr[:,12]]
    subplot.plot(measures_arr[:, 12], line_ys, color="#ff7f0e")

    plt.savefig('scatter-line.png', format='png')
    
if __name__ == "__main__":
    main()
