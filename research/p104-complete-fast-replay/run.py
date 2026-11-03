"""Regenerate the complete source result with explicit replay dependencies.

Ali Romman with OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
from types import SimpleNamespace
import contextlib
import importlib.util
import io
import json
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
SOURCE = HERE/'inputs/tree/research/p104-third-anchor-clean-mixed-root'
for path in (HERE,HERE/'inputs/native',HERE/'inputs/forward',HERE/'inputs/arithmetic',HERE/'inputs/pricing'):
    sys.path.insert(0,str(path))


def load(path,name):
    spec = importlib.util.spec_from_file_location(name,path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def services(root,source):
    from bounded import Moment,exponential,logarithm
    from rows import Sparse
    native = load(HERE/'inputs/native/native.py','explicit_native')
    compiler = load(HERE/'inputs/native/prefix_clifford.py','prefix_compiler')
    checker = load(HERE/'inputs/native/native_gray.py','gray_checker')
    forward = load(HERE/'inputs/forward/driver.py','forward_driver')
    second = Moment(logarithm,exponential)
    def dependency(path,name):
        if path.name == 'mixed_target_probe.py':
            return second
        return source.load(path,name)
    return SimpleNamespace(ROOT=root,read=source.read,need=source.need,load=dependency,
                           replay=lambda word:forward.replay(word,Sparse),
                           reverse_columns=source.reverse_columns,
                           native=lambda word:native.native(word,compiler,checker),
                           price=load(HERE/'inputs/pricing/pricing_fast.py','certificate_price'))


def run(mode):
    source = load(SOURCE/'verify.py' if mode == 'baseline' else HERE/'complete.py','full_driver')
    transcript = io.StringIO()
    with tempfile.TemporaryDirectory(prefix='complete-p104-') as directory:
        with contextlib.redirect_stdout(transcript):
            if mode == 'baseline':
                result = source.run(Path(directory)/'retained')
            elif mode == 'integrated':
                result = source.run(Path(directory)/'retained',service_factory=services)
            else:
                raise ValueError('Unknown complete replay mode')
    wanted = json.loads((SOURCE/'RESULT.json').read_bytes())
    if result != wanted:
        differing = [k for k in wanted if wanted[k] != result.get(k)]
        raise ValueError('Complete scientific receipt differs: '+str(differing))
    return result,transcript.getvalue()


if __name__ == '__main__':
    from verify import authenticate
    authenticate()
    result,transcript = run(sys.argv[1])
    print(json.dumps({'result':result,'transcript':transcript},sort_keys=True))
