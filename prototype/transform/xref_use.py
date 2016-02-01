from ..lib.toolchain import Toolchain, MetaDataTool
from ..lib.weaklist import WeakList

from weakref import WeakKeyDictionary, WeakSet


class UsesIndex(MetaDataTool):
    def __init__(self):
        super(UsesIndex, self).__init__(['uses'], dict(uses=WeakKeyDictionary()))

    def add_chunk(self, chunk, old_meta_data, new_meta_data):
        for use in chunk.findall('Use'):
            used_name = use.get('chunk_name')
            new_meta_data['uses'].setdefault(chunk, list()).append(used_name)


class UsedByIndex(MetaDataTool):
    def __init__(self):
        super(UsedByIndex, self).__init__(['used_by'], dict(used_by={}))

    def add_chunk(self, chunk, old_meta_data, new_meta_data):
        for use in chunk.findall('Use'):
            used_name = use.get('chunk_name')
            new_meta_data['used_by'].setdefault(used_name, WeakList()).append(chunk)


class ChunksByName(MetaDataTool):
    def __init__(self):
        super(ChunksByName, self).__init__(['chunks_by_name'], dict(chunks_by_name={}))

    def add_chunk(self, chunk, old_meta_data, new_meta_data):
        chunk_name = chunk.get('chunk_name')
        if chunk_name:
            new_meta_data['chunks_by_name'].setdefault(chunk_name, WeakList()).append(chunk)


def xref_use(*args, **kwargs):
    return Toolchain([UsesIndex(), UsedByIndex(), ChunksByName()])
