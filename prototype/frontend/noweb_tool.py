from ..lib import ast
from ..lib import regex
from ..lib.textutils import escape_chars

import re


class Token(object):
    pass


class FileToken(Token):
    def __init__(self, file_name):
        self.file_name = file_name

    def __str__(self):
        return r'@file %s' % self.file_name

    def __repr__(self):
        return r'FileToken(%s)' % (
            repr(self.file_name)
        )


class BeginDocsToken(Token):
    def __init__(self, chunk_id):
        self.chunk_id = chunk_id

    def __str__(self):
        return r'@begin docs %s' % self.chunk_id

    def __repr__(self):
        return r'BeginDocsToken(%s)' % (
            repr(self.chunk_id)
        )


class EndDocsToken(Token):
    def __init__(self, chunk_id):
        self.chunk_id = chunk_id

    def __str__(self):
        return r'@end docs %s' % self.chunk_id

    def __repr__(self):
        return r'EndDocsToken(%s)' % (
            repr(self.chunk_id)
        )


class BeginCodeToken(Token):
    def __init__(self, chunk_id):
        self.chunk_id = chunk_id

    def __str__(self):
        return r'@begin code %s' % self.chunk_id

    def __repr__(self):
        return r'BeginCodeToken(%s)' % (
            repr(self.chunk_id)
        )


class EndCodeToken(Token):
    def __init__(self, chunk_id):
        self.ident = chunk_id

    def __str__(self):
        return r'@end code %s' % self.chunk_id

    def __repr__(self):
        return r'EndCodeToken(%s)' % (
            repr(self.chunk_id)
        )


class DefnToken(Token):
    def __init__(self, chunk_name):
        self.chunk_name = chunk_name

    def __str__(self):
        return r'@defn %s' % self.chunk_name

    def __repr__(self):
        return r'DefnToken(%s)' % (
            repr(self.chunk_name)
        )


class UseToken(Token):
    def __init__(self, chunk_name):
        self.chunk_name = chunk_name

    def __str__(self):
        return r'@use %s' % self.chunk_name

    def __repr__(self):
        return r'UseToken(%s)' % (
            repr(self.chunk_name)
        )


class ChunkOptionsToken(Token):
    def __init__(self, options):
        self.options = options


class TextToken(Token):
    def __init__(self, text):
        self.text = text

    def __str__(self):
        return r'@text %s' % self.text

    def __repr__(self):
        return r'TextToken(%s)' % (
            repr(self.text)
        )


class LiteralToken(Token):
    def __init__(self, text):
        self.text = text

    def __str__(self):
        return r'@literal %s' % self.text

    def __repr__(self):
        return r'LiteralToken(%s)' % (
            repr(self.text)
        )


class NewlineToken(Token):
    def __init__(self):
        pass

    def __str__(self):
        return r'@nl'

    def __repr__(self):
        return r'NewlineToken()'


class UnknownToken(Token):
    def __init__(self, token_id, args=None):
        self.token_id = token_id
        self.args = args

    def __str__(self):
        return r'@%s %s' % (self.token_id, self.args)

    def __repr__(self):
        return r'UnknownToken(%s, %s)' % (
            repr(self.token_id),
            repr(self.args)
        )


class Lexer(object):
    def __init__(self, stream, recognize_chunk_opts=False):
        # static data
        self.stream         = stream
        self.recognize_opts = recognize_chunk_opts

        # regular expressions
        self.TOK_FILE       = re.compile(r'^@file (?P<file_name>.*)$')
        self.TOK_BEGIN_DOCS = re.compile(r'^@begin docs (?P<chunk_id>[0-9]+)$')
        self.TOK_END_DOCS   = re.compile(r'^@end docs (?P<chunk_id>[0-9]+)$')
        self.TOK_BEGIN_CODE = re.compile(r'^@begin code (?P<chunk_id>[0-9]+)$')
        self.TOK_END_CODE   = re.compile(r'^@end code (?P<chunk_id>[0-9]+)$')
        self.TOK_DEFN       = re.compile(r'^@defn (?P<chunk_name>.*)$')
        self.TOK_USE        = re.compile(r'^@use (?P<chunk_name>.*)$')
        self.TOK_TEXT       = re.compile(r'^@text (?P<text>.*)$')
        self.TOK_LITERAL    = re.compile(r'^@literal (?P<text>.*)$')
        self.TOK_NL         = re.compile(r'^@nl$')
        self.TOK_UNKNOWN    = re.compile('^@(?P<token_id>\S*)(?: (?P<args>.*))?$')
        #self.TOK_BEGIN_QUOTE= re.compile(r'^@quote$')
        #self.TOK_END_QUOTE  = re.compile(r'^@endquote$')
        self.TOK_OPTS       = re.compile(r'^@text (?:@\[(?P<options>(?:[^@\[\]]|@.)*))(?:\](?P<text>.*))?$')
        self.TOK_OPTS_CONT  = re.compile(r'^@text (?:(?P<options>(?:[^@\[\]]|@.)*))(?:\](?P<text>.*))?$')
        #self.OPT            = re.compile(r'(?P<option>(?:[^@,]|@.)+)')
        #self.OPT_KEYVAL     = re.compile(r'^(?:\s*(?P<key>(?:[^@=\s]|@.)+)\s*)(=(?P<val>(?:[^@=]|@.)+))?$')

        # lexer state
        self.internal_lineno    = 0
        self.at_chunk_options   = False
        self.in_chunk_options   = False

        self.token_queue    = []

    def __iter__(self):
        return self

    def next(self):
        if self.token_queue:
            return self.token_queue.pop(0)

        line = self.stream.next()

        self.internal_lineno += 1

        Re = regex.Searcher()
        if Re.search(self.TOK_FILE, line):
            self.at_chunk_options = False
            return FileToken(**Re.match.groupdict())

        elif Re.search(self.TOK_BEGIN_DOCS, line):
            self.at_chunk_options = True
            return BeginDocsToken(**Re.match.groupdict())

        elif Re.search(self.TOK_END_DOCS, line):
            self.at_chunk_options = False
            return EndDocsToken(**Re.match.groupdict())

        elif Re.search(self.TOK_BEGIN_CODE, line):
            self.at_chunk_options = True
            return BeginCodeToken(**Re.match.groupdict())

        elif Re.search(self.TOK_END_CODE, line):
            self.at_chunk_options = False
            return EndCodeToken(**Re.match.groupdict())

        elif Re.search(self.TOK_DEFN, line):
            self.at_chunk_options = True
            return DefnToken(**Re.match.groupdict())

        elif Re.search(self.TOK_USE, line):
            self.at_chunk_options = False
            return UseToken(**Re.match.groupdict())

        elif self.recognize_opts \
                and ((self.at_chunk_options and Re.search(self.TOK_OPTS, line))
                        or ((self.in_chunk_options and Re.search(self.TOK_OPTS_CONT, line)))):
            self.at_chunk_options = False
            if Re.match.group('text') is not None:
                self.in_chunk_options = False
                text = Re.match.group('text')
                if text:
                    self.token_queue.append(TextToken(text))
            else:
                self.in_chunk_options = True
            return ChunkOptionsToken(Re.match.group('options'))

        elif Re.search(self.TOK_TEXT, line):
            self.at_chunk_options = False
            return TextToken(**Re.match.groupdict())

        #elif Re.search(self.TOK_LITERAL, line):
        #    self.at_chunk_options = False
        #    return LiteralToken(**Re.match.groupdict()

        elif Re.search(self.TOK_NL, line):
            return NewlineToken(**Re.match.groupdict())

        elif Re.search(self.TOK_UNKNOWN, line):
            self.at_chunk_options = False
            return UnknownToken(**Re.match.groupdict())

        else:
            #raise NowebSyntaxError(self.internal_lineno)
            raise SyntaxError()


class Parser(object):
    def __init__(self, lexer):
        self.lexer = lexer

    def __iter__(self):
        return self

    def next(self):
        cur_file  = None
        cur_line  = None
        cur_chunk = None

        # parser state
        discard_newlines = False

        for token in self.lexer:
            if isinstance(token, FileToken):
                cur_file  = token.file_name
                cur_line  = 1
                cur_chunk = None
                discard_newlines = False

            elif isinstance(token, BeginDocsToken):
                cur_chunk = ast.Chunk()
                cur_chunk.set('lang', 'tex')
                cur_chunk.set('weave', 'unquoted')
                cur_chunk.set('source_file', cur_file)
                cur_chunk.set('source_line_begin', str(cur_line))
                discard_newlines = False

            elif isinstance(token, EndDocsToken):
                self._parse_chunk_opts(cur_chunk)
                cur_chunk.set('source_line_end', str(cur_line - 1))
                discard_newlines = False
                chunk = cur_chunk
                cur_chunk = None
                yield chunk

            elif isinstance(token, BeginCodeToken):
                cur_chunk = ast.Chunk()
                cur_chunk.set('weave', 'quoted')
                cur_chunk.set('source_file', cur_file)
                cur_chunk.set('source_line_begin', str(cur_line))
                discard_newlines = False

            elif isinstance(token, EndCodeToken):
                self._parse_chunk_opts(cur_chunk)
                cur_chunk.set('source_line_end', str(cur_line - 1))
                discard_newlines = False
                chunk = cur_chunk
                cur_chunk = None
                yield chunk

            else:
                if cur_chunk is None:
                    raise SyntaxError()

                if isinstance(token, TextToken):
                    if len(cur_chunk) and isinstance(cur_chunk[-1], ast.Text):
                        cur_chunk[-1].text += token.text
                    else:
                        cur_chunk.append(ast.Text(text=token.text))
                    discard_newlines = False

                elif isinstance(token, ChunkOptionsToken):
                    options = cur_chunk.get('options', '') + token.options
                    cur_chunk.set('options', options)
                    discard_newlines = True

                elif isinstance(token, DefnToken):
                    cur_chunk.set('chunk_name', token.chunk_name)
                    discard_newlines = True

                elif isinstance(token, UseToken):
                    cur_chunk.append(ast.Use(chunk_name=token.chunk_name))
                    discard_newlines = False

                elif isinstance(token, NewlineToken):
                    if not discard_newlines:
                        if len(cur_chunk) and isinstance(cur_chunk[-1], ast.Text):
                            cur_chunk[-1].text += '\n'
                        else:
                            cur_chunk.append(ast.Text(text='\n'))
                    cur_line += 1

        if cur_chunk:
            chunk = cur_chunk
            cur_chunk = None
            yield chunk

        raise StopIteration()

    def _parse_chunk_opts(self, chunk):
        options = dict()

        OPT_DELIMED = re.compile(r'(?P<option>(?:[^@,]|@.)+)')
        OPT_KEYVAL  = re.compile(r'^(?:\s*(?P<key>(?:[^@=\s]|@.)+)\s*)(=(?P<val>(?:[^@=]|@.)+))?$')

        for match in re.finditer(OPT_DELIMED, chunk.get('options', '')):
            option = match.group('option')
            option = escape_chars(r'@', r'[,\]]', option)
            match_keyval = re.search(OPT_KEYVAL, option)
            if match_keyval:
                key = escape_chars(r'@', r'[@=\s]', match_keyval.group('key'))
                val = match_keyval.group('val')
                if val is not None:
                    values = []

                    for value in re.finditer(r'^(?P<value>.+)$', val):
                        value = escape_chars(r'@', r'[@]', value.group('value'))

                        if value in ['true', 'on', 'yes']:
                            values.append(True)
                        elif value in ['false', 'off', 'no']:
                            values.append(False)
                        else:
                            try:
                                values.append(int(value))
                            except ValueError:
                                try:
                                    values.append(float(value))
                                except ValueError:
                                    values.append(value)

                    if len(values) == 0:
                        options[key] = None
                    elif len(values) == 1:
                        options[key] = values[0]
                    else:
                        options[key] = values
                else:
                    options[key] = ''
            else:
                raise SyntaxError()

        for key, value in options.items():
            chunk.set(key, value)

        if chunk.get('options'):
            chunk.attrib.pop('options')

        return options


class noweb_tool(object):
    def __init__(self, input, recognize_chunk_opts=False):
        self.lexer = Lexer(input, recognize_chunk_opts)
        self.parser = Parser(self.lexer)

    def __call__(self):
        return self.parser.next()
