import sys
from .yaweb import Yaweb
from .lib.args import parse_args


def main(argv):
    args, kwargs = parse_args(argv)

    kwargs['frontend'] = [
        ('noweb_tool', [], {'extended_syntax': True})
    ]
    kwargs['backend'] = [
        ('noweb_tool', [], {})
    ]

    yaweb = Yaweb(*args, **kwargs)
    yaweb()


if __name__ == '__main__':
    main(sys.argv[1:])
