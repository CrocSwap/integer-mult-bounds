#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent phase-exact check of the selected frontier1094 word's stored Clifford recipes (no new kappa).

Usage: python3 -I -B research/frontier1094-recipes-exact-seed76/verify.py [--write] [--subset SPEC] [--receipts PATH]

Lemma G's RecipesExact premise (research/e8-lemma-g-lean/LemmaG/Stream.lean:110-112) says every relabel of
the stream executes T_B o T_A^-1. For the selected gauge44 provider this script checks, with a kernel written
from scratch (clifford.py, standard library only; no producer code is imported):

  B  the byte binding: selected record -> frontier1094 certificate -> capsule -> owner audit / template ->
     CANONICAL-WORD, CLIFFORD-RECIPES, CLIFFORD-REVIEW, LOCAL-PROGRAMS (and SLOT-PINS-k8);
  I  the inventory: the 2,896 child records are exactly the word's directed edges (with both centre
     directions) and exactly the climb and centre relabel keys of both emitted orientations; ranks, nesting,
     and the 224 endpoint adapters with their ports and frames; every monomial record well formed;
  FX calibration of the kernel against independent published values: the Lean literals of
     HyperplaneEnd/Exact.lean (gate lists and the rank-7 pair identities), the #1415 operator digests and
     the #702 frame-kernel digests, plus hand values and basis-dependence checks;
  E  every child: L o F_r o R o T_old = T_new, and every endpoint adapter: M o C_q = T_start (source) and
     M o F_9 o C_q^-1 = T_final (target), exactly on all 512 columns of C^(2^9), global phase included,
     by packed exact Gaussian-integer evaluation at the sound radix beta = 2K + 2;
  C  semantic mutation controls on a fixed sample (each must be rejected), and a positive basis control.

Expected last line: PASS_FRONTIER1094_RECIPES_EXACT (PARTIAL_FRONTIER1094_RECIPES_EXACT for --subset).
"""
import argparse
import gzip
import hashlib
import io
import json
import re
import sys
import tarfile
import time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import clifford as C  # noqa: E402

CASES = json.loads((HERE / 'CASES.json').read_text())
FORBIDDEN = ('clifford_exact', 'lower_child', 'phases_full', 'sparse_state', 'fast_state', 'lg_phys')


class Reject(Exception):
    """A check failed; the argument is the label of the check."""


def need(ok, label):
    if not ok:
        raise Reject(label)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def strict_loads(data):
    def hook(pairs):
        out = {}
        for k, v in pairs:
            if k in out:
                raise Reject('P duplicate JSON key: ' + k)
            out[k] = v
        return out
    return json.loads(data, object_pairs_hook=hook)


def canonical_bytes(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':')).encode()


def find_pin(obj, key, value):
    if isinstance(obj, dict):
        return any((k == key and v == value) or find_pin(v, key, value) for k, v in obj.items())
    if isinstance(obj, list):
        return any(find_pin(v, key, value) for v in obj)
    return False


def safe_members(tar):
    names = Counter()
    for info in tar.getmembers():
        names[info.name] += 1
        need(info.isreg() or info.isdir(), 'B2 archive members are regular files')
        need(not info.name.startswith('/') and '..' not in Path(info.name).parts, 'B2 archive member paths')
    need(all(n == 1 for n in names.values()), 'B2 archive member names are unique')
    return {info.name: info for info in tar.getmembers()}


# ------------------------------------------------------------------------------------------------ binding
def load(archive_path=None, member_overrides=None, byte_overrides=None):
    """Check the byte binding (B1-B12) and return the decoded inputs. The keyword arguments exist only for the
    packaging controls in test_package.py (decoy members, flipped bytes)."""
    arc = CASES['archive']
    raw = (Path(archive_path) if archive_path else ROOT / arc['path']).read_bytes()
    need(sha(raw) == arc['sha256'], 'B1 archive digest')
    need(find_pin(json.loads((ROOT / arc['pinned_by']).read_text()), arc['path'], arc['sha256']), 'B1 archive pin')
    members = dict(CASES['members'], **(member_overrides or {}))
    with tarfile.open(fileobj=io.BytesIO(raw), mode='r:gz') as tar:          # parse exactly the hashed bytes
        index = safe_members(tar)

        def member(path):
            full = CASES['prefix'] + path
            need(full in index, 'B2 archive member present: ' + path)
            return tar.extractfile(index[full]).read()
        got = {k: member(p) for k, p in members.items()}
        twin = {k: member(CASES['twin_prefix'] + Path(p).name) for k, p in CASES['members'].items()
                if p.startswith('global/base/providers/gauge44/')}
    got.update(byte_overrides or {})
    # B3 certificate and record
    repo_asm = (ROOT / CASES['certificate']).read_bytes()
    need(repo_asm == got['assembly'] and sha(repo_asm) == CASES['certificate_sha256'], 'B3 certificate')
    # only the selected record, or the frontier1094 checkpoint once the frontier moves on
    records = [ROOT / CASES['selected_record'], ROOT / CASES['checkpoint_dir'] / 'frontier1094.json']
    named = False
    for f in records:
        try:
            rec = json.loads(f.read_text()) if f.is_file() else {}
        except ValueError:
            rec = {}
        rec = rec if isinstance(rec, dict) else {}
        named = named or (rec.get('certificate') == CASES['certificate'] and rec.get('certificate_sha256') == sha(repo_asm))
    need(named, 'B3 a selected or checkpoint record names the certificate')
    asm = strict_loads(got['assembly'])
    # B4 template, B5 owner audit
    template_raw = gzip.decompress(got['template'])
    need(sha(template_raw) == asm['template_sha256'], 'B4 template digest')
    need(sha(got['owner_audit']) == asm['input_sha256']['owner_audit'], 'B5 owner audit digest')
    audit = strict_loads(got['owner_audit'])
    need(audit['template_sha256'] == asm['template_sha256'], 'B5 owner audit template')
    # B6 raw-byte digests of the provider files, from the owner audit
    for key, art in CASES['source_artifact_keys'].items():
        need(sha(got[key]) == audit['source_artifacts'][art], 'B6 provider file digest: ' + key)
    word_raw = gzip.decompress(got['canonical_word'])
    programs_raw = gzip.decompress(got['local_programs'])
    word, recipes = strict_loads(word_raw), strict_loads(got['recipes'])
    programs, review = strict_loads(programs_raw), strict_loads(got['review'])
    template = strict_loads(template_raw)
    # B7 the template's gauge44 provider binds the same files and word parameters
    t = template['local_providers']['gauge44']
    need(t['exact_local_clifford_recipe_sha256'] == sha(got['recipes']), 'B7 template binds the recipes')
    need(t['canonical_word_sha256'] == sha(got['canonical_word']), 'B7 template binds the word')
    need(t['local_programs_sha256'] == sha(got['local_programs']) and t['local_programs'] == programs, 'B7 template binds the programs')
    need(t['ports'] == word['ports'] and t['centers'] == word['centers'], 'B7 template ports and centres')
    exp = CASES['expected']
    need((t['R'], t['h'], t['v']) == (word['R'], word['h'], word['v']) == (exp['R'], exp['h'], exp['v']), 'B7 word parameters')
    # B8 SLOT-PINS (repository file listed in the selected source manifest)
    ss, sp = CASES['selected_source'], CASES['slot_pins']
    ss_raw = (ROOT / ss['path']).read_bytes()
    need(sha(ss_raw) == ss['sha256'] and find_pin(json.loads((ROOT / arc['pinned_by']).read_text()), ss['path'], ss['sha256']),
         'B8 selected source manifest pinned')
    sp_raw = (ROOT / sp['path']).read_bytes()
    need(sha(sp_raw) == sp['sha256'] and find_pin(strict_loads(ss_raw), sp['path'], sp['sha256']),
         'B8 SLOT-PINS pinned by path in the source manifest')
    pins = strict_loads(sp_raw)
    need(pins['canonical_sha256'] == sha(word_raw), 'B8 SLOT-PINS word payload digest')     # payload, not gz bytes (B9)
    need(pins['clifford_recipes_sha256'] == sha(got['recipes']), 'B8 SLOT-PINS recipes digest')
    need(all(pins['program_sha256'][o] == sha(json.dumps(programs[o], separators=(',', ':')).encode())
             for o in ('forward', 'backward')), 'B8 SLOT-PINS program digests')
    # B10 the producer's review: consistency only, never evidence
    need(review['status'] == exp['review_status'] and review['recipe_sha256'] == sha(got['recipes'])
         and review['canonical_word_sha256'] == sha(got['canonical_word']), 'B10 review binds the same files')
    # B11 canonical encodings
    need(got['recipes'] == canonical_bytes(recipes) and word_raw == canonical_bytes(word), 'B11 canonical encodings')
    binding = dict(record_or_checkpoint='certificates/selected-result.json or certificates/checkpoints/frontier1094.json',
                   certificate=CASES['certificate'], certificate_sha256=sha(repo_asm), archive=arc['path'],
                   archive_sha256=arc['sha256'], template_sha256=asm['template_sha256'],
                   owner_audit_sha256=asm['input_sha256']['owner_audit'],
                   recipes_sha256=sha(got['recipes']), canonical_word_gz_sha256=sha(got['canonical_word']),
                   canonical_word_payload_sha256=sha(word_raw), local_programs_gz_sha256=sha(got['local_programs']),
                   review_sha256=sha(got['review']), slot_pins_sha256=sp['sha256'],
                   global8_twin_byte_identical=all(twin[k] == got[k] for k in twin))       # B12, informational
    return dict(word=word, recipes=recipes, programs=programs, review=review), binding


# ------------------------------------------------------------------------------------------------ inventory
def is_int(x):
    return type(x) is int


def nested(small, large):
    return C.f2_rank(list(large)) == C.f2_rank(list(large) + list(small))


def inventory(data):
    """I1-I7. Returns (children, adapters, counts)."""
    word, recipes, programs = data['word'], data['recipes'], data['programs']
    exp = CASES['expected']
    frames, v = word['frames'], word['v']
    # I1 frames
    need(len(frames) == exp['frames'], 'I1 frame count')
    need(all(isinstance(U, list) and all(is_int(x) and 0 < x < C.DIM for x in U) and C.f2_rank(U) == len(U)
             for U in frames), 'I1 frames are independent row lists')
    need(frames[0] == [] and frames[1] == [1 << i for i in reversed(range(C.N_AXES))], 'I1 empty and full frames')
    dims = Counter(str(len(U)) for U in frames)
    need(dict(dims) == exp['frame_dims'], 'I1 frame dimensions')
    centres = word['center_frames']
    need(all(len(frames[f]) == 8 for f in centres), 'I1 centre frames have dimension 8')
    # I2 children = directed edges (+ both centre directions)
    edges = [tuple(e) for e in word['edges']]
    E = set(edges) | {(f, 0) for f in centres} | {(0, f) for f in centres}
    need(len(edges) == len(set(edges)) and set(edges) == E and len(E) == exp['children'], 'I2 edge inventory')
    children = recipes['children']
    need(set(recipes) == {'children', 'endpoint_adapters'}, 'I2 recipe file keys')
    need([(c['old'], c['new']) for c in children] == sorted(E), 'I2 one record per edge, sorted')
    # I3 each child
    ranks = Counter()
    descending = 0
    for c in children:
        need(set(c) == {'left', 'new', 'old', 'rank', 'right'} and isinstance(c['right'], dict), 'I3 child keys')
        a, b, r = c['old'], c['new'], c['rank']
        need(is_int(r) and r >= 1 and r == abs(len(frames[a]) - len(frames[b])), 'I3 child rank')
        small, large = (frames[a], frames[b]) if len(frames[a]) < len(frames[b]) else (frames[b], frames[a])
        need(nested(small, large), 'I3 nested spans')
        if len(frames[a]) > len(frames[b]):
            descending += 1
            need(b == 0 and a in centres, 'I3 only centre reversals descend')
        ranks[str(r)] += 1
    need(dict(ranks) == exp['child_ranks'] and descending == exp['descending_children'], 'I3 rank histogram')
    # I4 endpoint adapters
    adapters = recipes['endpoint_adapters']
    need([(x['port'], x['role']) for x in adapters] == [(p, r) for p in range(v) for r in ('source', 'target')],
         'I4 adapter order')
    for x in adapters:
        need(set(x) == {'frame', 'left', 'port', 'rank', 'right', 'role'} and x['rank'] == 0 and x['right'] is None,
             'I4 adapter keys')
        p = x['port']
        if x['role'] == 'source':
            need(x['frame'] == word['start'][p] and frames[x['frame']] == [word['ports'][p]], 'I4 source frame')
        else:
            need(x['frame'] == word['final'][v + p] and len(frames[x['frame']]) == 8, 'I4 target frame')
    need(dict(Counter(str(bin(q).count('1')) for q in word['ports'])) == exp['port_weights'], 'I4 port weights')
    # I5 / I6 program events
    keys = set()
    for o in ('forward', 'backward'):
        ev = Counter()
        okeys = set()
        for e in programs[o]:
            if e[0] == 'climb':
                key = (e[3], e[4])
                need(key in E and e[5] == abs(len(frames[e[3]]) - len(frames[e[4]])), 'I5 climb key and rank')
                okeys.add(key)
                ev['climb'] += 1
            elif e[0] == 'center':
                f = centres[e[1]]
                need((e[2], e[3]) == ((f, 0) if o == 'forward' else (0, f)) and e[4] == 8, 'I5 centre key')
                okeys.add((e[2], e[3]))
                ev['center'] += 1
            elif e[0] == 'adapter':
                _, way, r, f = e
                if way == 'old_to_new':
                    need(f == (word['start'][r] if r < v else 0), 'I6 entry adapter frame')
                else:
                    need(way == 'new_to_old' and f == (word['final'][r] if v <= r < 2 * v else 1), 'I6 exit adapter frame')
                ev['adapter'] += 1
        need(dict(ev) == exp['events_per_orientation'], 'I5 event counts: ' + o)
        keys |= okeys
    need(keys == E, 'I5 relabel keys of both orientations = the record inventory')
    need(all(word['final'][p] == 1 for p in range(v)), 'I6 every source port ends in the full frame')
    # I7 monomials
    monos = [c[s] for c in children for s in ('left', 'right')] + [x['left'] for x in adapters]
    need(all(C.well_formed(m) for m in monos), 'I7 monomial records well formed')
    return children, adapters, dict(child_ranks=dict(sorted(ranks.items())), descending=descending, monomials=len(monos),
                                    relabel_keys=len(keys), frames=len(frames))


# ------------------------------------------------------------------------------------------------ calibration
def lean_fixtures():
    fx = CASES['fixtures']['lean_exact']
    raw = (ROOT / fx['path']).read_bytes()
    need(sha(raw) == fx['sha256'], 'FX1 Exact.lean pinned')
    text = raw.decode()
    num = r'\[([\d,\s]*)\]'

    def ints(s):
        return [int(x) for x in re.findall(r'\d+', s)]

    def gates(name):
        m = re.search(r'^def %s : List Gate :=\n(.*?)\n\n' % name, text, re.S | re.M)
        need(m is not None, 'FX1 literal present: ' + name)
        out = []
        for g in re.finditer(r'\.(dg|pm)\s*' + num + r'\s*' + num + r'|\.cg\s+(\d+)\s+(true|false)|\.(xg|ph)\s+(\d+)', m.group(1)):
            if g.group(1):
                out.append((g.group(1), ints(g.group(2)), ints(g.group(3))))
            elif g.group(4):
                out.append(('cg', int(g.group(4)), g.group(5) == 'true'))
            else:
                out.append((g.group(6), int(g.group(7))))
        return out
    mono = r'⟨' + num + r',\s*' + num + r',\s*' + num + r',\s*(\d+),\s*(\d+)⟩'
    pairs = []
    for k in (1, 2, 3):
        m = re.search(r'def pair%d : Pair := ⟨' % k + num + r',\s*' + num + r',\s*' + mono + r',\s*' + mono + r'⟩', text)
        need(m is not None, 'FX1 pair literal %d' % k)
        g = m.groups()

        def as_mono(i):
            return dict(quadratic_rows=ints(g[i]), linear_Z4=ints(g[i + 1]), matrix_rows=ints(g[i + 2]),
                        offset=int(g[i + 3]), phase=int(g[i + 4]))
        pairs.append(dict(E=ints(g[0]), U=ints(g[1]), L=as_mono(2), R=as_mono(7),
                          fE=gates('fE%d' % k), fU=gates('fU%d' % k), wL=gates('wL%d' % k), wR=gates('wR%d' % k)))
    return pairs


def matrix_digest_1415(circuit):
    """#1415's operator digest: per column x, reduce by 2 while all numerators are even, hash
    [e, [[y, re, im] ...]] lines (hpe-lean-semantic-binding/verify.py)."""
    k = C.c_gates(circuit)
    beta = C.radix(k)
    cols = C.columns(C.run(circuit, beta), beta)
    h, dens, nonzero = hashlib.sha256(), set(), 0
    for x in range(C.DIM):
        col, e = dict(cols.get(x, {})), k
        while e > 0 and all(re_ % 2 == 0 and im % 2 == 0 for re_, im in col.values()):
            col = {y: (re_ // 2, im // 2) for y, (re_, im) in col.items()}
            e -= 1
        dens.add(e)
        nonzero += len(col)
        h.update((json.dumps([e, [[y, col[y][0], col[y][1]] for y in sorted(col)]], sort_keys=True, separators=(',', ':')) + '\n').encode())
    return h.hexdigest(), sorted(dens), nonzero


def kernel_digest_702(circuit):
    """#702's frame-kernel digest: numerators over 2^k, unreduced, column by column (cold-wrapper-amplitude-audit)."""
    k = C.c_gates(circuit)
    beta = C.radix(k)
    cols = C.columns(C.run(circuit, beta), beta)
    body = [[[y, cols[x][y][0], cols[x][y][1]] for y in sorted(cols.get(x, {}))] for x in range(C.DIM)]
    return sha(json.dumps(body, sort_keys=True, separators=(',', ':')).encode()), k


def calibrate(frames):
    out = {}
    # FX1 Lean literals: gate lists and the three rank-7 pair identities (Exact.lean check1-3)
    pairs = lean_fixtures()
    for k, p in enumerate(pairs, 1):
        need(C.lean_syntax(C.canonical_frame(p['E'])) == p['fE'], 'FX1 canon(E%d) = fE%d' % (k, k))
        need(C.lean_syntax(C.canonical_frame(p['U'])) == p['fU'], 'FX1 canon(U%d) = fU%d' % (k, k))
        need(C.lean_syntax(C.monomial(p['L'])) == p['wL'] and C.lean_syntax(C.monomial(p['R'])) == p['wR'],
             'FX1 monomials %d' % k)
        need(C.same_operator(C.canonical_frame(p['E']) + C.monomial(p['R']) + C.fourier(7) + C.monomial(p['L']),
                             C.canonical_frame(p['U'])), 'FX1 pair %d identity' % k)
    out['lean_exact'] = '3 pairs: canon gate lists, monomial gate lists and rank-7 identities equal the Exact.lean literals'
    # FX2 #1415 operator digests of T_U o T_E^-1 (exercises the adjoint)
    fx = CASES['fixtures']['pr1415']
    raw = (ROOT / fx['path']).read_bytes()
    need(sha(raw) == fx['sha256'], 'FX2 #1415 RESULT pinned')
    for k, (f, p) in enumerate(zip(strict_loads(raw)['factorizations'], pairs), 1):
        need(f['entrance'] == p['E'] and f['terminal'] == p['U'], 'FX2 pair frames %d' % k)
        digest, dens, nonzero = matrix_digest_1415(C.adjoint(C.canonical_frame(p['E'])) + C.canonical_frame(p['U']))
        need(digest == f['left']['matrix_sha256'] and dens == f['left']['denominator_exponents']
             and nonzero == f['left']['nonzero_entries'], 'FX2 #1415 digest %d' % k)
    out['pr1415'] = '3 operator digests of T_U o T_E^-1 reproduced'
    # FX3 #702 frame kernels: all 14 are frames of this word
    fx = CASES['fixtures']['pr702']
    raw = (ROOT / fx['path']).read_bytes()
    need(sha(raw) == fx['sha256'], 'FX3 #702 EXPECTED pinned')
    index = {tuple(U): i for i, U in enumerate(frames)}
    found = []
    for ident in strict_loads(raw)['identities']:
        U = ident['frame']
        need(tuple(U) in index, 'FX3 #702 frame is a word frame')
        digest, k = kernel_digest_702(C.canonical_frame(U))
        need(digest == ident['kernel_sha256'] and (1 << k) == ident['amplitude_denominator'], 'FX3 #702 kernel digest')
        found.append(index[tuple(U)])
    out['pr702'] = '%d frame kernels reproduced (word frames %s)' % (len(found), sorted(found))
    # FX5 hand values; FX6 shortcut agreement; FX7 basis dependence
    cols = C.columns(C.run(C.canonical_frame(frames[2]), C.radix(1)), C.radix(1))
    need(frames[2] == [30] and cols[0] == {0: (1, 1), 30: (-1, -1)} and cols[1] == {1: (1, 1), 31: (-1, -1)}, 'FX5 T([30])')
    need(C.same_operator(C.canonical_frame(frames[1], shortcuts=False), C.fourier(9))
         and C.same_operator(C.canonical_frame(frames[0], shortcuts=False), []), 'FX6 shortcuts agree')
    for f in (174, 415):
        U = frames[f]
        need(C.same_operator(C.canonical_frame(list(reversed(U))), C.canonical_frame(U)), 'FX7 reordered rows: same T')
        need(not C.same_operator(C.canonical_frame([U[0] ^ U[1]] + U[1:]), C.canonical_frame(U)), 'FX7 other basis: other T')
    out['hand_and_structure'] = 'hand values, shortcut agreement and basis dependence'
    return out


# ------------------------------------------------------------------------------------------------ evaluation
def child_circuits(c, frames, variant=None):
    """side1 = T_old + R + F_r + L (first applied first), side2 = T_new; variant selects a mutation control."""
    a, b, r = c['old'], c['new'], c['rank']
    L, R = c['left'], c['right']
    Fr = C.fourier(r)
    order = 'DPXPH'
    if variant == 'one_gate':
        Fr = [('C', (1 << r) - 1, 1)]
    elif variant == 'fourier_sign':
        Fr = [('C', 1, -1)] + Fr[1:]
    elif variant == 'swap_wrappers':
        L, R = R, L
    elif variant == 'direction':
        a, b = b, a
    elif variant == 'gate_order':
        order = 'PDXPH'
    return C.canonical_frame(frames[a]) + C.monomial(R, order) + Fr + C.monomial(L, order), C.canonical_frame(frames[b])


def adapter_circuits(x, word, variant=None):
    p, role, frames = x['port'], x['role'], word['frames']
    q = word['ports'][(p + 1) % word['v']] if variant == 'port' else word['ports'][p]
    if variant == 'role':
        role = 'target' if role == 'source' else 'source'
    order = 'PDXPH' if variant == 'gate_order' else 'DPXPH'
    sign = -1 if variant == 'fourier_sign' else 1
    M = C.monomial(x['left'], order)
    T = C.canonical_frame(frames[x['frame']])
    if role == 'source':
        return [('C', q, sign)] + M, T
    return [('C', q, -sign)] + C.fourier(9) + M, T


def check_pair(c1, c2):
    return C.same_operator(c1, c2)


def evaluate(children, adapters, word, subset=None, receipts=None):
    """Every child and adapter identity, exact on all 512 columns. Returns counts and the K histogram."""
    frames = word['frames']
    sel_c, sel_a = subset_filter(subset, children, adapters, frames)
    groups = {}
    for c in sel_c:
        groups.setdefault(c['new'], []).append(c)
    order = sorted(groups, key=lambda b: (len(frames[b]), b))
    Ks = Counter()
    chain = hashlib.sha256(b'').hexdigest()
    lines = []

    def emit(obj):
        nonlocal chain
        line = canonical_bytes(dict(obj, prev=chain))
        chain = sha(line)
        lines.append(line)
    emit(dict(kind='header', schema=1, checker_sha256=sha((HERE / 'verify.py').read_bytes()),
              kernel_sha256=sha((HERE / 'clifford.py').read_bytes()), radix_rule='beta=2K+2', subset=subset))
    t0 = time.process_time()
    done_c = 0
    for b in order:
        grp = groups[b]
        k2 = C.c_gates(C.canonical_frame(frames[b]))
        Kmax = max(max(len(frames[c['old']]) + c['rank'], k2) for c in grp)
        beta = C.radix(Kmax)
        side2 = C.run(C.canonical_frame(frames[b]), beta)
        for c in grp:
            c1, _ = child_circuits(c, frames)
            k1 = C.c_gates(c1)
            need(C.equal(C.run(c1, beta), k1, side2, k2, beta), 'E child %d:%d' % (c['old'], c['new']))
            Ks[max(k1, k2)] += 1
            done_c += 1
        emit(dict(kind='children', new=b, dim_new=len(frames[b]), K=Kmax, beta=beta,
                  pairs=[[c['old'], c['new']] for c in grp], status='EXACT'))
    done_a = 0
    for x in sel_a:
        c1, c2 = adapter_circuits(x, word)
        need(check_pair(c1, c2), 'E adapter %d %s' % (x['port'], x['role']))
        done_a += 1
        emit(dict(kind='adapter', port=x['port'], role=x['role'], frame=x['frame'], status='EXACT'))
    if subset is None:
        emit(dict(kind='complete', children=done_c, adapters=done_a))
    if receipts:
        Path(receipts).write_bytes(b'\n'.join(lines) + b'\n')
    return dict(children=done_c, adapters=done_a, K_histogram={str(k): n for k, n in sorted(Ks.items())},
                receipts_sha256=sha(b'\n'.join(lines) + b'\n'), cpu_seconds=round(time.process_time() - t0, 1))


def subset_filter(spec, children, adapters, frames):
    if spec is None:
        return children, adapters
    sc, sa = list(children), list(adapters)
    for term in spec.split(','):
        key, _, val = term.partition('=')
        if key == 'dim':
            lo, _, hi = val.partition('..')
            lo, hi = int(lo), int(hi or lo)
            sc = [c for c in sc if lo <= len(frames[c['new']]) <= hi]
        elif key == 'rank':
            sc = [c for c in sc if c['rank'] == int(val)]
        elif key == 'pair':
            a, b = map(int, val.split(':'))
            sc = [c for c in sc if (c['old'], c['new']) == (a, b)]
        elif key == 'ports':
            lo, _, hi = val.partition('-')
            sa = [x for x in sa if int(lo) <= x['port'] <= int(hi or lo)]
        elif key == 'children' and val == 'none':
            sc = []
        elif key == 'adapters' and val == 'none':
            sa = []
        else:
            raise SystemExit('unknown subset term: ' + term)
    return sc, sa


# ------------------------------------------------------------------------------------------------ controls
SAMPLE_CHILDREN = ((0, 2), (0, 174), (37, 1), (0, 415), (415, 0))
SAMPLE_ADAPTERS = (0, 1)


def _mutate(rec, path, fn):
    out = json.loads(json.dumps(rec))
    obj = out
    for k in path[:-1]:
        obj = obj[k]
    obj[path[-1]] = fn(obj[path[-1]])
    return out


def semantic_controls(children, adapters, word):
    """Each mutation must be rejected on every sample record it applies to; the reordered-rows frame is a
    positive control that must pass. Returns {control: 'rejected k/k'}."""
    frames = word['frames']
    by_key = {(c['old'], c['new']): c for c in children}
    sample_c = [by_key[k] for k in SAMPLE_CHILDREN]
    sample_a = [adapters[i] for i in SAMPLE_ADAPTERS]
    for c in sample_c:
        need(check_pair(*child_circuits(c, frames)), 'C sample child passes unmutated')
    for x in sample_a:
        need(check_pair(*adapter_circuits(x, word)), 'C sample adapter passes unmutated')

    def cz(Q):
        Q = list(Q)
        Q[6] ^= 1 << 7
        Q[7] ^= 1 << 6
        return Q
    record_mutations = {
        'global_phase': (('left', 'phase'), lambda p: (p + 1) % 4),
        'input_character': (('right', 'linear_Z4'), lambda a: a[:5] + [(a[5] + 2) % 4] + a[6:]),
        'cz_cross_term': (('left', 'quadratic_rows'), cz),
        'translation': (('right', 'offset'), lambda b: b ^ 256),
    }
    out = {}
    for name, (path, fn) in record_mutations.items():
        rej = 0
        for c in sample_c:
            rej += not check_pair(*child_circuits(_mutate(c, path, fn), frames))
        apath = ('left', path[1])                  # adapters carry only a left monomial
        for x in sample_a:
            rej += not check_pair(*adapter_circuits(_mutate(x, apath, fn), word))
        need(rej == len(sample_c) + len(sample_a), 'C control not rejected: ' + name)
        out[name] = 'rejected %d/%d' % (rej, rej)
    for variant in ('swap_wrappers', 'direction', 'gate_order', 'fourier_sign', 'one_gate'):
        cands = [c for c in sample_c if variant != 'one_gate' or c['rank'] >= 2]
        rej = sum(not check_pair(*child_circuits(c, frames, variant)) for c in cands)
        if variant == 'fourier_sign':      # C_q sign flip on the adapters (the target then reads T_f C_q^-1 F_9^-1)
            rej += sum(not check_pair(*adapter_circuits(x, word, variant)) for x in sample_a)
            cands = cands + sample_a
        # gate_order is children only: for every endpoint adapter q(Gx) = q(x), so evaluating D after P is the
        # same operator (counted in gate_order_equivalent_adapters below); the order is pinned by the children
        # controls and by FX1's comparison with the Lean Mono.gates literals
        need(rej == len(cands), 'C control not rejected: ' + variant)
        out[variant] = 'rejected %d/%d' % (rej, rej)
    for variant in ('port', 'role'):
        rej = sum(not check_pair(*adapter_circuits(x, word, variant)) for x in sample_a)
        need(rej == len(sample_a), 'C control not rejected: adapter ' + variant)
        out['adapter_' + variant] = 'rejected %d/%d' % (rej, rej)
    # frame basis: same span, other basis -> rejected; same rows reordered -> passes (positive control)
    rej = passed = 0
    for key in ((0, 174), (0, 415)):
        c = by_key[key]
        U = frames[c['new']]
        alt = list(frames)
        alt[c['new']] = [U[0] ^ U[1]] + U[1:]
        rej += not check_pair(*child_circuits(c, alt))
        alt[c['new']] = list(reversed(U))
        passed += check_pair(*child_circuits(c, alt))
    need(rej == 2 and passed == 2, 'C frame basis control')
    out['frame_basis'] = 'rejected 2/2; reordered rows pass 2/2'
    return out


def gate_order_equivalent_adapters(adapters):
    """How many endpoint monomials are unchanged when D is evaluated after P (a structural fact, not a control)."""
    return sum(C.same_operator(C.monomial(x['left']), C.monomial(x['left'], 'PDXPH')) for x in adapters)


# ------------------------------------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--write', action='store_true')
    ap.add_argument('--subset', default=None)
    ap.add_argument('--receipts', default=None)
    a = ap.parse_args()
    if a.write and a.subset:
        raise SystemExit('--write needs a full run')
    need(not any(m.split('.')[0] in FORBIDDEN for m in sys.modules), 'independence: no producer module loaded')
    data, binding = load()
    children, adapters, counts = inventory(data)
    calibration = calibrate(data['word']['frames'])
    controls = semantic_controls(children, adapters, data['word'])
    ev = evaluate(children, adapters, data['word'], subset=a.subset, receipts=a.receipts)
    need(not any(m.split('.')[0] in FORBIDDEN for m in sys.modules), 'independence: no producer module loaded')
    if a.subset is not None:
        print('children %d adapters %d (%.1f s CPU)' % (ev['children'], ev['adapters'], ev['cpu_seconds']))
        print('PARTIAL_FRONTIER1094_RECIPES_EXACT subset=%s' % a.subset)
        return
    exp = CASES['expected']
    need(ev['children'] == exp['children'] and ev['adapters'] == exp['adapters'], 'E full coverage')
    ev.pop('cpu_seconds')
    counts['gate_order_equivalent_adapters'] = '%d of %d' % (gate_order_equivalent_adapters(adapters), len(adapters))
    result = dict(status='PASS_FRONTIER1094_RECIPES_EXACT', binding=binding, inventory=counts, calibration=calibration,
                  controls=controls, evaluation=dict(ev, columns=C.DIM, global_phase_included=True,
                                                     comparator='exact packed Gaussian integers, scaled to a common 2^K',
                                                     radix_rule='beta = 2K + 2'),
                  scope='Record level: every child record and endpoint adapter of the gauge44 CLIFFORD-RECIPES.json equals '
                        'T_new T_old^-1 (climb and centre relabels) or satisfies Lemma G H6; not the 36 residual wrapper '
                        'recipes, the identity adapters, the executor bridge, a Lean proof or a new kappa')
    text = json.dumps(result, indent=1, sort_keys=True) + '\n'
    target = HERE / 'RESULT.json'
    if a.write:
        target.write_text(text)
    else:
        need(target.read_text() == text, 'RESULT.json reproduced byte for byte')
    print('children %d adapters %d columns %d  K %s' % (ev['children'], ev['adapters'], C.DIM, ev['K_histogram']))
    print('PASS_FRONTIER1094_RECIPES_EXACT')


if __name__ == '__main__':
    try:
        main()
    except Reject as exc:
        raise SystemExit('FAIL ' + str(exc))
