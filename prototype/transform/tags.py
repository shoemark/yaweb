from ..lib.toolchain import ContentTool

import re


class TagsFilter(ContentTool):
    def __init__(self, tags=['.*'], default_tag=[], *args, **kwargs):
        super(TagsFilter, self).__init__()
        self.tags_spec = tags
        self.default_tag = default_tag

    def _tags(self, chunk):
        tags = []
        for k, v in chunk.attrib.items():
            if v:
                tags.append('%s=%s' % (str(k), str(v)))
            else:
                tags.append('%s' % str(k))
        return tags

    def process_chunk(self, chunk, meta_data):
        for tags in [self._tags(chunk), self.default_tag]:
            for tag_spec in self.tags_spec:
                for tag in tags:
                    if tag_spec.startswith('!'):
                        if re.search('^%s$' % tag_spec[1:], tag):
                            return []
                    else:
                        if re.search('^%s$' % tag_spec, tag):
                            return chunk

        return chunk


def tags(*args, **kwargs):
    return TagsFilter(*args, **kwargs)
