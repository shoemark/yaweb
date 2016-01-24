import sys
from .yaweb import Yaweb


def main(argv):
    frontend = [
        ('noweb_tool', [], dict(input=sys.stdin, recognize_chunk_opts=True))
    ]
    transform = [
        ('eval', [], dict()),
        ('lex_code', [], dict()),
        ('pretty', [], dict()),
    ]
    backend = [
        ('noweb_tool', [], dict(output=sys.stdout))
    ]

    Yaweb(frontend, transform, backend)()


if __name__ == '__main__':
    main(sys.argv[1:])
