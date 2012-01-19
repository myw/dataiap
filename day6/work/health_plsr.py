#!/usr/bin/env python

import sys, csv

import numpy as np
import scipy as sp
import scipy.stats as st
import matplotlib.pyplot as plt

from operator import itemgetter

# PyChem multivariable analytics
import mva.chemometrics as chm

_label_names = ['FIPS', 'State', 'County', 'Unreliable' ]

def load_data(file_x, file_y):
    read_file = lambda filename: \
        np.genfromtxt(filename,
                   delimiter      = ',',
                   dtype          = None,
                   names          = True)

    data_x = read_file(file_x)
    data_y = read_file(file_y)

    # Strip out state-wide data and unreliable data
    valid_conditions = np.logical_and(data_x['County']     != '',
                                      data_y['Unreliable'] == '')


    return data_x[valid_conditions], data_y[valid_conditions]


def plot_data(data_x, data_y):

    y = data_y['YPLL_Rate']

    measure_names = [name for name in data_x.dtype.fields.keys() if name not in _label_names]

    rows = 3.0;
    cols = np.ceil(len(measure_names) / rows)

    corrs = {}

    fig = plt.figure(figsize=(16,10))

    ytick_values = np.arange(min(y), max(y), (max(y) - min(y)) / 4)

    for mx, measure in enumerate(measure_names):
        x = data_x[measure]

        xtick_values = np.arange(min(x), max(x), (max(x) - min(x)) / 4)

        valid_terms = np.logical_and(np.logical_not(np.isnan(x)), np.logical_not(np.isnan(y)))
        corrs[measure] = st.pearsonr(x[valid_terms], y[valid_terms])[0]

        subplot = fig.add_subplot(rows, cols, mx + 1)
        subplot.scatter(x, y)
        subplot.set_title(measure)
        subplot.set_xticks(xtick_values)
        subplot.set_yticks(ytick_values)
        # TODO: make pretty: no edges, reposition subplots, etc
        # TODO: add line of best fit and r^2

    # TODO: save figure
    # plt.show()

    for name, corr in sorted(corrs.iteritems(), key=lambda v: abs(v[1]), reverse=True):
        print name, corr

def filter_data(data_x, data_y):
    corr_cutoff = 0.3

    good_measures = []

    y = data_y['YPLL_Rate'].reshape(len(data_y), 1)

    all_valid_terms = np.logical_not(np.isnan(y))

    measure_names = [name for name in data_x.dtype.fields.keys() if name not in _label_names]
    for measure in measure_names:
        x = data_x[measure].reshape(len(data_x), 1)

        valid_terms = np.logical_and(np.logical_not(np.isnan(x)), np.logical_not(np.isnan(y)))

        corr = st.pearsonr(x[valid_terms], y[valid_terms])[0]

        if corr > corr_cutoff:
            good_measures.append(measure)
            all_valid_terms = np.logical_and(all_valid_terms, valid_terms)

    x = np.asarray(data_x[good_measures].tolist())

    # return only the rows that are non-nan and safe for everyone
    all_valid_terms = all_valid_terms.squeeze()
    return x[all_valid_terms, :], y[all_valid_terms, :], good_measures, all_valid_terms

_abbrevs = {
    "Alabama":        "AL",
    "Alaska":         "AK",
    "Arizona":        "AZ",
    "Arkansas":       "AR",
    "California":     "CA",
    "Colorado":       "CO",
    "Connecticut":    "CT",
    "Delaware":       "DE",
    "Florida":        "FL",
    "Georgia":        "GA",
    "Hawaii":         "HI",
    "Idaho":          "ID",
    "Illinois":       "IL",
    "Indiana":        "IN",
    "Iowa":           "IA",
    "Kansas":         "KS",
    "Kentucky":       "KY",
    "Louisiana":      "LA",
    "Maine":          "ME",
    "Maryland":       "MD",
    "Massachusetts":  "MA",
    "Michigan":       "MI",
    "Minnesota":      "MN",
    "Mississippi":    "MS",
    "Missouri":       "MO",
    "Montana":        "MT",
    "Nebraska":       "NE",
    "Nevada":         "NV",
    "New Hampshire":  "NH",
    "New Jersey":     "NJ",
    "New Mexico":     "NM",
    "New York":       "NY",
    "North Carolina": "NC",
    "North Dakota":   "ND",
    "Ohio":           "OH",
    "Oklahoma":       "OK",
    "Oregon":         "OR",
    "Pennsylvania":   "PA",
    "Rhode Island":   "RI",
    "South Carolina": "SC",
    "South Dakota":   "SD",
    "Tennessee":      "TN",
    "Texas":          "TX",
    "Utah":           "UT",
    "Vermont":        "VT",
    "Virginia":       "VA",
    "Washington":     "WA",
    "West Virginia":  "WV",
    "Wisconsin":      "WI",
    "Wyoming":        "WY"}

# assign color codes in a random order
_color_codes = dict( (abbrev, cx) for cx, abbrev in enumerate(_abbrevs) )

def plot_pls(model, measures, good_measure_names):

    nrows = measures['FIPS'].shape[0]
    scores = model['plsscores'][:nrows,:2]

    fig = plt.figure(figsize=(12,7.5))
    subplot = fig.add_subplot(111)

    # grid basics
    subplot.axhline(color='k', alpha=0.2)
    subplot.axvline(color='k', alpha=0.2)


    dot_scale = 30.0
    pop = measures['Population'] / measures['Population'].mean() * dot_scale

    states = [_color_codes[state] for state in measures['State']]

    # XLoadings
    XL = model['P'][:,:2]

    mean_norm_loading = np.mean(map(sp.linalg.norm, XL))
    mean_norm_score = np.mean(map(sp.linalg.norm, scores[:,:2]))

    x_loading_color = "#37ABC8"
    for px, point in enumerate(XL):
        point *= mean_norm_score / mean_norm_loading
        subplot.plot([0, point[0]], [0, point[1]], '-', color=x_loading_color,
                     linewidth=3)
        subplot.plot([point[0]], [point[1]], 's', color=x_loading_color,
                     markersize=10)
        subplot.text(point[0], point[1], good_measure_names[px], size='xx-large',
                ha='left', va='top', color=x_loading_color, weight='bold',
                zorder = 1000)

    # YLoadings
    y_loading_color = "#5D7593"
    point = model['Q'][:2]
    point *= mean_norm_score / sp.linalg.norm(point)
    subplot.plot([0, point[0]], [0, point[1]], '-', color=y_loading_color,
                 linewidth=5)
    subplot.plot([point[0]], [point[1]], 's', color=y_loading_color,
                 markersize=10)
    subplot.text(point[0], point[1], 'YPLL_Rate', size='xx-large',
                 ha='left', va='bottom', color=y_loading_color, weight='bold')

    # Scores
    subplot.scatter(scores[:,0], scores[:,1], 
            s = pop,
            c = '#D97E72',
            edgecolor='none', alpha=0.3)

    # Labels
    for ix, point in enumerate(scores[:,:2]):
        if pop[ix]/dot_scale > 10:
            label = "%s\n%s" % (measures['County'][ix], _abbrevs[measures['State'][ix]])
            subplot.text(point[0], point[1], label, size='medium', ha='center',
                    va='center')

    subplot.set_xlabel('PC1 (A. U.)', fontsize='xx-large')
    subplot.set_ylabel('PC2 (A. U.)', fontsize='xx-large')
    subplot.set_aspect('equal')

    plt.savefig('biplot.pdf', format='pdf')

def do_plsr(file_x, file_y):

    data_x, data_y = load_data(file_x, file_y)

    # plot_data(data_x, data_y)

    x, y, good_measures, valid_terms = filter_data(data_x, data_y)

    n_factors = min((x.shape[0] - 1, x.shape[1]))

    # replicate the data for the cv, just to let it run
    mask = np.vstack((np.zeros(y.shape), np.ones(y.shape)))
    x = np.vstack((x, x))
    y = np.vstack((y, y))

    pls = chm.pls(x, y, mask, n_factors, type = 1)

    # plot the reduced data
    plot_pls(pls, data_x[valid_terms], good_measures)

    return pls

def main():
    do_plsr(sys.argv[1], sys.argv[2])

if __name__ == "__main__":
    main()
