#! /usr/bin/env python

# TODO:
#   - chunk tags, specialized weaving
#   - command presets
#   - command error propagation, noweb file location back-resolution
#   - mapping noweb file location <-> source code file location
#   - caching/makefiles
#   - multiline options, code options after name field
#   - language option derivation
#   - use namespaces for markup, filter, backend stages
#   - registerable macros, to be expanded at stage execution time
#
# XXX:
#  - factor out regular expressions, compile beforehand, use printf-like templates
#  - only check the regular expression matches that are actually needed, not all at once
#  - switch to global makers, tanglers, weavers lists and remove dependers arguments.
#  - use `@' as escape char

import imp
import importlib

from .lib import ast
from .lib import toolchain
#from .lib import toolchain_debug
from .transform.meta import meta


def YawebState():
    yaweb = imp.new_module('yaweb')

    chunkutils = importlib.import_module('.lib.chunkutils', __package__)
    for k, v in chunkutils.__dict__.items():
        setattr(yaweb, k, v)

    return yaweb


class Yaweb(object):
    def __init__(self, frontend=[], transform=[], backend=[], **params):
        self.frontends = []
        for fe in frontend:
            self.frontends.append(self._load_tool(fe, ['', 'frontend']))

        self.transforms = []
        for tf in transform:
            self.transforms.append(self._load_tool(tf, ['', 'transform']))

        self.backends = []
        for be in backend:
            self.backends.append(self._load_tool(be, ['', 'backend']))

    def _load_tool(self, plugin_desc, parent_packages=[]):
        try:
            name, args, kwargs = plugin_desc

            if '.' in name:
                pkg_name, class_name = name.rsplit('.', 1)
            else:
                pkg_name = name
                class_name = name

            module = importlib.import_module(
                '.'.join(parent_packages + [pkg_name]),
                __package__
            )
            return module.__dict__[class_name](*args, **kwargs)
        finally:
                pass

    def __call__(self):
        # TODO: combined pipeline should be like this:
        #   - create a list of main stages
        #       - populate with the stages requested via command line
        #   - if meta chunks are enabled:
        #       - fixed-function pre-pass Pipeline that evaluates meta chunks
        #       - buffer chunks before continuing
        #       - allow meta chunks to manipulate list of main stages
        #   - build the pipeline, feed it the buffered or generated chunks

        yaweb = YawebState()
        yaweb.load_tool = lambda desc, pkgs=[]: self._load_tool(desc, pkgs)
        yaweb.tools = self.transforms + self.backends

        meta_data_src = dict(yaweb=yaweb)

        chunks_src = (chunk for fe in self.frontends for chunk in fe())

        bootstrap_tools = meta()
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
    raise RuntimeError('not implemented yet')


if __name__ == '__main__':
    main(sys.argv[1:])
