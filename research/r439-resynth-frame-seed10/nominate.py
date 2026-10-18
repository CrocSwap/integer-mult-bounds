#!/usr/bin/env python3
"""Source-pinned PR886 enumeration on the changed PR952 word. Apache-2.0.

This is deliberately a wrapper around the credited producer, not an independent
implementation. check.py independently reconstructs the problem and certificate.
"""
import argparse
import contextlib
import hashlib
import io
import json
from pathlib import Path
import runpy
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = 'research/r439-six-wire-boolean/candidate.json.gz'
PRODUCER = 'research/bit589-frame-optimum/frameopt.py'
C = '1733427039589844234749/1000000000000000000000000'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def produce():
    need(__debug__, 'Run without -O: the inherited producer uses assertions')
    sources = json.loads((HERE / 'SOURCES.json').read_text())
    for name, expected in sources['files'].items():
        need(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected,
             'source hash mismatch: ' + name)
    old_argv = sys.argv
    sys.argv = [str(ROOT / PRODUCER), str(ROOT / WORD), C]
    try:
        with contextlib.redirect_stdout(io.StringIO()) as output:
            state = runpy.run_path(str(ROOT / PRODUCER), run_name='__main__')
    finally:
        sys.argv = old_argv
    summary = json.loads(output.getvalue())
    gates = { (s,k): regs for s,k,regs,_ in state['gates'] if s != 'S' }
    nodes = []
    for key, choices in sorted(state['opts'].items()):
        nodes.append({'gate': list(key), 'registers': gates[key],
                      'lower': str(state['lo'][key]), 'upper': str(state['hi'][key]),
                      'original': str(state['word'][key]),
                      'choices': sorted(str(m) for m in choices)})
    components = sorted(sorted([list(x) for x in xs]) for xs in state['members'].values())
    return {'schema': 'r439-resynth-frame-nomination-v1', 'assignment_seed': 10,
            'base_commit': sources['base_commit'], 'source_word': WORD,
            'c': C, 'summary': summary, 'free_nodes': nodes,
            'components': components,
            'original_copy_frames': {str(q): str(m) for q,m in sorted(state['pin'].items())},
            'scope': 'Credited PR886 producer replay on fixed PR952 word; relaxed C frames; no new kappa.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='explicitly regenerate only NOMINATION.json')
    args = parser.parse_args()
    result = produce()
    path = HERE / 'NOMINATION.json'
    if args.write:
        path.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    else:
        need(result == json.loads(path.read_text()), 'nomination differs from committed certificate')
    print('PASS_R439_RESYNTH_NOMINATION free=%s assignments=%s improving=%s' % (
          result['summary']['free_gates'], result['summary']['assignments_enumerated'],
          result['summary']['improving_components']))


if __name__ == '__main__':
    main()
