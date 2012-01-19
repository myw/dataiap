#!/usr/bin/env python

# use MapReduce to do a word-count by sender

import sys
sys.path.append('..')

from mrjob.protocol import JSONValueProtocol
from mrjob.job import MRJob
from term_tools import get_terms

class MRWordCountSender(MRJob):
    INPUT_PROTOCOL = JSONValueProtocol
    OUTPUT_PROTOCOL = JSONValueProtocol

    def mapper(self, key, email):
        for term in get_terms(email['text']):
            yield (email['sender'], term), 1

    def reducer(self, term, occurrences):
        yield None, {'sender': term[0], 'term': term[1], 'count': sum(occurrences)}

if __name__ == '__main__':
        MRWordCountSender.run()

