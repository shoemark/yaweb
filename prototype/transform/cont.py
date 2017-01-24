from ..lib.toolchain import ContentTool

import sys


class Continue(ContentTool):
    def __init__(self):
        super(Continue, self).__init__()
        self.previous = None

    def process_chunk(self, chunk, meta_data):
        if chunk.get('chunk_name') == '' and self.previous:
            chunk.set('chunk_name', self.previous.get('chunk_name'))
            chunk.set('quiet', True)

        self.previous = chunk

        return chunk


def cont(*args, **kwargs):
    return Continue()
