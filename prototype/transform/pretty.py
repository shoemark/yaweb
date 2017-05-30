from ..lib import ast
from ..lib.toolchain import ContentTool


class PrettyPrinter(ContentTool):
    def __init__(self, *args, **kwargs):
        super(PrettyPrinter, self).__init__()

        self.weaving = False
        if 'weave' in kwargs:
            self.weaving = True

        self.tangling = False
        if 'tangle' in kwargs:
            self.tangling = True

    def process_chunk(self, chunk, meta_data):
        yaweb = meta_data['yaweb']

        pretty_print = None

        if self.weaving and 'pretty_print' in yaweb.__dict__:
            pretty_print = yaweb.__dict__['pretty_print']

        if self.tangling and 'pretty_print_code' in yaweb.__dict__:
            pretty_print = yaweb.__dict__['pretty_print_code']

        if pretty_print and chunk.get('weave') == 'quoted':
            result = ast.clone(chunk)
            pretty_print(result, meta_data)
            return result

        else:
            return chunk


def pretty(*args, **kwargs):
    return PrettyPrinter(*args, **kwargs)
