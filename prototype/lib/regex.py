import re


class Searcher(object):
    def __init__(self):
        self.match = None

    def search(self, pattern, text):
        self.match = re.search(pattern, text)
        return self.match
