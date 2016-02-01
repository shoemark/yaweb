from . import regex


def parse_args(argv):
    args   = []
    kwargs = {}

    Re = regex.Searcher()

    for arg in argv:
        if Re.search(r'^--(?P<name>[A-Za-z_][A-Za-z_0-9]*)=(?P<value>.*)$', arg):
            name = Re.match.group('name')
            value = Re.match.group('value')

            if Re.search(r'^(?P<name>[A-Za-z_][A-Za-z_0-9]*)\((?P<args>[^)]*)\)$', value):
                key = Re.match.group('name')
                pos = []
                kws = {}
                for arg in Re.match.group('args').split(','):
                    if Re.search(r'^(?P<key>[A-Za-z_][A-Za-z_0-9]*)=(?P<value>.*)$', arg.strip()):
                        kws.setdefault(Re.match.group('key'), []).append(Re.match.group('value'))
                    else:
                        pos.append(arg)
                arg = (key, pos, kws)
            else:
                arg = value

            kwargs.setdefault(name, []).append(arg)
        elif Re.search(r'^--(?P<name>[A-Za-z_][A-Za-z_0-9]*)$', arg):
            name = Re.match.group('name')
            kwargs.setdefault(name, []).append('')
        else:
            args.append(arg)

    return args, kwargs
