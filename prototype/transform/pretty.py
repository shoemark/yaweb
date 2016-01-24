from ..lib import ast
from ..lib.toolchain import ContentTool


class PrettyPrinter(ContentTool):
    def __init__(self):
        super(PrettyPrinter, self).__init__()

    def process_chunk(self, chunk, meta_data):
        yaweb = meta_data['yaweb']

        if 'pretty_print' in yaweb.__dict__:
            pretty_print = yaweb.__dict__['pretty_print']
        else:
            pretty_print = None

        if pretty_print and chunk.get('weave') == 'quoted':
            result = ast.clone(chunk)
            pretty_print(result)
            return result

        else:
            return chunk


def pretty():
    return PrettyPrinter()
