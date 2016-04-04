from ..lib.toolchain import ContentTool

import sys


class Dumper(ContentTool):
    def __init__(self):
        super(Dumper, self).__init__()

    def process_chunk(self, chunk, meta_data):
        sys.stderr.write('%r\n' % chunk)
        return chunk


def dump(*args, **kwargs):
    return Dumper()
