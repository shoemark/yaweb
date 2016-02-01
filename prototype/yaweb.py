#! /usr/bin/env python

# TODO:
#   - language option derivation
#   - registerable macros, to be expanded at stage execution time

from .lib import ast
from .lib import toolchain
#from .lib import toolchain_debug
from .lib.args import parse_args
from .transform.meta import meta

import sys
import imp
import importlib


def YawebState():
    yaweb = imp.new_module('yaweb')

    chunkutils = importlib.import_module('.lib.chunkutils', __package__)
    for k, v in chunkutils.__dict__.items():
        setattr(yaweb, k, v)

    return yaweb


class Yaweb(object):
    def __init__(self, *args, **kwargs):
        default_bootstrap = [
            ('meta', [], {})
        ]
        bootstrap  = kwargs.setdefault('bootstrap', default_bootstrap)
        del kwargs['bootstrap']

        default_frontends = [] # TODO
        frontend  = kwargs.setdefault('frontend', default_frontends)
        del kwargs['frontend']

        default_transforms = [
            ('eval', [], {}),
            ('tags', [], {}),
            ('lex_code', [], {}),
            ('pretty', [], {}),
        ]
        transform = kwargs.setdefault('transform', default_transforms)
        del kwargs['transform']

        default_backends = [] # TODO
        backend = kwargs.setdefault('backend', default_backends)
        del kwargs['backend']

        self.bootstrap_tools = []
        for bs in bootstrap:
            self.bootstrap_tools.append(self._load_tool(bs, ['', 'transform'], args, kwargs))

        self.frontends = []
        for fe in frontend:
            self.frontends.append(self._load_tool(fe, ['', 'frontend'], args, kwargs))

        self.transforms = []
        for tf in transform:
            self.transforms.append(self._load_tool(tf, ['', 'transform'], args, kwargs))

        self.backends = []
        for be in backend:
            self.backends.append(self._load_tool(be, ['', 'backend'], args, kwargs))

    def _load_tool(self, desc, parent_packages, g_args, g_kwargs):
        try:
            name, l_args, l_kwargs = desc

            args = l_args

            kwargs = {}
            kwargs.update(g_kwargs)
            kwargs.update(l_kwargs)

            if '.' in name:
                pkg_name, class_name = name.rsplit('.', 1)
            else:
                pkg_name = name
                class_name = name

            module = importlib.import_module(
                '.'.join(parent_packages + [pkg_name]),
                __package__
            )

            return module.__dict__[class_name](**kwargs)
        finally:
                pass

    def __call__(self):
        yaweb = YawebState()
        yaweb.load_tool = lambda desc, pkgs=[]: self._load_tool(desc, pkgs)
        yaweb.tools = self.transforms + self.backends

        meta_data_src = dict(yaweb=yaweb)

        chunks_src = (chunk for fe in self.frontends for chunk in fe)

        bootstrap_tools = toolchain.Toolchain(self.bootstrap_tools)
        chunks_pre, meta_data_pre = bootstrap_tools.pipe(chunks_src, meta_data_src)

        main_tools = toolchain.Toolchain(meta_data_pre['yaweb'].tools)
        chunks_out, meta_data_out = main_tools.pipe(chunks_pre, meta_data_pre)

        if self.backends:
            #web = ast.Web(children=chunks_out)
            #print(repr(web))
            #print(meta_data)
            for chunk in chunks_out:
                pass
        else:
            return ast.Web(children=list(chunks_out))


def main(argv):
    args, kwargs = parse_args(argv)
    yaweb = Yaweb(*args, **kwargs)
    yaweb()


if __name__ == '__main__':
    main(sys.argv[1:])
