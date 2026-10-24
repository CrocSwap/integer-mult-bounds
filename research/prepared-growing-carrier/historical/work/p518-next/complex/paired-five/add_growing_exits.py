"""Add exact rank-zero exits to the frozen growing-cap decoder word."""
from pathlib import Path
import hashlib
import json
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / 'source/research/nodal-pair-async/inputs/work/odd-stages'))
import clifford_exact as c

source = HERE / 'GROWING-CYCLE-WORD.json'
word = json.loads(source.read_bytes())
h = word['h']
exits = []
for t, q in enumerate(word['target_ports']):
    stream = len(word['source_ports']) + t
    old = c.canonical_frame(h, tuple(word['final_frames'][stream]))
    target = c.cgate(h, q).adjoint().then(c.fourier(h))
    adapter = old.adjoint().then(target)
    recipe, emitted = c.lower_child(adapter)
    assert recipe['rank'] == 0
    assert emitted.tab == adapter.tab
    for column in range(1 << h):
        assert old.then(emitted).zero_state(column) == target.zero_state(column)
    exits.append(dict(stream=stream, port=q, recipe=recipe,
                      target_circuit=target.circuit))
    word['events'].append(['monomial_exit', stream, len(exits)-1])
word['exit_adapters'] = exits
word['endpoint_convention'] = dict(
    sources='F', targets='F C_q^-1',
    scalar_rows='The scalar row is stated before the address operator.')
raw = json.dumps(word, sort_keys=True, separators=(',', ':')).encode()
(HERE / 'GROWING-CYCLE-LEGACY-EXITS-WORD.json').write_bytes(raw)
receipt = dict(status='PASS_EXACT_MONOMIAL_EXITS',
               original_word_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
               word_sha256=hashlib.sha256(raw).hexdigest(),
               exits=len(exits), rank_zero_exits=len(exits),
               address_columns_checked=len(exits) * (1 << h),
               full_global_phase=True, extra_paid_rank=0,
               scope='The finite decoder has the stated legacy exits. It is not a full factory or parent supplier.')
(HERE / 'GROWING-CYCLE-LEGACY-EXITS-RESULT.json').write_text(json.dumps(receipt, indent=2)+'\n')
print(json.dumps(receipt, indent=2))
