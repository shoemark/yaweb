from ..lib.noweb_tool import Lexer, Parser
import sys


class noweb_tool(object):
    def __init__(self, input=sys.stdin, extended_syntax=False, *args, **kwargs):
        self.lexer = Lexer(input, extended_syntax)
        self.parser = Parser(self.lexer)

    def __iter__(self):
        return iter(self.parser)
