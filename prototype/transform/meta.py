from ..lib import ast
from ..lib.toolchain import Toolchain, SideEffectsTool, Fence
from .xref_use import xref_use


class MetaProcessor(SideEffectsTool):
    def __init__(self):
        super(MetaProcessor, self).__init__()

    def process_chunk(self, chunk, meta_data):
        if ast.is_element_type(chunk, ast.Chunk) \
                and chunk.get('lang', '') == 'python' \
                and chunk.get('meta') is not None \
                and chunk.get('meta') is not False:
            yaweb = meta_data['yaweb']
            input = yaweb.tangle(chunk, meta_data)
            # FIXME: This is unversioned access and breaks reproducibility in
            # interactive mode
            exec(input, yaweb.__dict__)


def meta(*args, **kwargs):
    return Toolchain([xref_use(), Fence(), MetaProcessor(), Fence()])
