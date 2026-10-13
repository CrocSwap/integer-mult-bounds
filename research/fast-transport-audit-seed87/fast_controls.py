#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Prepared by Sagar Thakrar with substantial Anthropic Claude assistance.
"""fast_controls.py [--require-fast] [--no-state-maps] [--pinned] CONTROL_SCRIPT [ARGS...]

Runs an unchanged transport-audit control script (layer_end_controls.py, cold_end_controls.py, ...) exactly as
'python3 CONTROL_SCRIPT ARGS...' would, but with an import hook.  The script still decides which
hpe_audit_and_transport.py it imports (its own sys.path / $PR635_CODE rule).  That file is executed from the bytes
whose sha256 is checked, and it is accelerated only when the sha256 is a validated version.  Any other version runs
unaccelerated with a warning, or exits non-zero under --require-fast.  Options are read only before CONTROL_SCRIPT;
everything after it is passed to the script verbatim.

--pinned loads the module through the same hook without accelerating it (the matched baseline for comparisons).
With FAST_HPE_RECORD=PATH, every hpe_audit_and_transport.run call is recorded to PATH (JSON): the input sha256 and
either the exception (type, repr(args), and the line of run() through which it propagated) or the
SCALAR-FRAME-AUDIT.json text without its 'seconds' line plus the sha256 of both output words.
"""
import hashlib
import json
import os
import runpy
import sys
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))


def recorder(records):
    def on_load(atc):
        inner = atc.run
        code = inner.__code__

        def run(raw, routing, out):
            item = dict(input=hashlib.sha256(raw.read_bytes()).hexdigest())
            try:
                inner(raw, routing, out)
            except BaseException as e:
                lines = [ln for f, ln in traceback.walk_tb(e.__traceback__) if f.f_code is code]
                item['exception'] = [type(e).__name__, repr(e.args), lines[-1] if lines else None]
                records.append(item)
                raise
            text = (out / 'SCALAR-FRAME-AUDIT.json').read_text()
            item['receipt'] = '\n'.join(ln for ln in text.splitlines() if not ln.startswith('  "seconds":'))
            item['outputs'] = {n: hashlib.sha256((out / n).read_bytes()).hexdigest()
                               for n in ('CANONICAL-WORD.json.gz', 'FULL-WORD.json.gz')}
            records.append(item)
        atc.run = run
    return on_load


def main(argv):
    require = state_maps = pinned = None
    while argv and argv[0].startswith('--'):
        flag = argv.pop(0)
        if flag == '--require-fast':
            require = True
        elif flag == '--no-state-maps':
            state_maps = False
        elif flag == '--pinned':
            pinned = True
        else:
            raise SystemExit(__doc__)
    if not argv:
        raise SystemExit(__doc__)
    script, args = os.path.abspath(argv[0]), argv[1:]
    sys.path.insert(0, HERE)
    import fast_hpe_transport
    sys.path.remove(HERE)
    record_path, records = os.environ.get('FAST_HPE_RECORD'), []
    finder = fast_hpe_transport.install_import_hook(accelerate=not pinned, require=bool(require),
                                                    state_maps=state_maps is not False,
                                                    on_load=recorder(records) if record_path else None)
    # Make sys.path look exactly as it would for 'python3 CONTROL_SCRIPT': its directory first, not this one.
    if sys.path and os.path.abspath(sys.path[0] or '.') == HERE:
        sys.path[0] = os.path.dirname(script)
    else:
        sys.path.insert(0, os.path.dirname(script))
    sys.argv = [script, *args]
    try:
        runpy.run_path(script, run_name='__main__')
    finally:
        if record_path:
            with open(record_path, 'w') as stream:
                json.dump(dict(loaded=finder.loaded, audits=records), stream, sort_keys=True)
        for item in finder.loaded:
            print('fast_hpe_transport: loaded %(path)s sha256 %(sha256)s accelerated=%(accelerated)s' % item, file=sys.stderr)


if __name__ == '__main__':
    main(sys.argv[1:])
