from .textutils import valid_python_ident

from xml.etree import ElementTree as ElementTree


# XXX: Current masterplan:
#  - There are two kinds of nodes contained in chunks, [ContentNode]s and
#    [AnnotationNode]s. A ContentNode contains textual data that may be
#    modified by the toolchain. An AnnotatationNode contains meta data about
#    the chunk or part of it. Nodes may be nested. For example, a text node may
#    be contained within an annotation node. This indicates that a tool in the
#    chain parsed the text node(s) contained in the annotation node and created
#    the annotation out of them. A mapping from each node to its origin in the
#    source web is preserved, as long as new nodes only wrap old nodes.
#  - A helper class is introduced that eases creating new ContentTools.
#    It helps to parse a chunk's content in the following way: First, a set of
#    criteria is specified for nodes to process; second, a set of criteria is
#    specified describing which nodes may be "opened up" to look for the nodes
#    to process. Third, each uninterrupted sequence of matching nodes is fed to
#    the processing function, which is to aggregate the nodes into as many new
#    nodes as it sees fit. Nodes that had to be broken up are removed and lost.


def is_element_type(element, element_type):
    return isinstance(element, element_type)


def to_xml(element):
    return ElementTree.tostring(element)


def clone(element):
    return eval(repr(element))


# Attribs may only contain string keys and string values and may only be
# manipulated by ContentTools.
class SyntaxElement(ElementTree.Element):
    def __init__(self, attrib={}, **extra):
        text = ''
        if 'text' in attrib and attrib['text'] is not None:
            text += attrib['text']
            del attrib['text']
        if 'text' in extra and extra['text'] is not None:
            text += extra['text']
            del extra['text']

        children = []
        if 'children' in attrib:
            children += attrib['children']
            del attrib['children']
        if 'children' in extra:
            children += extra['children']
            del extra['children']

        super(SyntaxElement, self).__init__('None', attrib, **extra)

        self.text = text

        for child in children:
            self.append(child)

    def __repr__(self):
        for bad_attr in ['text', 'children']:
            if self.get(bad_attr):
                del self.attrib[bad_attr]

        attrib = [(k, self.get(k)) for k in sorted(self.attrib.keys())]
        state_desc = ['%s=%r' % (str(k), v) for k, v in attrib if valid_python_ident(str(k))]
        state_desc += ['attrib=%r' % dict([(str(k), repr(v)) for k, v in attrib if not valid_python_ident(str(k))])]

        if self.text:
            state_desc.append('text=%s' % repr(self.text))

        children = list(self)
        if children:
            state_desc.append('children=%s' % repr(children))

        return '%s(%s)' % (self.tag, ', '.join(state_desc))


class Web(SyntaxElement):
    def __init__(self, attrib={}, **extra):
        super(Web, self).__init__(attrib, **extra)
        self.tag = self.__class__.__name__


class Chunk(SyntaxElement):
    def __init__(self, attrib={}, **extra):
        super(Chunk, self).__init__(attrib, **extra)
        self.tag = self.__class__.__name__


# TODO: Rename to `Textual' ?
class Text(SyntaxElement):
    def __init__(self, attrib={}, **extra):
        super(Text, self).__init__(attrib, **extra)
        self.tag = self.__class__.__name__


class NaturalText(Text):
    def __init__(self, attrib={}, **extra):
        super(NaturalText, self).__init__(attrib, **extra)
        self.tag = self.__class__.__name__


class QuotedText(Text):
    def __init__(self, attrib={}, **extra):
        super(QuotedText, self).__init__(attrib, **extra)
        self.tag = self.__class__.__name__


# TODO: Code should inherit QuotedText?
class Code(Text):
    def __init__(self, attrib={}, **extra):
        super(Code, self).__init__(attrib, **extra)
        self.tag = self.__class__.__name__


class Keyword(Text):
    def __init__(self, attrib={}, **extra):
        super(Keyword, self).__init__(attrib, **extra)
        self.tag = self.__class__.__name__


class Comment(Text):
    def __init__(self, attrib={}, **extra):
        super(Comment, self).__init__(attrib, **extra)
        self.tag = self.__class__.__name__


class SpecialComment(Text):
    def __init__(self, attrib={}, **extra):
        super(SpecialComment, self).__init__(attrib, **extra)
        self.tag = self.__class__.__name__


class Literal(Text):
    def __init__(self, attrib={}, **extra):
        super(Literal, self).__init__(attrib, **extra)
        self.tag = self.__class__.__name__


class LiteralChar(Text):
    def __init__(self, attrib={}, **extra):
        super(LiteralChar, self).__init__(attrib, **extra)
        self.tag = self.__class__.__name__


class LiteralString(Text):
    def __init__(self, attrib={}, **extra):
        super(LiteralString, self).__init__(attrib, **extra)
        self.tag = self.__class__.__name__


class LiteralNumber(Text):
    def __init__(self, attrib={}, **extra):
        super(LiteralNumber, self).__init__(attrib, **extra)
        self.tag = self.__class__.__name__


class LiteralNumberBin(Text):
    def __init__(self, attrib={}, **extra):
        super(LiteralNumberBin, self).__init__(attrib, **extra)
        self.tag = self.__class__.__name__


class LiteralNumberOct(Text):
    def __init__(self, attrib={}, **extra):
        super(LiteralNumberOct, self).__init__(attrib, **extra)
        self.tag = self.__class__.__name__


class LiteralNumberDec(Text):
    def __init__(self, attrib={}, **extra):
        super(LiteralNumberDec, self).__init__(attrib, **extra)
        self.tag = self.__class__.__name__


class LiteralNumberHex(Text):
    def __init__(self, attrib={}, **extra):
        super(LiteralNumberHex, self).__init__(attrib, **extra)
        self.tag = self.__class__.__name__


class LiteralNumberFloat(Text):
    def __init__(self, attrib={}, **extra):
        super(LiteralNumberFloat, self).__init__(attrib, **extra)
        self.tag = self.__class__.__name__


class Punctuation(Text):
    def __init__(self, attrib={}, **extra):
        super(Punctuation, self).__init__(attrib, **extra)
        self.tag = self.__class__.__name__


class Operator(Code):
    def __init__(self, attrib={}, **extra):
        super(Operator, self).__init__(attrib, **extra)
        self.tag = self.__class__.__name__


class WordOperator(Code):
    def __init__(self, attrib={}, **extra):
        super(WordOperator, self).__init__(attrib, **extra)
        self.tag = self.__class__.__name__


class CodeEntityName(Code):
    def __init__(self, attrib={}, **extra):
        super(CodeEntityName, self).__init__(attrib, **extra)
        self.tag = self.__class__.__name__


class BuiltinCodeEntityName(CodeEntityName):
    def __init__(self, attrib={}, **extra):
        super(BuiltinCodeEntityName, self).__init__(attrib, **extra)
        self.tag = self.__class__.__name__


class ClassName(CodeEntityName):
    def __init__(self, attrib={}, **extra):
        super(ClassName, self).__init__(attrib, **extra)
        self.tag = self.__class__.__name__


class ConstantName(CodeEntityName):
    def __init__(self, attrib={}, **extra):
        super(ConstantName, self).__init__(attrib, **extra)
        self.tag = self.__class__.__name__


class ExceptionName(CodeEntityName):
    def __init__(self, attrib={}, **extra):
        super(ExceptionName, self).__init__(attrib, **extra)
        self.tag = self.__class__.__name__


class FunctionName(CodeEntityName):
    def __init__(self, attrib={}, **extra):
        super(FunctionName, self).__init__(attrib, **extra)
        self.tag = self.__class__.__name__


class LabelName(CodeEntityName):
    def __init__(self, attrib={}, **extra):
        super(LabelName, self).__init__(attrib, **extra)
        self.tag = self.__class__.__name__


class NamespaceName(CodeEntityName):
    def __init__(self, attrib={}, **extra):
        super(NamespaceName, self).__init__(attrib, **extra)
        self.tag = self.__class__.__name__


class VariableName(CodeEntityName):
    def __init__(self, attrib={}, **extra):
        super(VariableName, self).__init__(attrib, **extra)
        self.tag = self.__class__.__name__


class Annotation(SyntaxElement):
    def __init__(self, attrib={}, **extra):
        super(Annotation, self).__init__(attrib, **extra)
        self.tag = self.__class__.__name__


class Use(Annotation):
    def __init__(self, attrib={}, **extra):
        super(Use, self).__init__(attrib, **extra)
        self.tag = self.__class__.__name__
