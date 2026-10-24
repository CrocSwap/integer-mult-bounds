"""Replay the complete set of retained diagonal terminal words with Fraction."""
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import struct
import sys

if not __debug__:
    raise SystemExit("Run this verifier without -O. Historical sources use assert.")

package, primary, output = map(Path, sys.argv[1:])
source = package / 'independent-sources/work/four-register/dirty_ancilla.py'
spec = spec_from_file_location('fraction_core', source)
core = module_from_spec(spec)
spec.loader.exec_module(core)
terminals = [json.loads(line) for line in (primary / 'rational3.terminals.jsonl').read_text().splitlines()]
if len(terminals) != 538 or len({r['word'] for r in terminals}) != 538:
    raise RuntimeError('Terminal word count')
records = []
with (primary / 'rank3.bin').open('rb') as inp:
    for record in terminals:
        inp.seek(18 * record['word'])
        matrices = struct.unpack('<9H', inp.read(18))[:8]
        word = []
        for matrix in matrices:
            rows = [(matrix >> (4*i)) & 15 for i in range(4)]
            nonzero = {r for r in rows if r}
            if len(nonzero) != 1:
                raise RuntimeError('Projector rank')
            y = next(iter(nonzero))
            x = sum(1 << i for i,r in enumerate(rows) if r)
            if (x & y).bit_count() % 2 != 1:
                raise RuntimeError('Projector idempotence')
            word.append((x,y))
        result = core.solve(word)
        if result['candidate'] or result['stats']['terminals'] != record['terminals']:
            raise RuntimeError('Fraction terminal result')
        stats = result['stats']
        records.append({'word': record['word'], **{key: stats[key] for key in ['nodes','terminals','low_rank_targets','zero_frame_branches','parity_branches']}})
        core.rref.cache_clear()
        core.rep.cache_clear()
        core.add.cache_clear()
output.write_text(json.dumps({'status':'PASS_FRACTION_TERMINAL_REPLAY','words':len(records),'nodes':sum(r['nodes'] for r in records),'terminals':sum(r['terminals'] for r in records),'candidates':0,'records':records},indent=2)+'\n')
print('538 terminal words, 538 terminals, zero candidates')
