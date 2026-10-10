#!/usr/bin/env python3
"""Bind PR273's frozen target-prefix square groups to a different cohort transcript.

The groups are identified by target ids and a close frame; only the cut record and each group's close record are
transcript-bound. After the kernel cut the two words carry the same scalar events (the kernel families only differ
in the pre-cut compensation reads and the Q/Q^-1 passes), so every post-cut non-MOVE event is aligned by its scalar
content (op, a, b, c, z), ignoring frames (descent/plateau retimings change frames only). The cut is the first record
after the last Q pass (category 28), as in PR273's word."""
import hashlib, json, struct, sys
from pathlib import Path
if not __debug__: raise SystemExit('assertions required')
base, sel_path, cand, out = map(Path, sys.argv[1:5])
E = struct.Struct('<6i')
sel = json.loads(sel_path.read_text())
b = base.read_bytes(); n = cand.read_bytes()
assert hashlib.sha256(b).hexdigest() == sel['input_record_sha256']
be = list(E.iter_unpack(b)); ne = list(E.iter_unpack(n))
def cut_of(ev):
    last = max(i for i, e in enumerate(ev) if e[0] == 1 and e[5] == 28); return last + 1
cut_b, cut_n = cut_of(be), cut_of(ne)
assert cut_b == sel['cut_record'], (cut_b, sel['cut_record'])
def core(ev, cut): return [(i, (e[0], e[1], e[2], e[3], e[5])) for i, e in enumerate(ev) if i > cut and e[0] and not (e[0] == 1 and e[5] in (28, 29))]
cb, cn = core(be, cut_b), core(ne, cut_n)
assert [e for _, e in cb] == [e for _, e in cn], 'post-cut scalar event sequence differs'
mapping = {i: j for (i, _), (j, _) in zip(cb, cn)}
bindings = []
for g in sel['groups']:
    i = g['close_after_record']; j = mapping[i]
    assert be[i][0] == 1 and (be[i][1], be[i][2], be[i][3], be[i][5]) == (ne[j][1], ne[j][2], ne[j][3], ne[j][5])
    bindings.append(dict(baseline_close=i, candidate_close=j, event=list(be[i])))
    g['close_after_record'] = j
adds = sum(e[0] == 1 for e in ne)
sel.update(baseline_input_record_sha256=sel['input_record_sha256'], baseline_cut_record=cut_b, input_record_sha256=hashlib.sha256(n).hexdigest(),
           input_record_count=len(ne), cut_record=cut_n, expected_scalar_additions=adds - sel['expected_deleted_reads'] + sel['expected_inserted_additions'],
           core_binding=dict(status='PASS_POST_CUT_SCALAR_EVENT_ALIGNMENT_FRAMES_IGNORED', events_compared=len(cb), cut_record=cut_n, bindings=bindings))
out.write_text(json.dumps(sel, indent=2) + '\n')
print('bound', len(bindings), 'groups; cut', cut_b, '->', cut_n, 'post-cut events', len(cb), 'scalar additions expected', sel['expected_scalar_additions'], flush=True)
