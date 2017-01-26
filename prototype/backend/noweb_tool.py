from ..lib import ast
from ..lib.toolchain import SideEffectsTool

import sys


class noweb_tool(SideEffectsTool):
    def __init__(self, output=sys.stdout, tangle=False, *args, **kwargs):
        super(noweb_tool, self).__init__()

        if isinstance(output, list) and output and isinstance(output[0], str):
            output = open(output[0], 'w')

        self.source_file = None
        self.chunk_id = 0
        self.output = output
        self.tangle = tangle

    def process_chunk(self, chunk, meta_data):
        self._format(chunk)

    def _format(self, element):
        if ast.is_element_type(element, ast.Web):
            for chunk in element:
                self._format(chunk)

        elif ast.is_element_type(element, ast.Chunk):
            if element.get('weave') is not False:
                source_file = element.get('source_file')
                if source_file:
                    if source_file != self.source_file:
                        self.output.write('@file %s\n' % source_file)
                        self.source_file = source_file

                if element.get('weave') == 'unquoted':
                    self.output.write('@begin docs %s\n' % str(self.chunk_id))
                else:
                    self.output.write('@begin code %s\n' % str(self.chunk_id))
                    name = element.get('chunk_name')
                    quiet = element.get('quiet')
                    self.output.write('@defn %s\n@nl\n' % str(name))

                for text in element:
                    self._format(text)

                if element.get('weave') == 'unquoted':
                    self.output.write('@end docs %s\n' % str(self.chunk_id))
                else:
                    self.output.write('@end code %s\n' % str(self.chunk_id))

                self.chunk_id += 1

        elif ast.is_element_type(element, ast.QuotedText):
                lines = element.text.split('\n')
                text = ['@text %s\n' % line for line in lines[:-1]]
                if lines[-1]:
                    text += ['@text %s\n' % lines[-1]]
                else:
                    text += ['']
                text = '@quote\n%s@endquote\n' % '@nl\n'.join(text)
                self.output.write(text)

        elif ast.is_element_type(element, ast.Text):
            if element.get('pretty_latex') is not None and self.tangle is False:
                lines = element.get('pretty_latex').split('\n')
                text = ['@literal %s\n' % line for line in lines[:-1]]
                if lines[-1]:
                    text += ['@literal %s\n' % lines[-1]]
                else:
                    text += ['']
                text = '@nl\n'.join(text)
                self.output.write(text)
            else:
                lines = element.text.split('\n')
                text = ['@text %s\n' % line for line in lines[:-1]]
                if lines[-1]:
                    text += ['@text %s\n' % lines[-1]]
                else:
                    text += ['']
                text = '@nl\n'.join(text)
                self.output.write(text)

        elif ast.is_element_type(element, ast.Use):
            self.output.write('@use %s\n' % element.get('chunk_name'))
