"""Run the pinned source machine in a fresh test-only import directory."""
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from program import assemble, ROLES, BORROWED, BLANK, LEFT, RIGHT
from machine import execute

code, entries = assemble()
result = []
for session in json.load(sys.stdin):
    tapes = {r: bytearray([BLANK]) for r in ROLES}
    heads = {r: 0 for r in ROLES}
    events = []
    def call(name):
        receipt = execute(code, tapes, heads, entries[name], max_steps=10000000)
        events.append(dict(entry=name, receipt=receipt, heads=dict(heads),
                           tapes={r: list(v) for r, v in tapes.items()}))
    call('init')
    for case in session:
        h, a, g, s = case['geometry']
        tapes['SOURCE'] = bytearray([LEFT] + case['bits'])
        for r, v in zip(('H', 'A', 'G', 'S'), (h, a, g, s)):
            tapes[r] = bytearray([LEFT] + [int(x) for x in reversed(bin(v)[2:])] + [RIGHT])
        for r in BORROWED:
            heads[r] = 1
        call('run')
        call('install' if case.get('install') else 'consume')
    call('close')
    result.append(events)
json.dump(result, sys.stdout, sort_keys=True)
