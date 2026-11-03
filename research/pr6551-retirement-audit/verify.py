"""Check frozen-input integrity and run independent audit checks. Apache-2.0.
DLamdata with substantial OpenAI Codex assistance.
"""
import hashlib
import importlib.util
import json
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def check_retained_integrity(root=HERE):
    record = json.loads((root/'RETAINED.json').read_bytes())
    seen = set()
    for item in record['files']:
        name = item['path']; path = PurePosixPath(name)
        need(path.parts[0] == 'source' and not path.is_absolute() and '..' not in path.parts and
             name not in seen, 'unique confined retained input')
        seen.add(name)
        file = root/name
        need(file.is_file() and not file.is_symlink(), 'regular retained input '+name)
        data = file.read_bytes()
        need(hashlib.sha256(data).hexdigest() == item['sha256'], 'source SHA256 '+name)
        need(hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest() == item['git_blob'],
             'source Git blob '+name)
    actual = {p.relative_to(root).as_posix() for p in (root/'source').rglob('*') if p.is_file()}
    need(seen == actual, 'exact retained input inventory')
    return len(seen)


def load(name):
    spec = importlib.util.spec_from_file_location('independent_'+name, HERE/(name+'.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run():
    integrity_count = check_retained_integrity()
    # These are audit modules, never retained predecessor Python modules.
    with tempfile.TemporaryDirectory(prefix='retirement-audit-') as temporary:
        old_prefix = sys.pycache_prefix
        sys.pycache_prefix = str(Path(temporary)/'bytecode')
        try:
            caller = load('caller').run()
            accounting = load('accounting').run(HERE/'source/pr6545', HERE/'source/pr6551')
            pricing = load('pricing_binding').run(HERE/'source/pr6545/pricing.py',
                                                 HERE/'source/pr6551/pricing.py')
            # Evaluation of the explicitly bound SOURCE tariff, not a proof
            # that its physical per-operation allowances are valid.
            ordinary = {name: 18*10**7 + 17*1664 + 32*35*104*caller[name]['events']
                        + 35*104*(26+1000) for name in ('old', 'new')}
            need(ordinary == {'old': 254699248, 'new': 254932208}, 'declared ordinary arithmetic')
            command = [sys.executable, '-I', '-B', '-X', 'pycache_prefix='+str(Path(temporary)/'oracle-cache')]
            if sys.flags.optimize:
                command.append('-O')
            command += [str(HERE/'cut_four_fibers.py'), str(HERE/'source/pr6545/CONTROLLER.json'),
                        str(HERE/'source/pr6551/CONTROLLER.json')]
            result = subprocess.run(command, check=True, capture_output=True, text=True, timeout=30)
            oracle = json.loads(result.stdout)
        finally:
            sys.pycache_prefix = old_prefix
    return {'status': 'PASS_PR6551_INDEPENDENT_RETIREMENT_AUDIT',
            'integrity_checked_files': integrity_count, 'caller': caller,
            'accounting': accounting, 'four_fiber_cut': oracle,
            'pricing_source_binding': pricing, 'declared_ordinary_bounds': ordinary,
            'scope': 'Exact finite caller identities and complete Gaussian invoice delta; no supplier admission or new kappa.'}


if __name__ == '__main__':
    need(sys.argv[1:] in ([], ['--emit']), 'only --emit is supported')
    result = run()
    if not sys.argv[1:]:
        need(result == json.loads((HERE/'RESULT.json').read_bytes()), 'exact integrated scientific receipt')
    print(json.dumps(result, indent=2, sort_keys=True))
