#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Compose four declared stages on our merged PR2942 words (Mason Hale's PR2917 words plus four paired extractions at
hyperplane normal 45):

  stage 1  joint codimension-2 end-frame lowering: 22 restored helpers in five groups, each group lowered to one shared
           rank-7 subspace W (a hyperplane of the old end frames); frame-only, i.e. declared end frames and declared gate
           frames (each one dimension lower) change, while every gate, scalar, operator, entrance and the cleanup stay;
  stage 2  five rank-8 paired input/output extractions (normal 42: pivots 226, 228, 230; normal 7: pivots 363, 395),
           composed exactly as PR2917's producer.py (Mason Hale) composes PR2908's paired construction (Jeremy Diviney):
           input gates at frame zero right after the prelude, output gates at E_n appended to restore, compensation C*S,
           one more private zero buffer per pivot, and the step's declared frame changes;
  stage 3  Jeremy Kothe's fourteen declared PR2957 gate rewrites, re-addressed to this word with exact preimages
           (data/REWRITES-2957.json) and applied by PR2957's own pure applier (vendor/declared_rewrites.py, vendored
           byte-identical; called with check_declared=False because its declared profile is that of PR2917's words),
           then paid profile, inventory and cleanup re-derived and compared;
  stage 4  four declared post-stage-3 edit blocks (edits/EDITS.json via edits/declared_edits.py): two restore carrier/pivot
           hyperplane skips (R1_E42, R2_E7) and two coupled B+restore carrier-fold rewrites (B_586_438, B_588_440) lowering
           entering helpers 586 and 588 from end frame E_30 (rank 8, width 7) to E_30 n E_76 n E_82 and E_30 n E_97 n E_127
           (rank 7, width 6), shifting local_profile to {1:2433, 2:724, 3:228, 4:102, 5:20, 8:8} and width_inventory to
           {4:26, 5:2, 6:18, 7:50, 8:99, 9:213}.

Frame accounting (frame_report) and inverse-reverse cleanup (derive_cleanup) are Jeremy Kothe's PR2894 code, vendored
byte-identical by PR2917 (vendor/preload_move.py). Marius-Paul Dumitrean (stages 1-3, PR2979) and dcharb78 (stage 4), with
substantial AI assistance. When imported as a module, this file is pure: no file, process or output access.
"""
import collections
import copy
from fractions import Fraction as Q

try:
    import preload_move as pm
    import declared_rewrites as dr
except ImportError:
    import sys as _sys
    from pathlib import Path as _Path
    _root = _Path(__file__).resolve().parent
    _sys.path.insert(0, str(_root / 'vendor'))
    _sys.path.insert(0, str(_root / 'edits'))
    import preload_move as pm
    import declared_rewrites as dr

try:
    import declared_edits as de
except ImportError:
    de = None

PARENT_PROFILE = {'1': 2434, '2': 632, '3': 286, '4': 104, '5': 26, '8': 8}      # PR2942
PARENT_INVENTORY = {'4': 26, '5': 2, '7': 62, '8': 100, '9': 218}
PARENT_BUFFERS = 86
# stage 1: group -> (shared rank-7 end frame W, helpers lowered to W)
GROUPS = {'V45': ([256, 128, 64, 35, 16, 11, 5], [249, 251, 265, 267]),           # = E_7 n E_42 n E_45 (PR2942's pivots, 8 -> 7)
          'A': ([256, 128, 64, 38, 20, 10, 1], [331, 450, 451, 508, 509]),        # inside E_30; 331 (PR2917) 8 -> 7, entering helpers 7 -> 6
          'B': ([256, 128, 64, 34, 17, 11, 4], [299, 448, 449, 484, 485]),        # inside E_51; 299 (PR2917) 8 -> 7, entering helpers 7 -> 6
          'C': ([256, 128, 64, 32, 19, 11, 6], [452, 453, 532, 533]),             # entering helpers 7 -> 6
          'D': ([256, 128, 64, 37, 21, 8, 3], [454, 455, 556, 557])}              # entering helpers 7 -> 6
STAGE1_PROFILE = {'1': 2430, '2': 722, '3': 236, '4': 102, '5': 18, '8': 8}
STAGE1_INVENTORY = {'4': 26, '5': 2, '6': 16, '7': 52, '8': 94, '9': 218}
STAGE1_ALLOWED = {'B', 'restore', 'helper_final', 'report'}
# stage 2
HELPERS = (226, 228, 230, 363, 395)
NORMALS = (42, 42, 42, 7, 7)
STAGE2_PROFILE = {'1': 2449, '2': 710, '3': 236, '4': 102, '5': 18, '8': 8}
STAGE2_ALLOWED = {'A', 'restore', 'helper_final', 'compensation', 'report', 'cleanup'}
# stage 3 (PR2957, Jeremy Kothe)
REWRITES = ('5997', '6000', '6004', '6008', '3779', '1564', '1569', '4604', '4630',
            'swap3749', 'swap3755', 'swap3761', 'swap3767', 'swap3773')
STAGE3_ALLOWED = {'A', 'B', 'restore', 'warps', 'report', 'cleanup'}
PROFILE = {'1': 2445, '2': 706, '3': 232, '4': 108, '5': 18, '8': 8}
INVENTORY = {'4': 26, '5': 2, '6': 16, '7': 52, '8': 99, '9': 213}
BUFFERS = 91
# stage 4 (declared restore carrier skips R1_E42, R2_E7 + coupled B_586_438, B_588_440 carrier folds)
DECLARED_EDITS = ('R1_E42', 'R2_E7', 'B_586_438', 'B_588_440')
COUPLED_LOWERED = {'586': [256, 128, 70, 32, 18, 12, 1],
                   '588': [256, 128, 65, 33, 18, 10, 6]}
STAGE4_ALLOWED = {'A', 'B', 'restore', 'warps', 'helper_final', 'report', 'cleanup'}
FINAL_PROFILE = {'1': 2433, '2': 724, '3': 228, '4': 102, '5': 20, '8': 8}
FINAL_INVENTORY = {'4': 26, '5': 2, '6': 18, '7': 50, '8': 99, '9': 213}


def hyperplane(normal):
    """Canonical basis of the rank-8 hyperplane E_n of F_2^9 with the given nonzero normal."""
    pm.require(0 < normal < 512, 'nonzero nine-bit normal')
    return list(pm.basis([x for x in range(1, 512) if (x & normal).bit_count() % 2 == 0]))


def inside(small, big):
    """span(small) is a subspace of span(big) (both given by any spanning lists)."""
    return pm.basis(list(big) + list(small)) == pm.basis(list(big))


def roles(g):
    return g[1:3] if g[0] == 'add' else g[1:2]


def rereport(x):
    profile, inventory = pm.frame_report(x)
    x['report']['local_profile'], x['report']['width_inventory'] = profile, inventory
    return x


def recleanup(x):
    z = copy.deepcopy(x)
    z['A'] = z['A'][z['prelude_events']:]
    return pm.derive_cleanup(z, set(map(int, x['helper_final'])))


def lowered_fit(word, groups=GROUPS):
    """Stage-1 validity: every gate touching a lowered helper lies in that helper's lowered end frame."""
    bad = []
    for _, (W, hs) in groups.items():
        for h in hs:
            for sec in ('A', 'B', 'restore'):
                for i, g in enumerate(word[sec]):
                    if g[0] in ('add', 'scale') and h in roles(g) and not inside(g[-1], W):
                        bad.append((h, sec, i))
    return bad


def lower_end_frames(word, record):
    """Stage 1: the declared joint end-frame lowering (frame-only)."""
    pm.require({k: [list(W), list(hs)] for k, (W, hs) in GROUPS.items()} == record['groups'], 'declared groups')
    lowered = {}
    for _, (W, hs) in GROUPS.items():
        pm.require(list(pm.basis(W)) == W and len(W) == 7, 'canonical rank-7 group subspace')
        for h in hs:
            lowered[str(h)] = W
    pm.require(set(record['helper_final_changes']) == set(lowered), 'exactly the grouped helpers are lowered')
    x = copy.deepcopy(word)
    for h, change in record['helper_final_changes'].items():
        old, new = word['helper_final'][h], change['new']
        pm.require(change['old'] == old and new == lowered[h], 'exact end-frame preimage and group subspace')
        pm.require(inside(new, old) and len(new) == len(old) - 1, 'lowered end frame is a hyperplane of the old end frame')
        x['helper_final'][h] = list(new)
    seen = set()
    for e in record['frame_edits']:
        section, index = e['section'], e['index']
        pm.require(section in ('A', 'B', 'restore') and (section, index) not in seen and 0 <= index < len(x[section]) and
                   (section != 'A' or index >= x['prelude_events']), 'unique declared non-prelude gate frame edit')
        seen.add((section, index))
        g = x[section][index]
        pm.require(g[0] in ('add', 'scale') and g[:-1] == e['gate'] and g[-1] == e['old_frame'], 'exact gate frame preimage')
        pm.require(list(pm.basis(e['new_frame'])) == e['new_frame'] and inside(e['new_frame'], e['old_frame']) and
                   len(e['new_frame']) == len(pm.basis(e['old_frame'])) - 1, 'canonical frame lowered by one dimension')
        g[-1] = list(e['new_frame'])
    pm.require(not lowered_fit(x), 'every gate touching a lowered helper fits its lowered end frame')
    rereport(x)
    pm.require(recleanup(x) == word['cleanup'], 'the cleanup contract is unchanged (frames do not enter it)')
    pm.require({k for k in word if word[k] != x[k]} == STAGE1_ALLOWED, 'stage 1 changes frames, end frames and the report only')
    pm.require(all(a[:-1] == b[:-1] for s in ('A', 'B', 'restore') for a, b in zip(word[s], x[s])), 'no gate or scalar changes')
    pm.require(x['report']['local_profile'] == STAGE1_PROFILE == record['declared_local_profile'] and
               x['report']['width_inventory'] == STAGE1_INVENTORY == record['declared_width_inventory'], 'declared joint stage-1 invoice')
    return x


def apply_stage(word, transform):
    """Stage 2, one step: PR2917's paired composition rule with the step's declared frame changes."""
    h, k = transform['helper'], transform['step']
    before, after = transform['before'], transform['after']
    pm.require(1 <= k <= len(HELPERS) and HELPERS[k - 1] == h and NORMALS[k - 1] == transform['normal'], 'declared step')
    pm.require(str(h) not in word['helper_final'] and str(h) not in word['start_extra'], 'fresh zero-entrance helper')
    protected = set(map(int, word['helper_final'])) | set(map(int, word['start_extra']))
    protected |= {c['source'] for c in word['initial_corrections']}
    for g in before:
        pm.require(g[0] in ('add', 'scale') and g[-1] == [], 'scalar zero-frame input change')
        pm.require(all(224 <= r < 704 and r not in protected and r not in word['removed'] for r in roles(g)), 'unprotected live helpers only')
    frame = hyperplane(transform['normal'])
    pm.require(len(after) > 0 and all(g[0] in ('add', 'scale') and g[-1] == frame for g in after), 'common terminal hyperplane E_n')
    x = copy.deepcopy(word)
    n = x['prelude_events']
    x['A'] = x['A'][:n] + copy.deepcopy(before) + x['A'][n:]
    x['restore'] += copy.deepcopy(after)
    x['helper_final'][str(h)] = list(frame)
    C = collections.defaultdict(dict)
    for g in x['compensation']:
        C[g[2]][g[1]] = C[g[2]].get(g[1], Q(0)) + Q(g[3], g[4])
    # Right multiplication C*S uses the reverse order of the literal input gates.
    for g in reversed(before):
        if g[0] == 'scale':
            C[g[1]] = {t: a * Q(g[2], g[3]) for t, a in C[g[1]].items()}
        else:
            t, s = g[1:3]
            for target, a in C[t].items():
                C[s][target] = C[s].get(target, Q(0)) + Q(g[3], g[4]) * a
    x['compensation'] = [['add', t, r, a.numerator, a.denominator, []]
                         for r, col in sorted(C.items()) for t, a in sorted(col.items()) if a]
    pm.require(not any(g[2] == h for g in x['compensation']), 'new cold column has no compensation (C v = 0)')
    seen = set()
    for e in transform['frame_changes']:      # addressed in the child word
        section, index = e['section'], e['index']
        pm.require(section in ('A', 'B', 'restore') and (section, index) not in seen and 0 <= index < len(x[section]) and
                   (section != 'A' or index >= n), 'unique declared frame change')
        seen.add((section, index))
        g = x[section][index]
        pm.require(g[0] in ('add', 'scale') and g[:-1] == e['gate'] and g[-1] == e['old_frame'], 'exact frame change preimage')
        pm.require(list(pm.basis(e['new_frame'])) == e['new_frame'] and not 112 <= g[1] < 224, 'canonical nontarget frame')
        g[-1] = list(e['new_frame'])
    rereport(x)
    x['cleanup'] = recleanup(x)
    pm.require({k_ for k_ in word if word[k_] != x[k_]} == STAGE2_ALLOWED, 'exact stage-2 changed sections')
    return x


def apply_rewrites(word, rewrites):
    """Stage 3: PR2957's fourteen declared rewrites by PR2957's own applier, re-derivations compared."""
    pm.require(tuple(r['id'] for r in rewrites) == REWRITES, 'the fourteen declared PR2957 rewrites, in order')
    pm.require({r['cls'] for r in rewrites} == set(dr.CLASSES), 'all five PR2957 rewrite classes')
    x, ledger = dr.apply(word, rewrites, check_declared=False)
    pm.require(ledger['rewrites'] == list(REWRITES), 'applier ledger')
    profile, inventory = pm.frame_report(x)
    pm.require((profile, inventory) == (x['report']['local_profile'], x['report']['width_inventory']), 'report re-derived')
    pm.require(x['cleanup'] == recleanup(x), 'cleanup re-derived with the 91 restored endpoints')
    pm.require(inventory == word['report']['width_inventory'], 'rewrites keep every helper width')
    pm.require({k for k in word if word[k] != x[k]} <= STAGE3_ALLOWED, 'exact stage-3 changed sections')
    pm.require([w[1:] for w in x['warps']] == [w[1:] for w in word['warps']], 'warps: only their B positions move')
    return x, ledger


def apply_declared_edits(word, spec, declared=None):
    """Stage 4: declared restore carrier skips (R1_E42, R2_E7) and coupled B+restore carrier folds (B_586_438, B_588_440)."""
    pm.require(de is not None, 'declared_edits module available')
    pm.require(tuple(e['id'] for e in spec) == DECLARED_EDITS, 'the four declared stage-4 edit blocks, in order')
    x, ledger = de.apply(word, spec, declared)
    profile, inventory = pm.frame_report(x)
    pm.require((profile, inventory) == (FINAL_PROFILE, FINAL_INVENTORY), 'stage-4 final profile and width inventory')
    pm.require(x['cleanup'] == recleanup(x), 'cleanup re-derived with the 91 restored endpoints')
    pm.require({k for k in word if word[k] != x[k]} <= STAGE4_ALLOWED, 'exact stage-4 changed sections')
    for h, W in COUPLED_LOWERED.items():
        pm.require(x['helper_final'][h] == W and inside(W, word['helper_final'][h]), ('coupled lowered helper_final', h))
    pm.require(not lowered_fit(x, {'coupled_586': (COUPLED_LOWERED['586'], [586]), 'coupled_588': (COUPLED_LOWERED['588'], [588])}),
               'every gate touching 586 or 588 fits its lowered rank-7 end frame')
    return x, ledger


def stages(parent, record, transforms, rewrites, edits_spec=None, declared=None):
    """All intermediate words: [stage 1, stage-2 step 1..5, stage 3] (+ [stage 4] if edits_spec is given)."""
    pm.require(len(parent['helper_final']) == PARENT_BUFFERS, 'PR2942 cold endpoint count')
    pm.require(parent['report']['local_profile'] == PARENT_PROFILE and
               parent['report']['width_inventory'] == PARENT_INVENTORY, 'PR2942 local profile and inventory')
    pm.require(tuple(t['helper'] for t in transforms) == HELPERS and [t['step'] for t in transforms] == [1, 2, 3, 4, 5], 'declared stage-2 order')
    words = [lower_end_frames(parent, record)]
    for t in transforms:
        words.append(apply_stage(words[-1], t))
    pm.require(words[-1]['report']['local_profile'] == STAGE2_PROFILE and words[-1]['report']['width_inventory'] == INVENTORY, 'stage-2 invoice')
    words.append(apply_rewrites(words[-1], rewrites)[0])
    if edits_spec is not None:
        words.append(apply_declared_edits(words[-1], edits_spec, declared)[0])
    return words


def apply(parent, record, transforms, rewrites, edits_spec=None, declared=None):
    x = stages(parent, record, transforms, rewrites, edits_spec, declared)[-1]
    lowered = {str(h): W for W, hs in GROUPS.values() for h in hs}
    if edits_spec is None:
        pm.require(all(x['helper_final'].get(h) == lowered.get(h, U) for h, U in parent['helper_final'].items()),
                   'inherited endpoints retained, the 22 grouped ones lowered to their group subspace')
        pm.require(len(x['helper_final']) == BUFFERS, 'all five added buffers charged')
        pm.require(x['report']['local_profile'] == PROFILE and x['report']['width_inventory'] == INVENTORY, 'complete local profile and inventory')
    else:
        lowered.update(COUPLED_LOWERED)
        pm.require(all(x['helper_final'].get(h) == lowered.get(h, U) for h, U in parent['helper_final'].items()),
                   'inherited endpoints retained, the 24 lowered ones at their rank-7 subspaces')
        pm.require(len(x['helper_final']) == BUFFERS, 'all five added buffers charged')
        pm.require(x['report']['local_profile'] == FINAL_PROFILE and x['report']['width_inventory'] == FINAL_INVENTORY, 'complete stage-4 profile and inventory')
    return x


def _cli_check():
    import argparse, contextlib, gzip, hashlib, io, json, tempfile
    from pathlib import Path
    ap = argparse.ArgumentParser(description='Rebuild and verify all four producer stages (PARENT -> WORD -> FINAL-WORD).')
    ap.add_argument('--check', action='store_true', help='Verify complete producer reconstruction and exact audit of final words')
    ap.add_argument('--work', type=Path, default=None, help='Optional working directory for audit outputs')
    a = ap.parse_args()
    root = Path(__file__).resolve().parent
    import audit_local as aud

    def read_f(p):
        b = p.read_bytes()
        return json.loads(gzip.decompress(b) if b[:2] == b'\x1f\x8b' else b)

    def sha_f(p):
        return hashlib.sha256(p.read_bytes()).hexdigest()

    record = read_f(root / 'data/STAGE1-FRAME-EDITS.json')
    transforms = [read_f(root / f'data/TRANSFORM-{h}.json') for h in HELPERS]
    rewrites = read_f(root / 'data/REWRITES-2957.json')
    edits_doc = read_f(root / 'edits/EDITS.json')

    def run_in(out_dir):
        summary = {}
        for tag in ('base', 'extra'):
            parent = read_f(root / f'data/PARENT-{tag}.json.gz')
            word3 = read_f(root / f'data/WORD-{tag}.json.gz')
            word4 = read_f(root / f'edits/FINAL-WORD-{tag}.json.gz')
            chain = stages(parent, record, transforms, rewrites, edits_doc['edits'][tag], edits_doc['declared'])
            pm.require(chain[-2] == apply(parent, record, transforms, rewrites) == word3, f'{tag}: stage-3 word matches data/WORD-{tag}.json.gz')
            pm.require(chain[-1] == apply(parent, record, transforms, rewrites, edits_doc['edits'][tag], edits_doc['declared']) == word4,
                       f'{tag}: stage-4 word matches edits/FINAL-WORD-{tag}.json.gz')
            gz_path = out_dir / f'final-{tag}.json.gz'
            gz_path.write_bytes(gzip.compress(json.dumps(word4, separators=(',', ':')).encode(), mtime=0))
            with contextlib.redirect_stdout(io.StringIO()):
                res = aud.run(gz_path, out_dir / f'final-{tag}.json')
            pm.require(res['status'] == 'PASS_INDEPENDENT_EXACT_BORROWING_WORD' and res['orientations'] == {'forward': 'PASS', 'dual': 'PASS'},
                       f'{tag}: exact audit pass')
            summary[tag] = {
                'parent_sha256': sha_f(root / f'data/PARENT-{tag}.json.gz'),
                'stage3_word_sha256': sha_f(root / f'data/WORD-{tag}.json.gz'),
                'final_word_sha256': sha_f(root / f'edits/FINAL-WORD-{tag}.json.gz'),
                'audit': res['status'],
                'local_profile': word4['report']['local_profile'],
                'width_inventory': word4['report']['width_inventory'],
            }
        print('PASS_PRODUCER_CHECK', json.dumps(summary, sort_keys=True), flush=True)

    if a.work is not None:
        out = a.work.resolve()
        out.mkdir(parents=True, exist_ok=True)
        run_in(out)
    else:
        with tempfile.TemporaryDirectory(prefix='rank7-producer-check-') as td:
            run_in(Path(td))


if __name__ == '__main__':
    _cli_check()
