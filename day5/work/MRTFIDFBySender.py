#!/usr/bin/env python

import sys, os
sys.path.append('..')

from mrjob.protocol import JSONValueProtocol
from mrjob.job import MRJob
from term_tools import get_terms

DIRECTORY = "/Users/misha/Documents/Classes/Misc/DataViz/repo/day5/work/idf_parts"

class MRTFIDFBySender(MRJob):
    INPUT_PROTOCOL = JSONValueProtocol
    OUTPUT_PROTOCOL = JSONValueProtocol

    def mapper(self, key, email):
        for term in get_terms(email['text']):
            yield {'term': term, 'sender': email['sender']}, 1

    def reducer_init(self):
        self.idfs = {}
        for fname in os.listdir(DIRECTORY): # look through file names in the directory
            with open(os.path.join(DIRECTORY, fname)) as file: # open a file
                for line in file: # read each line in json file

                    term_idf = JSONValueProtocol.read(line)[1] # parse the line as a JSON object
                    self.idfs[term_idf['term']] = term_idf['idf']

    def reducer(self, term_sender, howmany):
        tfidf = sum(howmany) * self.idfs[term_sender['term']]
        yield None, {'term_sender': term_sender, 'tfidf': tfidf}

if __name__ == '__main__':
        MRTFIDFBySender.run()
