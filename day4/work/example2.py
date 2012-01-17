#!/usr/bin/env python

import sys, math, re
sys.path.append('../../resources/util') # fix this path to work for you!!!!
from email_util import EmailWalker, STOPWORDS
from collections import Counter, defaultdict
from operator import itemgetter

# Precompile regexes
_valid_word = re.compile("^[\"(]?[a-z]+[a-z-']*[a-z][.)]?$")
_non_alpha  = re.compile("[^a-z-]")

def reasonable_words(all_words):

    # Ignore short words and stop words
    min_length = 3

    keep = [_non_alpha.sub('', word.lower())
                for word in all_words
                if len(word) > min_length and
                   word not in STOPWORDS  and 
                   _valid_word.search(word)]

    return keep

def cos_sim(words_a, words_b):

    # loop through terms in sec_scores
    # if term also exists in fam_scores, multiply both tfidf values and 
    # add to numerator
    numerator = 0.0
    for a_key, a_score in words_a.iteritems():
        dotscore = a_score * words_b.get(a_key, 0.0)
        numerator += dotscore

    # compute the l2 norm of each vector
    denominator = 0.0
    norm = lambda vector: \
        math.sqrt(sum(score * score for score in vector));

    denominator = norm(words_a.values()) * norm(words_b.values());
    if denominator <= 0.0:
        denominator = 1.0

    similarity = numerator / denominator
    return similarity


def walk_emails(folder):

    folder_tf = defaultdict(Counter)
    terms_per_folder = defaultdict(set)

    for e in EmailWalker(folder):
        terms_in_email = reasonable_words(e['text'].split()) # split the email text using whitespaces

        folder_tf[e['folder']].update(terms_in_email)

        # For the IDF, this collects all of the terms in each folder
        terms_per_folder[e['folder']].update(terms_in_email)

    # Count all the folders that every term appears in
    allterms = Counter()
    for terms in terms_per_folder.itervalues():
        allterms.update(terms)

    # From the counts, compute the IDFs
    idfs = {}
    nfolders = len(terms_per_folder) # num of keys is num of folders
    for term, folder_count in allterms.iteritems():
        idfs[term] = math.log(nfolders / (1.0 + folder_count))

    # Combine TFs and IDFs to make TFIDFs
    tfidfs = defaultdict(dict)
    for folder, terms in folder_tf.iteritems():
        for term, tf in terms.iteritems():
            tfidfs[folder][term] = (tf * idfs[term])

    # Display 
    seen_folders = set()
    similarities = {}
    for folder, scores in tfidfs.items():
        seen_folders.add(folder)
        for folder2, scores2 in tfidfs.items():
            if folder2 not in seen_folders:
                similarities[(folder, folder2)] = cos_sim(scores, scores2)


    sorted_by_sim_top_20 = sorted(similarities.items(), key=itemgetter(1), reverse=True)[:20]
    for folder_pair, similarity in sorted_by_sim_top_20:
        print folder_pair, similarity

def main():
    walk_emails(sys.argv[1])
        
if __name__ == "__main__":
    main()
