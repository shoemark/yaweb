import os
import re


def striphead(string, n=0, pred=lambda line: True):
    lines = string.split('\n')
    if n < 0:
        n = len(lines) - 1
    for i in range(min(n, len(lines) - 1), 0, -1):
        if pred(lines[i - 1]):
            del lines[i - 1]
    return os.linesep.join(lines)


def striptail(string, n=0, pred=lambda line: True):
    lines = string.split('\n')
    if n < 0:
        n = len(lines) - 1
    for i in range(len(lines) - 1, max(len(lines) - 1 - n, 0), -1):
        if pred(lines[i - 1]):
            del lines[i - 1]
    return os.linesep.join(lines)


def rchomp(string, n=0):
    return striptail(string, n, pred=lambda line: line == '')


def escape_chars(escape_char, chars_to_escape, text):
    def escape(escape_sequence):
        escaped_char = escape_sequence.group(0)[1]
        if re.match(chars_to_escape, escaped_char):
            return escaped_char
        else:
            return escape_sequence.group(0)
    return re.sub('%s.' % escape_char, lambda match: escape(match), text)


def valid_python_ident(string):
    return re.match('^[_A-Za-z][_A-Za-z0-9]*$', string) is not None
