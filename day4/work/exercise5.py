#!/usr/bin/env python

# Per-sender TF-IDF with 2-grams

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

def group_in_grams(n, words):

    grams = []

    for wx in xrange(len(words) - n + 1):
        grams.append(' '.join(words[wx:(wx + n)]))

    return grams

def walk_emails(folder):

    sender_tf = defaultdict(Counter)
    sender_counts = Counter()

    for e in EmailWalker(folder):
        terms_in_email = reasonable_words(e['text'].split()) # split the email text using whitespaces

        terms_in_email = group_in_grams(3, terms_in_email)

        sender_tf[e['sender']].update(terms_in_email)
        sender_counts[e['sender']] += 1

    # Count all the senders that every term was sent by
    allterms = Counter()
    for sender_terms in sender_tf.itervalues():
        allterms.update(sender_terms.keys())

    # From the counts, compute the IDFs
    idfs = {}
    nsenders = len(sender_tf) # num of keys is num of senders
    for term, sender_count in allterms.iteritems():
        idfs[term] = math.log(nsenders / (1.0 + sender_count))

    # Filter down to most frequent senders
    top_senders = sorted(sender_counts.items(), key=itemgetter(1), reverse=True)[:20];

    # Combine TFs and IDFs to make TFIDFs
    tfidfs = defaultdict(list)
    for sender, count in top_senders:
        for term, tf in sender_tf[sender].iteritems():
            tfidfs[sender].append((term, tf * idfs[term]))

    # Display 
    for sender, count in top_senders:
        print sender, count

        sorted_by_count_top20 = sorted(tfidfs[sender], key=itemgetter(1), reverse=True)[:20]
        for pair in sorted_by_count_top20:
            print '\t', pair

def main():
    walk_emails(sys.argv[1])
        
if __name__ == "__main__":
    main()
