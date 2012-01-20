#!/usr/bin/env python

import sys
from cStringIO import StringIO

from mrjob.protocol import JSONValueProtocol
from mrjob.job import MRJob
from mrjob.emr import parse_s3_uri

from boto.s3.connection import S3Connection
from term_tools import get_terms

class MRTFIDFBySender(MRJob):
    INPUT_PROTOCOL = JSONValueProtocol
    OUTPUT_PROTOCOL = JSONValueProtocol

    def configure_options(self):
        super(MRTFIDFBySender, self).configure_options()
        self.add_passthrough_option(
            '--idf_loc', type='str', default='',
            help='The s3:// URL for the location of the IDFs')
        self.add_passthrough_option(
            '--aws_access_key_id', type='str', default='',
            help='The access key ID for the AWS account')
        self.add_passthrough_option(
            '--aws_secret_access_key', type='str', default='',
            help='The secret access key for the AWS account')

    def mapper(self, key, email):
        for term in get_terms(email['text']):
            yield {'term': term, 'sender': email['sender']}, 1

    def reducer_init(self):
        self.idfs = {}

        conn = S3Connection(self.options.aws_access_key_id,
                            self.options.aws_secret_access_key)

        # Iterate through the files in the bucket provided by the user
        bucket, folder = parse_s3_uri("s3://" + self.options.idf_loc)
        for key in conn.get_bucket(bucket).list(folder):

            # Load the whole file first, then read it line-by-line: otherwise,
            # chunks may not be even lines
            for line in StringIO(key.get_contents_as_string()): 
                term_idf = JSONValueProtocol.read(line)[1] # parse the line as a JSON object
                self.idfs[term_idf['term']] = term_idf['idf']

    def reducer(self, term_sender, howmany):
        tfidf = sum(howmany) * self.idfs[term_sender['term']]
        yield None, {'sender': term_sender['sender'], 'term': term_sender['term'], 'tfidf': tfidf}

if __name__ == '__main__':
        MRTFIDFBySender.run()
