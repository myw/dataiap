#!/usr/bin/env python

import sys
sys.path.append('..')

from mrjob.protocol import JSONValueProtocol
from mrjob.job import MRJob
from term_tools import get_terms

AWS_DIRECTORY = "dataiap-wolfsonm-student55-testbucket/idf_parts"

awskey = "AKIAJEMFAHAMY7PUJ34Q"
awssecret = "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"

from boto.s3.connection import S3Connection

class MRTFIDFBySender(MRJob):
    INPUT_PROTOCOL = JSONValueProtocol
    OUTPUT_PROTOCOL = JSONValueProtocol

    def mapper(self, key, email):
        for term in get_terms(email['text']):
            yield {'term': term, 'sender': email['sender']}, 1

    def reducer_init(self):
        self.idfs = {}
        conn = S3Connection(awskey, awssecret)
        bucket_name, search_string = AWS_DIRECTORY.split('/')
        bucket = conn.get_bucket(bucket_name)

        for key in bucket.list(search_string):

            buffer = ""

            for bytes in key: # iterate through the key, buffering into lines yourself

                buffer += bytes # add to the buffer

                # If our buffer includes any complete lines
                if "\n" in buffer:
                    lines = buffer.split('\n')
                    buffer = lines.pop()

                    for line in lines:
                        term_idf = JSONValueProtocol.read(line)[1] # parse the line as a JSON object
                        self.idfs[term_idf['term']] = term_idf['idf']

    def reducer(self, term_sender, howmany):
        tfidf = sum(howmany) * self.idfs[term_sender['term']]
        yield None, {'term_sender': term_sender, 'tfidf': tfidf}

if __name__ == '__main__':
        MRTFIDFBySender.run()
