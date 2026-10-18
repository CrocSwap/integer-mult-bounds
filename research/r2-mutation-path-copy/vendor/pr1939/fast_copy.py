#!/usr/bin/env python3
"""Opt-in launcher: run a pinned retained verifier with a checked C-level deepcopy.

Usage (drop-in for `python3 -B RUN_PORTABLE SCRIPT ARGS...`):

    python3 -B fast_copy.py RUN_PORTABLE SCRIPT ARGS...

Both RUN_PORTABLE and SCRIPT must match the SHA-256 allow-list below. The
pinned `run_portable.py` then runs SCRIPT exactly as it would without this
launcher. The only process change is `copy.deepcopy`: for a top-level dict or
list, the copy is `marshal.loads(marshal.dumps(x))`, accepted only if marshal
serializes the value (it refuses anything but core builtin types, including
dict/list subclasses) and the copy has the same type and compares equal.
Otherwise, and for every call with a `memo`, the original `copy.deepcopy`
runs. marshal (format 4) records repeated objects as back-references, so
aliasing inside the value is kept, as it is by deepcopy; every dict and list in
the copy is a new object.

No verifier source is edited, no check or mutation control is skipped, and no
result is cached. Set FAST_COPY_STATS=PATH to write call counts as JSON
(stdout and stderr stay untouched, so stage logs remain byte-identical).

jackmgaller with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
import copy
import hashlib
import json
import marshal
import os
import runpy
import sys
from pathlib import Path

if not __debug__:
    raise RuntimeError('Assertions must remain enabled')

# run_portable.py retained by research/complex-k492-owner-repair/vendor/multicold.
RUN_PORTABLE = {'322d29d43dbee8130cde15d4bf05396698b5e3dfe3735813899db91cc0ba7955'}
# audit_allcold.py of the selected PR1087 T16 replay (upstream1087.tar.gz code/)
# and of research/gauge44-slots-t16/code/ (the cold baseline1042 `t16` stage).
SCRIPTS = {'1467a2acb654e62552c69fb9a7c4c85f70a02120881d222313865058ab71a6cc'}

_original_deepcopy = copy.deepcopy
STATS = {'marshal': 0, 'fallback': 0}


def checked_deepcopy(x, memo=None, _nil=[]):
    if memo is None and type(x) in (dict, list):
        try:
            y = marshal.loads(marshal.dumps(x))
            ok = type(y) is type(x) and y == x
        except (ValueError, RecursionError):  # unmarshallable, too deep or cyclic
            ok = False
        if ok:
            STATS['marshal'] += 1
            return y
    STATS['fallback'] += 1
    return _original_deepcopy(x) if memo is None else _original_deepcopy(x, memo, _nil)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main(argv, copier=checked_deepcopy):
    if len(argv) < 2:
        raise SystemExit('usage: fast_copy.py RUN_PORTABLE SCRIPT ARGS...')
    launcher, script = Path(argv[0]).resolve(), Path(argv[1]).resolve()
    if sha(launcher) not in RUN_PORTABLE:
        raise SystemExit('fast_copy: run_portable.py is not on the allow-list: ' + str(launcher))
    if sha(script) not in SCRIPTS:
        raise SystemExit('fast_copy: script is not on the allow-list: ' + str(script))
    copy.deepcopy = copier
    sys.argv = [str(launcher), *argv[1:]]
    try:
        runpy.run_path(str(launcher), run_name='__main__')
    finally:
        copy.deepcopy = _original_deepcopy
        out = os.environ.get('FAST_COPY_STATS')
        if out:
            Path(out).write_text(json.dumps(STATS, sort_keys=True) + '\n')


if __name__ == '__main__':
    main(sys.argv[1:])
