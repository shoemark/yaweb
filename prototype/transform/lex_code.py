from ..lib import ast
from ..lib.toolchain import ContentTool

import sys
import re
import pygments
import pygments.lexers
from pygments.token import Token


class CodeLexer(ContentTool):
    def __init__(self):
        super(CodeLexer, self).__init__()

    def process_chunk(self, chunk, meta_data):
        lang = chunk.get('lang')
        if chunk.get('weave') == 'quoted' and lang:
            #yaweb = meta_data['yaweb']
            #elements = yaweb.merge_text_elements(list(chunk))
            elements = list(chunk)

            result = ast.clone(chunk)
            for element in list(result):
                result.remove(element)

            for element in elements:
                #if ast.is_element_type(element, ast.Text):
                if element.tag == 'Text' or element.tag == 'Code':

                    # Pygments appearantly strips line breaks at the beginning,
                    # so save leading white space
                    match = re.search(r'^(?P<white>\s*)(?P<text>|\S.*)$', element.text, re.MULTILINE)
                    if match.group('white') is not '':
                        result.append(ast.Text(text=match.group('white')))
                        element.text = match.group('text')

                    try:
                        for e in _lex_pygments(lang, element):
                            result.append(e)
                    except:
                        result.append(element)
                else:
                    result.append(element)

            return result

        else:
            return chunk


def _lex_pygments(lang, element):
    lexer = pygments.lexers.get_lexer_by_name(lang)

    result = []
    for token, text in pygments.lex(element.text, lexer):
        if pygments.token.is_token_subtype(token, Token.Comment.Special):
            result.append(ast.SpecialComment(text=text))
        elif pygments.token.is_token_subtype(token, Token.Comment):
            result.append(ast.Comment(text=text))

        elif pygments.token.is_token_subtype(token, Token.Operator.Word):
            result.append(ast.WordOperator(text=text))
        elif pygments.token.is_token_subtype(token, Token.Operator):
            result.append(ast.Operator(text=text))

        elif pygments.token.is_token_subtype(token, Token.Punctuation):
            result.append(ast.Punctuation(text=text))

        elif pygments.token.is_token_subtype(token, Token.Keyword):
            result.append(ast.Keyword(text=text))

        elif pygments.token.is_token_subtype(token, Token.Name.Builtin):
            result.append(ast.BuiltinCodeEntityName(text=text))
        elif pygments.token.is_token_subtype(token, Token.Name.Class):
            result.append(ast.ClassName(text=text))
        elif pygments.token.is_token_subtype(token, Token.Name.Constant):
            result.append(ast.ConstantName(text=text))
        elif pygments.token.is_token_subtype(token, Token.Name.Exception):
            result.append(ast.ExceptionName(text=text))
        elif pygments.token.is_token_subtype(token, Token.Name.Function):
            result.append(ast.FunctionName(text=text))
        elif pygments.token.is_token_subtype(token, Token.Name.Label):
            result.append(ast.LabelName(text=text))
        elif pygments.token.is_token_subtype(token, Token.Name.Namespace):
            result.append(ast.NamespaceName(text=text))
        elif pygments.token.is_token_subtype(token, Token.Name.Variable):
            result.append(ast.VariableName(text=text))
        elif pygments.token.is_token_subtype(token, Token.Name):
            result.append(ast.CodeEntityName(text=text))

        elif pygments.token.is_token_subtype(token, Token.Number.Bin):
            result.append(ast.LiteralNumberBin(text=text))
        elif pygments.token.is_token_subtype(token, Token.Number.Oct):
            result.append(ast.LiteralNumberOct(text=text))
        elif pygments.token.is_token_subtype(token, Token.Number.Dec):
            result.append(ast.LiteralNumberDec(text=text))
        elif pygments.token.is_token_subtype(token, Token.Number.Hex):
            result.append(ast.LiteralNumberHex(text=text))
        elif pygments.token.is_token_subtype(token, Token.Number):
            result.append(ast.LiteralNumber(text=text))

        elif pygments.token.is_token_subtype(token, Token.String.Char):
            result.append(ast.LiteralChar(text=text))
        elif pygments.token.is_token_subtype(token, Token.String.Escape):
            result.append(ast.LiteralChar(text=text))
        elif pygments.token.is_token_subtype(token, Token.String):
            result.append(ast.LiteralString(text=text))

        elif pygments.token.is_token_subtype(token, Token.Literal):
            result.append(ast.Literal(text=text))

        elif pygments.token.is_token_subtype(token, Token.Text):
            result.append(ast.Text(text=text))

        else:
            sys.stderr.write('lex_code: unhandled token %s=%s\n' % (str(token), text))

    if not element.text.endswith('\n') and result[-1].text == u'\n':
        del result[-1]

    return result


def lex_code(*args, **kwargs):
    return CodeLexer()
