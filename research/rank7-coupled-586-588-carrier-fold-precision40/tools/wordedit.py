# SPDX-License-Identifier: Apache-2.0
"""wordedit.py -- generic, pure, reproducible BORROW-WORD edit spec (Marius-Paul Dumitrean, with substantial AI
assistance from Claude Code; supersedes our r12 version).

make_spec(old, new) -> spec : exact diff of two words (A/B/restore/cut/precondition/compensation gate-level edits with
                                frames; start_extra / helper_final / removed / warps / initial_corrections / report
                                replacements; cleanup is NOT stored, it is re-derived).
apply_spec(old, spec) -> word : pure producer; re-derives cleanup with the package's word_patch.derive_cleanup and the
                                restored set taken from the NEW word's helper_final (r12 used restored_of(old cleanup),
                                which is stale when an edit adds a restored endpoint, e.g. a paired extraction).
Round trip must give apply_spec(old, make_spec(old, new)) == new (checked by `python wordedit.py OLD NEW [SPEC_OUT]`).
Edit indices: deletes use OLD indices, inserts use NEW indices (apply deletes first, then inserts ascending),
matching lane B's EDITS.json convention. Frames are part of every gate (last element), so a re-solved frame on an
otherwise unchanged gate appears as a 'frame' op (index in NEW coordinates after structural edits).
"""
import gzip, json, sys, copy, difflib
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    import word_patch as WP  # PR2833's helpers (derive_cleanup); found next to this file inside a derived overlay
except ImportError:          # standalone use in this package: PR2894's equal derive_cleanup (vendor/preload_move.py)
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'vendor'))
    import preload_move; sys.modules['word_patch'] = preload_move  # noqa: E702
    import word_patch as WP

GATE_SECTIONS = ('A', 'B', 'restore', 'cut', 'precondition', 'compensation')
FIELD_KEYS = ('warps', 'initial_corrections', 'start_extra', 'helper_final', 'removed', 'report', 'cleanup')

def load(p): return json.loads(gzip.decompress(Path(p).read_bytes()))
def dump(w, p): Path(p).write_bytes(gzip.compress(json.dumps(w, separators=(',', ':')).encode(), mtime=0))
def strip(g): return g[:-1] if isinstance(g, list) and g and g[0] in ('add', 'scale') and isinstance(g[-1], list) else g
def key(g): return json.dumps(strip(g))

def section_spec(old, new):
    sm = difflib.SequenceMatcher(a=[key(g) for g in old], b=[key(g) for g in new], autojunk=False)
    deletes, inserts, frames = [], [], []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal':
            for di, (a, b) in enumerate(zip(old[i1:i2], new[j1:j2])):
                if a != b: frames.append([j1 + di, b[-1]])          # same gate, new frame (NEW index)
        else:
            for i in range(i1, i2): deletes.append([i, old[i]])      # OLD indices
            for j in range(j1, j2): inserts.append([j, new[j]])      # NEW indices, gate incl. frame
    return dict(deletes=deletes, inserts=inserts, frames=frames)

def apply_section(old, s):
    out = [g for i, g in enumerate(old) if i not in {d[0] for d in s['deletes']}]
    for j, g in sorted(s['inserts'], key=lambda x: x[0]): out.insert(j, copy.deepcopy(g))
    for j, fr in s['frames']: out[j] = out[j][:-1] + [fr]
    return out

def derive_cleanup(w):
    """Inverse-reverse cleanup of w (A without the entry prelude), buffers for every helper_final endpoint."""
    t = copy.deepcopy(w); t['A'] = w['A'][w['prelude_events']:]
    return WP.derive_cleanup(t, set(map(int, w['helper_final'])))

def make_spec(old, new):
    spec = {'sections': {}, 'warps': None, 'compensation_removed': [], 'compensation_added': [],
            'initial_corrections': None, 'start_extra': {}, 'start_extra_removed': [], 'helper_final': None,
            'removed': None, 'report': new['report'], 'other': {}}
    for sec in GATE_SECTIONS:
        if old[sec] != new[sec]: spec['sections'][sec] = section_spec(old[sec], new[sec])
    if old['warps'] != new['warps']: spec['warps'] = new['warps']
    if old['initial_corrections'] != new['initial_corrections']: spec['initial_corrections'] = new['initial_corrections']
    s_ = spec['sections'].get('compensation', {'deletes': [], 'inserts': [], 'frames': []})
    spec['compensation_removed'] = [g for _, g in s_['deletes']]; spec['compensation_added'] = [g for _, g in s_['inserts']]
    for k, v in new['start_extra'].items():
        if old['start_extra'].get(k) != v: spec['start_extra'][k] = v
    spec['start_extra_removed'] = [k for k in old['start_extra'] if k not in new['start_extra']]
    if old['helper_final'] != new['helper_final']: spec['helper_final'] = new['helper_final']
    if old['removed'] != new['removed']: spec['removed'] = new['removed']
    for k in new:
        if k not in GATE_SECTIONS + FIELD_KEYS and old.get(k) != new[k]:
            spec['other'][k] = new[k]
    return spec

def apply_spec(old, spec):
    w = copy.deepcopy(old)
    for sec, s in spec['sections'].items(): w[sec] = apply_section(w[sec], s)
    if spec.get('warps') is not None: w['warps'] = copy.deepcopy(spec['warps'])
    if spec.get('initial_corrections') is not None: w['initial_corrections'] = copy.deepcopy(spec['initial_corrections'])
    # compensation is edited positionally through spec['sections']['compensation'] (order-exact)
    for k in spec['start_extra_removed']: w['start_extra'].pop(k, None)
    for k, v in spec['start_extra'].items(): w['start_extra'][k] = v
    if spec.get('helper_final') is not None: w['helper_final'] = copy.deepcopy(spec['helper_final'])
    if spec.get('removed') is not None: w['removed'] = copy.deepcopy(spec['removed'])
    for k, v in spec['other'].items(): w[k] = copy.deepcopy(v)
    w['report'] = copy.deepcopy(spec['report'])
    w['cleanup'] = derive_cleanup(w)
    return w

if __name__ == '__main__':
    old, new = load(sys.argv[1]), load(sys.argv[2])
    spec = make_spec(old, new)
    rebuilt = apply_spec(old, spec)
    diff = [k for k in new if rebuilt.get(k) != new[k]]
    summary = {sec: {k: len(v) for k, v in s.items()} for sec, s in spec['sections'].items()}
    print(json.dumps(dict(roundtrip_exact=(not diff and set(rebuilt) == set(new)), differing_keys=diff, sections=summary,
                          comp_removed=len(spec['compensation_removed']), comp_added=len(spec['compensation_added']),
                          start_extra=spec['start_extra'], helper_final_changed=spec['helper_final'] is not None,
                          buffers=len(new['helper_final']), report=spec['report'])))
    if len(sys.argv) > 3: Path(sys.argv[3]).write_text(json.dumps(spec, indent=1))
