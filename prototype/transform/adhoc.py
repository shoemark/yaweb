from ..lib import ast
from ..lib import regex
from ..lib.toolchain import ContentTool
import re


class AdHocChunks(ContentTool):
    def __init__(self):
        super(AdHocChunks, self).__init__()
        self.chunk_id = 0
        self.adhoc_chunk_name = re.compile(r'^[^a-zA-Z0-9]+$')
        self.adhoc_chunk_names = {}

    def process_chunk(self, chunk, meta_data):
        self.chunk_id += 1
        Re = regex.Searcher()

        chunk_name = chunk.get('chunk_name')
        if chunk_name and Re.search(self.adhoc_chunk_name, chunk_name):
            if chunk_name in self.adhoc_chunk_names:
                chunk.set('chunk_name', self.adhoc_chunk_names[chunk_name])
                chunk.set('chunk_name_alias', chunk_name)

        for element in chunk:
            if ast.is_element_type(element, ast.Use):
                chunk_name = element.get('chunk_name')
                if Re.search(self.adhoc_chunk_name, chunk_name):
                    self.adhoc_chunk_names[chunk_name] = '%s %d' % (chunk_name, self.chunk_id)
                    element.set('chunk_name', self.adhoc_chunk_names[chunk_name])
                    element.set('chunk_name_alias', chunk_name)

        return chunk


def adhoc(*args, **kwargs):
    return AdHocChunks()
