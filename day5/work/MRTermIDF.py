#!/usr/bin/env python

import sys, math
sys.path.append('..')

from mrjob.protocol import JSONValueProtocol
from mrjob.job import MRJob
from term_tools import get_terms

NUMDOCS = 516893.0

class MRTermIDF(MRJob):
    INPUT_PROTOCOL = JSONValueProtocol
    OUTPUT_PROTOCOL = JSONValueProtocol

    def mapper(self, key, email):
        for term in set(get_terms(email['text'])):
            yield term, 1

    def reducer(self, term, occurrences):
        yield None, {'term': term, 'idf': math.log(NUMDOCS / sum(occurrences))}

if __name__ == '__main__':
        MRTermIDF.run()

