from ..lib import ast
from ..lib.toolchain import SideEffectsTool
from ..lib.textutils import splitlines

import sys


class md(SideEffectsTool):
    def __init__(self, output=sys.stdout, flavor='github', *args, **kwargs):
        super(md, self).__init__()

        if isinstance(output, list) and output and isinstance(output[0], str):
            output = open(output[0], 'w')

        self.source_file = None
        self.output = output
        self.flavor = flavor

    def process_chunk(self, chunk, meta_data):
        self._format(chunk)

    def _format(self, element):
        if ast.is_element_type(element, ast.Web):
            for chunk in element:
                self._format(chunk)

        elif ast.is_element_type(element, ast.Chunk):
            if element.get('weave') is not False:
                if element.get('weave') == 'unquoted':
                    pass
                else:
                    name = element.get('chunk_name')
                    if name is not None:
                        self.output.write('`<<%s>>=`\n' % str(name))
                    self.output.write('```%s\n' % element.get('lang', ''))

                for text in element:
                    self._format(text)

                if element.get('weave') == 'unquoted':
                    pass
                else:
                    self.output.write('```\n')

        elif ast.is_element_type(element, ast.Text):
            lines = splitlines(element.text)
            text = '%s' % '\n'.join(lines)
            self.output.write(text)

        elif ast.is_element_type(element, ast.Use):
            self.output.write('<<%s>>\n' % element.get('chunk_name'))
