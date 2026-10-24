"""Pin exact Git bytes of the independently audited upstream package."""
from pathlib import Path
from hashlib import sha256, sha1
import json, subprocess, sys
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
HEAD = '4cc96829fad977aecf0018b26beb067cfd2689a5'
PREFIX = 'research/native-dual-suppliers/'

def need(ok, why):
    if not ok:
        raise ValueError(why)

def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)

def main():
    entries = git('ls-tree', '-r', HEAD, '--', PREFIX).decode('utf-8').splitlines()
    pins = []
    for line in entries:
        meta, path = line.split('\t', 1)
        mode, kind, blob = meta.split()
        need(kind == 'blob' and path.startswith(PREFIX), 'Unexpected Git entry')
        data = git('show', HEAD + ':' + path)
        need(sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest() == blob, 'Git blob mismatch')
        local = HERE / 'upstream' / path[len(PREFIX):]
        local.parent.mkdir(parents=True, exist_ok=True)
        if local.exists():
            need(local.read_bytes() == data, 'Refusing to replace different pinned source')
        else:
            local.write_bytes(data)
        pins.append(dict(path=path, local=local.relative_to(HERE).as_posix(), mode=mode, git_blob=blob, bytes=len(data), sha256=sha256(data).hexdigest()))
    need(len(pins) == 54, 'Expected exact PR4703 package file set')
    result = dict(repository='Dugongue/integer-mult-bounds', pr_url='https://github.com/CrocSwap/integer-mult-bounds/pull/4703', head=HEAD, files=pins)
    (HERE / 'SOURCES.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8', newline='\n')
    print('PASS_CAPTURE', len(pins), 'files')

if __name__ == '__main__':
    main()
