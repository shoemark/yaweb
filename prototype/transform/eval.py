from ..lib import ast
from ..lib import regex
from ..lib.textutils import splitlines, striphead, striptail
from ..lib.toolchain import Toolchain, ContentTool, MetaDataTool, Fence
from ..lib.weaklist import WeakList

import sys
import os
import os.path
import re
import subprocess
import hashlib
from weakref import WeakKeyDictionary
from threading import Thread

# TODO: rename to `exec'?


class ChunksByEvalSession(MetaDataTool):
    def __init__(self):
        super(ChunksByEvalSession, self).__init__(
            ['chunks_by_eval_session'],
            dict(chunks_by_eval_session={})
        )

    def add_chunk(self, chunk, old_meta_data, new_meta_data):
        chunk_name = chunk.get('chunk_name')
        if chunk_name:
            new_meta_data['chunks_by_eval_session'].setdefault(chunk_name, WeakList()).append(chunk)

        preamble_name = chunk.get('eval_preamble')
        if preamble_name:
            new_meta_data['chunks_by_eval_session'].setdefault(preamble_name, WeakList()).append(chunk)


class EvalTaskCreator(MetaDataTool):
    def __init__(self):
        super(EvalTaskCreator, self).__init__(
            ['eval_tasks'],
            dict(eval_tasks=WeakKeyDictionary())
        )
        self.presets = {
            'R':                    preset_R,
            'R session':        preset_R_session,
            'coq':                  preset_coq,
            'coq session':      preset_coq_session,
        }
        self.schemes = {
            'shell':                scheme_shell
        }

    #def process_chunk(self, chunk, meta_data):
    def add_chunk(self, chunk, old_meta_data, new_meta_data):
        if chunk.get('eval'):
            # create job
            Re = regex.Searcher()
            if Re.search(r'^([a-z_][a-z_0-9]+)://(.*)$', chunk.get('eval')):
                scheme, command = Re.match.groups()
                if scheme in self.schemes:
                    # TODO: permit code chunks as commands, if of the form `<<chunk_name>>'
                    job = lambda chunk, meta_data: \
                            self.schemes[scheme](command, chunk, meta_data)
                else:
                    # TODO: error: unknown evaluation scheme
                    #return chunk
                    return
            elif chunk.get('eval') in self.presets:
                job = self.presets[chunk.get('eval')]
            else:
                # TODO: error: unknown evaluation preset
                #return chunk
                return

            new_meta_data['eval_tasks'][chunk] = job


class EvaluatorThread(Thread):
    def __init__(self, task, chunk, meta_data):
        super(EvaluatorThread, self).__init__()
        self.task = task
        self.chunk = chunk
        self.meta_data = meta_data

    def run(self):
        self.result = self.task(self.chunk, self.meta_data)


# TODO: consider session mode properly
# TODO: Cache: hash-based, timestamp-based
class EvalTaskRunner(MetaDataTool):
    def __init__(self):
        super(EvalTaskRunner, self).__init__(
            ['eval_task_results'],
            dict(eval_task_results=WeakKeyDictionary())
        )
        self.threads = WeakKeyDictionary()

    def add_chunk(self, chunk, old_meta_data, new_meta_data):
        tasks = [(ch, old_meta_data['eval_tasks'][ch]) \
                    for ch in old_meta_data['eval_tasks'] \
                        if ch not in new_meta_data['eval_task_results']]

        # create threads for the tasks and run them in parallel
        for chunk_, task_ in tasks:
            # wait for a running thread to terminate
            running = [th for ch, th in self.threads.items() if th.isAlive()]
            while len(running) >= 8:
                for th in running:
                    if not th.isAlive():
                        running.remove(th)
                        break
                if running:
                    running[0].join(0.01)

            # create and start new thread
            th = EvaluatorThread(task_, chunk_, old_meta_data)
            th.start()
            self.threads[chunk_] = th

        # retrieve results
        for ch, th in self.threads.items():
            th.join()
            new_meta_data['eval_task_results'][ch] = th.result

        self.threads = WeakKeyDictionary()


class EvalResultAssigner(ContentTool):
    def __init__(self):
        super(EvalResultAssigner, self).__init__()

    def process_chunk(self, chunk, meta_data):
        if chunk in meta_data['eval_task_results']:
            return meta_data['eval_task_results'][chunk]
        else:
            return chunk


def gather_input(chunk, meta_data):
    session_name = chunk.get('eval_preamble')
    if not session_name:
        session_name = chunk.get('chunk_name')

    if session_name:
        session = meta_data['chunks_by_eval_session'][session_name]
        index = session.index(chunk)
        chunks = [ch for ch in session[0:index] if ch.get('chunk_name') == session_name] \
                    + [session[index]]
    else:
        chunks = [chunk]

    preamble = chunks[0:-1]
    input = chunks[-1]

    return preamble, input


def tangle_input(chunk, meta_data, preamble, input):
    yaweb = meta_data['yaweb']

    preamble_t = ''.join([yaweb.tangle(ch, meta_data) for ch in preamble])
    input_t = yaweb.tangle(input, meta_data)

    return preamble_t, input_t


def output(chunk, meta_data, text):
    src_chunk = chunk #ast.clone(chunk)

    out_chunk = ast.Chunk()
    out_chunk.set('weave', 'quoted')

    inherited_props = ['chunk_name']
    for prop in inherited_props:
        if src_chunk.get(prop) is not None:
            out_chunk.set(prop, src_chunk.get(prop))

    for prop in src_chunk.attrib:
        if prop.startswith('out_'):
            out_chunk.set(prop[4:], src_chunk.get(prop))

    out_chunk.append(ast.Text(text=text))

    return src_chunk, out_chunk


class HashDbCache(object):
    def __init__(self):
        pass

    def _cache_file_base(self, command, input):
        dirname = '_yaweb_eval'
        command_hash = hashlib.sha256(command).hexdigest()
        input_hash = hashlib.sha256(input).hexdigest()
        return '%s/%s/%s' % (dirname, command_hash, input_hash)

    def get(self, command, input):
        try:
            base = self._cache_file_base(command, input)

            fret = open(base + '/ret', 'rb')
            ret  = int(fret.read())

            fout = open(base + '/out', 'rb')
            out  = fout.read()

            ferr = open(base + '/err', 'rb')
            err  = ferr.read()

            return ret, out, err
        except:
            return None

    def set(self, command, input, value):
        try:
            base = self._cache_file_base(command, input)

            if not os.path.isdir(base):
                os.makedirs(base)

            ret, out, err = value

            fret = open(base + '/ret', 'wb')
            fret.write(str(ret))

            fout = open(base + '/out', 'wb')
            fout.write(out)

            ferr = open(base + '/err', 'wb')
            ferr.write(err)
        except Exception as x:
            sys.stderr.write(str(x) + '\n')
            pass


def shell_exec(command, input):
    cache = HashDbCache()

    result = cache.get(command, input)
    if result:
        return result
    else:
        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True
        )
        out, err = process.communicate(input)

        ret = process.returncode
        if out is not '' and not out.endswith('\n'):
            out += '\n'
        if err is not '' and not err.endswith('\n'):
            err += '\n'

        result = (ret, out, err)

        cache.set(command, input, result)
        return result


def shell_exec_session(command, preamble, input):
    if preamble:
        ret_, out_, err_ = shell_exec(command, preamble)
        ret, out, err = shell_exec(command, preamble + os.linesep + input)

        lines = splitlines(out)
        out = os.linesep.join(lines[len(splitlines(out_)) - 2:])
        pre = os.linesep.join(lines[:len(splitlines(out_)) - 2])
    else:
        ret, out, err = shell_exec(command, input)
        pre = ''

    return ret, out, err, pre


# TODO: dependency/remake semantics?:
# <<TARGET>>=
# <<DEPENDENCY 1>>
# INPUT
# <<DEPENDENCY 2>>


def preset_R(chunk, meta_data):
    preamble, input = gather_input(chunk, meta_data)
    preamble_t, input_t = tangle_input(chunk, meta_data, preamble, input)
    ret, out, err, pre = shell_exec_session('R --vanilla --quiet --slave', preamble_t, input_t)
    source, result = output(chunk, meta_data, out)
    return [source, result]


def preset_R_session(chunk, meta_data):
    preamble, input = gather_input(chunk, meta_data)
    preamble_t, input_t = tangle_input(chunk, meta_data, preamble, input)
    ret, out, err, pre = shell_exec_session('R --vanilla --quiet', preamble_t, input_t)

    out = striphead(out, n=1, pred=lambda line: line == '> ')
    out = striptail(out, n=1, pred=lambda line: line == '> ')

    source, result = output(chunk, meta_data, out)
    return [source, result]


def preset_coq(chunk, meta_data):
    preamble, input = gather_input(chunk, meta_data)
    preamble_t, input_t = tangle_input(chunk, meta_data, preamble, input)
    ret, out, err, pre = shell_exec_session('coqtop -q 2>&1', preamble_t, input_t)
    source, result = output(chunk, meta_data, out)
    return [source, result]


def preset_coq_session(chunk, meta_data):
    preamble, input = gather_input(chunk, meta_data)
    preamble_t, input_t = tangle_input(chunk, meta_data, preamble, input)
    ret, out, err, pre = shell_exec_session('coqtop -q 2>&1', preamble_t, input_t)

    Re = regex.Searcher()
    COQ_PROMPT = '^(?P<prompt>[\w\s_]* < )(?P<text>.*)$'

    ins = iter(splitlines(input_t))
    outs = splitlines(out)

    if not preamble and len(outs) >= 4:
        # skip banner
        del outs[0:3]

    elif len(outs) >= 1:
        # skip first prompt
        if Re.search(COQ_PROMPT, outs[0]):
            outs[0] = Re.match.group('text')

    # remove footer (blank line and prompt) to begin of this session
    if len(outs) >= 3 and outs[-3] == '' and Re.search(COQ_PROMPT, outs[-2]):
        del outs[-3:-1]

    i = 0
    while True:
        if i >= len(outs):
            break
        while Re.search(COQ_PROMPT, outs[i]):
            try:
                outs[i:i + 1] = [
                        Re.match.group('prompt') + ins.next(),
                        Re.match.group('text')
                ]
                i = i + 1
            except StopIteration:
                break
        i = i + 1

    source, result = output(chunk, meta_data, os.linesep.join(outs))

    return [source, result]


def scheme_shell(command, chunk, meta_data):
    preamble, input = gather_input(chunk, meta_data)
    preamble_t, input_t = tangle_input(chunk, meta_data, preamble, input)
    ret, out, err, pre = shell_exec_session(command, preamble_t, input_t)
    source, result = output(chunk, meta_data, out)
    return [source, result]


def eval():
    return Toolchain([
        ChunksByEvalSession(),
        EvalTaskCreator(),
        Fence(),
        EvalTaskRunner(),
        EvalResultAssigner()
    ])
