from ..lib.toolchain import SideEffectsTool
from ..lib.noweb_tool import *

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

    def _format(self, chunk):
        if self.tangle or chunk.get('weave') is not False:
            tokens = []

            source_file = chunk.get('source_file')
            if source_file and source_file != self.source_file:
                tokens.append(FileToken(source_file))
                self.source_file = source_file

            if chunk.get('weave') == 'unquoted':
                tokens.append(BeginDocsToken(self.chunk_id))
            else:
                tokens.append(BeginCodeToken(self.chunk_id))
                if not self.tangle and chunk.get('chunk_name_alias'):
                    chunk_name = chunk.get('chunk_name_alias')
                else:
                    chunk_name = chunk.get('chunk_name')
                tokens.append(DefnToken(chunk_name))
                tokens.append(NewlineToken())

            for element in chunk:
                if ast.is_element_type(element, ast.Use):
                    if not self.tangle and element.get('chunk_name_alias'):
                        chunk_name = element.get('chunk_name_alias')
                    else:
                        chunk_name = element.get('chunk_name')
                    tokens.append(UseToken(chunk_name))

                elif ast.is_element_type(element, ast.QuotedText):
                    tokens.append(BeginQuoteToken())

                    if not self.tangle and element.get('pretty_latex'):
                        lines = element.get('pretty_latex').split('\n')
                        token = LiteralToken
                    else:
                        lines = element.text.split('\n')
                        token = TextToken

                    if lines:
                        for line in lines[:-1]:
                            tokens.append(token(line))
                            tokens.append(NewlineToken())
                        tokens.append(token(lines[-1]))

                    tokens.append(EndQuoteToken())

                elif ast.is_element_type(element, ast.Text) and not ast.is_element_type(element, ast.QuotedText):
                    if not self.tangle and element.get('pretty_latex'):
                        lines = element.get('pretty_latex').split('\n')
                        token = LiteralToken
                    else:
                        lines = element.text.split('\n')
                        token = TextToken

                    if lines:
                        for line in lines[:-1]:
                            tokens.append(token(line))
                            tokens.append(NewlineToken())
                        tokens.append(token(lines[-1]))

            # remove empty text tokens at the end
            while (isinstance(tokens[-1], TextToken) or isinstance(tokens[-1], LiteralToken)) \
                    and not tokens[-1].text:
                del tokens[-1]

            if chunk.get('weave') == 'unquoted':
                tokens.append(EndDocsToken(self.chunk_id))
            else:
                tokens.append(EndCodeToken(self.chunk_id))
            self.chunk_id += 1

            tokens = simplify(tokens)
            self.output.write('\n'.join([str(token) for token in tokens]) + '\n')
