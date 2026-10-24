#!/usr/bin/env python3
"""Literal reverse/letter macro accounting for the unchanged p19 word."""
import argparse
from collections import Counter
import json
from pathlib import Path

import p19_word as W

HERE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def replay(gates):
    rows = [{(i, ()): 1} for i in range(38)]
    code_state = [False] * 38
    scratch = set()
    events = []
    for index, gate in enumerate(gates):
        kind = gate[0]
        if kind == 'GAUGE_LOAD':
            role = gate[1]
            need(role % 2 and not code_state[role], 'load state')
            code_state[role] = True
            scratch.add(role)
            events.append(('code', role, -1))
        elif kind == 'GAUGE_UNLOAD':
            role = gate[1]
            need(code_state[role] and role in scratch, 'unload state')
            code_state[role] = False
            scratch.remove(role)
            events.append(('code', role, 1))
        elif kind == 'REVERSE':
            x, y = gate[1:3]
            need(code_state[y], 'reverse coded source')
            events.extend([('native_reverse', x, y), ('central_q', x), ('central_q', y)])
        elif kind == 'LETTER':
            events.append(('letter', gate[1], gate[2]))
        elif kind == 'IDLE':
            events.append(('idle', gate[1], gate[2], gate[3]))
        elif kind == 'BRIDGE':
            events.append(('add', gate[1], gate[2], gate[3]))
        elif kind == 'FORWARD':
            events.append(('forward_query', gate[1], gate[2]))
        elif kind == 'SWAP':
            need(gate[3] == -1, 'swap sign')
            events.append(('signed_swap', gate[1], gate[2], -1))
        else:
            raise ValueError(f'unknown gate {kind} at {index}')
    need(not any(code_state) and not scratch, 'reverse endpoint cleanup')
    return events


def main():
    gates = W.native_chain(19, 'I' * 9 + 'T' * 9)
    events = replay(gates)
    counts = Counter(e[0] for e in events)
    need(counts['native_reverse'] == 19, 'reverse calls')
    need(counts['central_q'] == 38, 'central corrections')
    need(counts['forward_query'] == 20, 'forward calls')
    need(counts['signed_swap'] == 19, 'terminal swaps')
    out = {
        'status': 'PASS_LITERAL_REVERSE_LETTER_PROGRAM',
        'gate_records': len(gates),
        'macro_events': len(events),
        'counts': dict(sorted(counts.items())),
        'reverse_rank_one_corrections': 38 * W.OWNERS,
        'endpoint': {'all_roles_uncoded': True, 'owned_scratch_blank': True},
        'scope': 'exact chronology and correction inventory; native precision/tape lowering remains source-interface work',
        'events': events,
    }
    if '--write' in __import__('sys').argv:
        (HERE / 'P19_REVERSE_PROGRAM.json').write_text(json.dumps(out, indent=2, sort_keys=True) + '\n')
    print(json.dumps({k: v for k, v in out.items() if k != 'events'}, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
