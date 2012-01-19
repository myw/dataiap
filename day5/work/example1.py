#!/usr/bin/env python

import sys
sys.path.append('..')

from collections import defaultdict
from mrjob.protocol import JSONValueProtocol
from term_tools import get_terms

def parse_file(filename):
    words = defaultdict(lambda: 0)

    with open(filename) as input:
        for line in input:
            email = JSONValueProtocol.read(line)[1]
            for term in get_terms(email['text']):
                words[term] += 1

        for word, count in words.items():
            print word, count

def main():
    parse_file(sys.argv[1])

if __name__ == "__main__":
    main()
