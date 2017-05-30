from ..lib import ast
from ..lib.toolchain import ContentTool

import sys
import re
import pygments
import pygments.lexers
from pygments.token import Token


class Lexer(ContentTool):
    def __init__(self):
        super(Lexer, self).__init__()

    def process_chunk(self, chunk, meta_data):
        result = chunk

        if chunk.get('lang'):
            result = lex_pygments(chunk)

        yaweb = meta_data['yaweb']
        if 'lex' in yaweb.__dict__:
            result = yaweb.__dict__['lex'](result, meta_data)

        return result


def lex_pygments(chunk):
    #lexer = pygments.lexers.get_lexer_by_name(chunk.get('lang'), encoding='utf-8', outencoding='utf-8')
    lexer = pygments.lexers.get_lexer_by_name(chunk.get('lang'))

    elements = list(chunk)

    result = ast.clone(chunk)
    for element in list(result):
        result.remove(element)

    for element in elements:
        if element.tag == 'Text' or element.tag == 'Code':
            # Pygments appearantly strips line breaks at the beginning,
            # so save leading white space (for example, after a Use token)
            match = re.search(r'^(?P<white>\s*)(?P<text>|\S.*)$', element.text)
            if match and match.group('white') is not '':
                result.append(ast.Text(text=match.group('white')))
                element.text = match.group('text')

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

                elif pygments.token.is_token_subtype(token, Token.Text) \
                        or pygments.token.is_token_subtype(token, Token.Error):
                    lines = text.split('\n')
                    for line in lines[:-1]:
                        result.append(ast.Text(text=line + '\n'))
                    if lines[-1]:
                        result.append(ast.Text(text=lines[-1]))

                else:
                    sys.stderr.write('lex_pygments: unhandled token %s=%s\n' % (str(token), text))
                    result.append(element)

            # Pygments always terminates lines, even if the original line was not terminated.
            if not element.text.endswith('\n') and result and result[-1].text.endswith(u'\n'):
                result[-1].text = result[-1].text[:-1]

        else:
            result.append(element)

    return result


def lex(*args, **kwargs):
    return Lexer()
