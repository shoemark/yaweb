import re


class Searcher(object):
    def __init__(self):
        self.match = None

    def search(self, pattern, text, *args, **kwargs):
        self.match = re.search(pattern, text, *args, **kwargs)
        return self.match
