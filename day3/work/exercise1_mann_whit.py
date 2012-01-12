#!/usr/bin/env python

# Candidates' contributions boxplot and Mann-Whitney U test

import collections, sys, csv, datetime, operator, math
import matplotlib.pyplot as p
import scipy as s
import scipy.stats as st


def parse_contrib(file, *candidates):
    """Parse out contributions of candidates from a file.
    
    Returns a dictionary of lists of date-amount tuples."""

    # Make as many default-counting dictionaries as there are candidates
    reattribs = collections.defaultdict(list)

    # CSV-parse the file
    reader = csv.DictReader(file)

    for row in reader:
        name = row['cand_nm']
        amount = float(row['contb_receipt_amt'])

        # If candidates given and no match, key = False
        if amount >= 0.01:
            key = False

            if candidates: 
            # Some candidates => do any of the candidate arguments match? 
            #                    if so, return the last one; else, false 
                valid_names = [cname for cname in candidates if cname in name]
                key = any(valid_names) and valid_names[0]
            else:
            # No candidates => any candidate
                key = name
        
            if key:
                reattribs[key].append(amount) # Need to compensate for negatives

    
    return reattribs

def setup_plot():
    """Create an empty 10x5 inch plot."""
    fig = p.figure(figsize=(12, 8))
    subplot = fig.add_subplot(111)
    subplot.set_title("Campaign Contribution Distributions")
    subplot.set_yscale('log')

    p.subplots_adjust(bottom = 0.3)

    return subplot

def plot_contrib(fig, contribs):
    """Unpack and plot candidates' contributions, with a label."""

    fig.boxplot(contribs.values(), whis=1)
    fig.set_xticklabels(contribs.keys(), rotation='vertical')
    fig.set_ylim(0.1, 10000)


def save_plot(*candidates):
    """Make a legend and save the file with an identifying name."""

    root = 'contribution_boxplot-'

    if candidates:
        name = root + \
               '_'.join([candidate.lower() for candidate in candidates]) + \
               '.png'
    else:
        name = root + 'all.png'

    p.savefig(name, format='png')

def plot_candidates(filename, *candidates):
    """Given a filename and a list of candidates and contribution ranges, 
       turn it into a plot."""

    with open(filename) as file:
        contribs = parse_contrib(file, *candidates)

        fig = setup_plot()
        plot_contrib(fig, contribs)
        save_plot()

    return contribs

def test_candidates(contribs, *candidates):
    """Run a Mann-Whitney U test on the candidates, given their contributions"""

    def test_pair(names, contribs):
        try:
            n_log_p = -math.log10(st.mannwhitneyu(contribs[0], contribs[1])[1])
        except ValueError:
            n_log_p = float('inf')

        print "%-23s vs. %-23s: -log p = %g" % \
              (names[0], names[1], n_log_p)

    # Determine keys from candidates
    if candidates:
        candidates = \
            filter(
                lambda name: 
                    any(filter(
                        lambda fullname: name in fullname,
                        contribs.iterkeys())),
                candidates)
    else:
        candidates = contribs.keys()

  
    if len(candidates) == 2:
        # Exactly one pair
        test_pair(candidates,
                  (contribs[candidates[0]], contribs[candidates[1]]))
    elif len(candidates) > 2:
        # List of candidates to pair with one another
        for (ix, cand) in enumerate(candidates):
            for cand2 in candidates[ix + 1:]:
                test_pair((cand, cand2),
                          (contribs[cand], contribs[cand2]))
    else:
        raise ValueError("invalid number of arguments: must have either none or more than one candidate")


def main():
    """Plot all candidates for the first given filename."""
    contribs = plot_candidates(sys.argv[1])
    test_candidates(contribs)
    

if __name__ == '__main__':
    main()

