from . import ast
from .weaklist import WeakList

from weakref import WeakKeyDictionary
import copy


class Toolchain(object):
    def __init__(self, stages):
        self.stages = stages

    # TODO: each stage needs their own meta data (shallow copying should do) so
    # that re-indexing doesn't destroy a previous stage's state
    def pipe(self, chunks, meta_data={}):
        return reduce(
            lambda state, stage: stage.pipe(state[0], state[1]),
            (stage for stage in self.stages),
            (chunks, meta_data)
        )


# TODO:
#   - add a WeakKeyDictionary containing a WeakList mapping
#       each input chunk to its output chunks
#   - store that input/output map in the tool itself so it dies when the tool
#       does
#   - we can now replicate the output chunks in order, even after updating some
#       chunks
class ContentTool(object):
    def __init__(self, hooks=[]):
        super(ContentTool, self).__init__()
        self.hooks = hooks
        self.iomap = WeakKeyDictionary()

    def pipe(self, chunks, meta_data):
        return self._pipe_chunks(chunks, meta_data), meta_data

    def _pipe_chunks(self, chunks, meta_data):
        self.iomap = WeakKeyDictionary()
        for old_chunk in chunks:
            #old_repr = repr(old_chunk)

            for hook in self.hooks:
                hook.before_process_chunk(old_chunk)

            result = self.process_chunk(old_chunk, meta_data)

            self.iomap.setdefault(old_chunk, WeakList())

            if isinstance(result, list):
                #for new_chunk in result:
                #    self._verify_not_mutated(old_chunk, old_repr, new_chunk)

                for hook in self.hooks:
                    hook.after_chunk_removed(old_chunk)

                for new_chunk in result:
                    self.iomap[old_chunk].append(new_chunk)

                    for hook in self.hooks:
                        hook.after_chunk_added(new_chunk)

                    yield new_chunk

            elif isinstance(result, ast.Chunk):
                #self._verify_not_mutated(old_chunk, old_repr, result)

                if result is old_chunk:
                    self.iomap[old_chunk].append(old_chunk)

                    for hook in self.hooks:
                        hook.after_chunk_unmodified(result)
                else:
                    self.iomap[old_chunk].append(result)

                    for hook in self.hooks:
                        hook.after_chunk_removed(old_chunk)
                        hook.after_chunk_added(result)

                yield result

            elif result is None:
                for hook in self.hooks:
                    hook.after_chunk_removed(old_chunk)

            else:
                # TODO: contract error: bad return value
                raise RuntimeError()

    #def _verify_not_mutated(self, old_chunk, old_repr, new_chunk):
    #    if new_chunk is old_chunk and repr(new_chunk) != old_repr:
    #        # TODO: contract error: chunks are immutable
    #        raise RuntimeError()

    # XXX:
    #   - this computation may not depend on what chunks appeared earlier,
    #       only on the current chunk and the meta_data
    def process_chunk(self, chunk, meta_data):
        return chunk


class MetaAttribTool(object):
    def __init__(self, attrib_names=[]):
        self.attrib_names = attrib_names

    def pipe(self, state):
        # TODO:
        # TODO: dependency management?
        return state


class MetaDataTool(object):
    def __init__(self, names=[], initial_values={}):
        self.names    = names
        self.initial  = initial_values

    def pipe(self, chunks, old_meta_data):
        new_meta_data = copy.copy(old_meta_data)
        new_meta_data.update(copy.deepcopy(self.initial))
        return self._pipe_chunks(chunks, old_meta_data, new_meta_data), new_meta_data

    def _pipe_chunks(self, chunks, old_meta_data, new_meta_data):
        for chunk in chunks:
            self.add_chunk(chunk, old_meta_data, new_meta_data)
            yield chunk

    # process_chunk must be "symmetric"; that enables updatability
    # TODO: add remove() or similar
    # TODO: add on_content_change() or similar
    # TODO: add on_meta_attrib_change() or similar
    # TODO: see to it that remove() is called on object destruction
    def add_chunk(self, chunk, old_meta_data, new_meta_data):
        return new_meta_data


class ContentToolHook(object):
    def before_chunk_process(self, chunk):
        pass

    def after_chunk_added(self, chunk):
        pass

    def after_chunk_removed(self, chunk):
        pass

    def after_chunk_unmodified(self, chunk):
        pass


class PopOnIteration(object):
    def __init__(self, items):
        if not isinstance(items, list):
            raise RuntimeError()
        self.items = items

    def __iter__(self):
        self.items.reverse()
        return self

    def next(self):
        if self.items:
            return self.items.pop()
        else:
            raise StopIteration()


class Fence(object):
    def __init__(self):
        pass

    def pipe(self, chunks, meta_data):
        return PopOnIteration(list(chunks)), meta_data


class SideEffectsTool(object):
    def __init__(self):
        pass

    def pipe(self, chunks, meta_data):
        return self._pipe_chunks(chunks, meta_data), meta_data

    def _pipe_chunks(self, chunks, meta_data):
        for chunk in chunks:
            self.process_chunk(chunk, meta_data)
            yield chunk

    def process_chunk(self, chunk, meta_data):
        pass


class CrossRefs(ContentToolHook):
    pass


class IncrementalCrossRefs(CrossRefs):
    pass


class CompleteCrossRefs(CrossRefs):
    pass


class Index(ContentToolHook):
    pass


class IncrementalIndex(Index):
    pass


class CompleteIndex(Index):
    pass
