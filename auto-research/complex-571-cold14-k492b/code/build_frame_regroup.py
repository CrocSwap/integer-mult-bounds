"""Apply recipe-bound gate frame changes; the scalar operations stay identical.  Apache-2.0.
Extends PR583's build_frames.py (chafreaky, OpenAI Codex assisted) with changes of any profile delta, prepared with
Claude Code assistance.

Recipe: input_content_sha256, before/after profiles, and changes [{section, index, before, after, delta}].  Each change
keeps the gate's scalar operation and replaces only its frame.  Its exact sequential profile delta must equal the
recipe's `delta`, and the frame chains must stay monotone (gk_word.profile asserts this).  The cleanup must already
follow the inherited inverse rule, which only uses FULL frames, so frame changes on A and B leave it unchanged.
Helper widths and all initial helper responses must be unchanged.

Negative controls:
* each omitted change must lose the recipe profile;
* each change replaced by the FULL frame must violate a chain or cut bound."""
from pathlib import Path
from collections import Counter
import argparse, copy, gzip, hashlib, json, sys
assert __debug__, 'Assertions required'
ap = argparse.ArgumentParser()
for k in ('--input', '--recipe', '--gk-dir', '--out'): ap.add_argument(k, type=Path, required=True)
a = ap.parse_args(); assert not a.out.exists()
sys.path.insert(0, str(a.gk_dir)); import gk_word as G, gk_common as C
G.V = C.V = 112; G.DATA = C.DATA = 7168
raw = json.loads(gzip.decompress(a.input.read_bytes())); recipe = json.loads(a.recipe.read_text())
enc = lambda x: json.dumps(x, sort_keys=True, separators=(',', ':')).encode(); sha = lambda x: hashlib.sha256(x).hexdigest()
assert sha(enc(raw)) == recipe['input_content_sha256']; before = G.profile(raw); assert dict(before) == {int(r): n for r, n in recipe['before'].items()}
assert raw['cleanup'] == [G.inverse(e, G.FULL) for e in reversed(raw['A'] + raw['B']) if not 112 <= e[1] < 224], 'input cleanup is not the inherited inverse rule'
assert len({(c['section'], c['index']) for c in recipe['changes']}) == len(recipe['changes']) and recipe['changes']
w = copy.deepcopy(raw); trace = []
for c in recipe['changes']:
    part, i = c['section'], c['index']; assert part in ('A', 'B') and w[part][i] == c['before'] and c['before'][:-1] == c['after'][:-1] and c['before'][-1] != c['after'][-1]
    w[part][i] = c['after']; after = G.profile(w)
    delta = {r: after[r] - before[r] for r in set(after) | set(before) if after[r] != before[r]}
    assert delta == {int(r): n for r, n in c['delta'].items()}, ('delta', part, i, delta); trace.append(dict(section=part, index=i, delta=delta)); before = after
assert dict(G.profile(w)) == {int(r): n for r, n in recipe['after'].items()}
for k in raw:
    if k not in ('A', 'B', 'report'): assert w[k] == raw[k]
for part in ('A', 'B'): assert [e[:-1] for e in w[part]] == [e[:-1] for e in raw[part]]
assert G.widths_of(w) == G.widths_of(raw); responses = G.responses(w); assert responses == G.responses(raw)
assert all(not responses[int(r) - 224] for r in w['start_extra'])
rejected = []
for c in recipe['changes']:
    z = copy.deepcopy(w); z[c['section']][c['index']] = c['before']; assert G.profile(z) != G.profile(w); rejected.append('omission-%s-%d' % (c['section'], c['index']))
    z = copy.deepcopy(w); z[c['section']][c['index']][-1] = list(G.FULL)
    try: G.profile(z)
    except AssertionError: rejected.append('overpromotion-%s-%d' % (c['section'], c['index']))
    else: raise AssertionError('Invalid frame accepted')
H = G.profile(w); w['report'].update(local_profile={str(k): v for k, v in sorted(H.items())}, local_rank_mass=sum(r * n for r, n in H.items()))
a.out.mkdir(parents=True); (a.out / 'FULL-WORD.json.gz').write_bytes(gzip.compress(enc(w), mtime=0))
receipt = dict(status='PASS_EXACT_FRAME_REGROUPING', input_content_sha256=sha(enc(raw)), output_content_sha256=sha(enc(w)), profile_before=recipe['before'],
               profile_after=recipe['after'], changes=trace, negative_controls_rejected=rejected, all_scalar_operations_unchanged=True,
               all_initial_helper_responses_equal=True, all_entering_helper_responses_zero=True, helper_widths_unchanged=True,
               scope='Construction, frame/profile and scalar response checks only; native, phase and global admission are separate.')
(a.out / 'FRAME-CONSTRUCTION.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n', newline='\n'); print(json.dumps(receipt, indent=2))
