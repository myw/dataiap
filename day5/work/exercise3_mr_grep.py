#!/usr/bin/env python

# use MapReduce to do an email grep 

import sys, re
sys.path.append('..')

from mrjob.protocol import JSONValueProtocol
from mrjob.job import MRJob

class MREmailGrep(MRJob):
    INPUT_PROTOCOL = JSONValueProtocol
    OUTPUT_PROTOCOL = JSONValueProtocol

    def configure_options(self):
        super(MREmailGrep, self).configure_options()
        self.add_passthrough_option(
            '--regex', type='str', default='.', help='The re to match an email for')

    def mapper(self, key, email):
        for line in email['text'].split('\n'):
            if re.search(self.options.regex, line):
                yield {'sender': email['sender'], 'subject': email['subject']}, line

    def reducer(self, email_info, lines):
        yield None, {'sender':  email_info['sender'],
                     'subject': email_info['subject'],
                     'matches': list(lines)}

if __name__ == '__main__':
        MREmailGrep.run()

