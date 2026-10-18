# Mutation controls for the punctured-word hosted chain.  Every mutant is built from the SHIPPED word (or from the chain's
# own emitted files) by one change, pushed through the real chain stages, and must be refused by a named stage.
# Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code. Apache-2.0.
"""usage: mutants.py WORD.json.gz WD ADAPTED_DIR PARENT_PACKAGE HOSTING.json OUT.json
WD is verify.py's work dir after steps 1-5 (bin/, records/, cin/, cout/, nine/, bit/, interface.json).

  word-level  (the mutated word goes through the relaxed independent checker, the exporter, the official legality and
               five-stage / eleven-stage column checkers, and the emitter's gate on their receipts):
    M1 dropped gate        delete the phase-A gate that forms the first retained total
    M2 wrong frame         move a phase-B gate to the zero frame (below the frames its registers already stand at)
    M3 payload overflow    an F2-neutral block of Fibonacci-growth ADDs on two helpers: legal, restores every column,
                           but the signed prefix payload exceeds 2^104 -> refused by columns_h only
  template-level (the chain's own emitted files, tampered; audit.py must refuse, the hashes of the tampered file re-written
               so that only the semantic checks can catch it):
    M4a cell collision (#442 rule)       two helpers of one invocation given the same physical family AND hosted cells.
                                         (NOT a test of #458's one-helper-per-family rule: the pooled whole-residual hosting of
                                         #442/#472/#493/#503 stacks several helpers on one family at disjoint cells; see README)
    M4b hosted on the invoked pair       a helper's residual placed on the data family the call itself acts on
    M5  profile claim                    GLOBAL.json claims a cheaper paid profile than the template's
  assembly-level:
    M6  v tied to the complex word       GLOBAL.json v := 112 (the cited complex v); assemble.py must refuse
    M7  the stock PR #493 emitter        refuses any word with v != 120 (what the parameterisation had to change)"""
import copy
import gzip
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

WORD, WD, AD, PARENT, HOST, OUT = map(Path, sys.argv[1:7])
PY = sys.executable
B = PARENT / 'code/bit'; C = PARENT / 'code'
sys.path.insert(0, str(Path(__file__).resolve().parent))
import punct_cfg as PC  # noqa: E402

w0 = PC.load(WORD); V, R = w0['v'], w0['R']
BIN = WD / 'bin'
LEG = BIN / 'legality'; COLH = BIN / ('columns_h_v%d_r%d' % (V, R)); COLK = BIN / ('columns_k5_v%d_r%d' % (V, R))
PROBE = BIN / ('columns_probe_v%d_r%d' % (V, R))
MD = WD / 'mut'; shutil.rmtree(MD, ignore_errors=True); MD.mkdir()
controls = []


def run(cmd, **kw):
    return subprocess.run([str(x) for x in cmd], capture_output=True, text=True, **kw)


def last(p):
    t = (p.stderr.strip().splitlines() or p.stdout.strip().splitlines() or ['?'])
    return t[-1][:110]


def save_word(w, p):
    with gzip.open(p, 'wt') as f: json.dump(w, f)


def through_chain(w, tag):
    """returns [(stage, rejected, message)] and stops reading further stages' receipts as in the real chain."""
    d = MD / tag; d.mkdir(); wp = d / 'word.json.gz'; save_word(w, wp); out = []
    p = run([PY, '-I', '-B', AD / 'rchk/checkword_mut.py', wp, C / 'pricing'])
    out.append(('relaxed independent checker (exact F2 replay, frames)', p.returncode != 0, last(p)))
    p = run([PY, '-I', '-B', B / 'export_records.py', wp, d / 'records']); assert p.returncode == 0, p.stderr
    p = run([PY, '-I', '-B', B / 'regression/stage_cohort.py', d / 'records', d / 'records', d / 'cin', d / 'cout']); assert p.returncode == 0, p.stderr
    p = run([LEG, d / 'cin', d / 'cout', d / 'cout/legality.json'])
    out.append(('official legality (frames, lifecycle, COPY ranks)', p.returncode != 0, last(p)))
    p = run([COLH, d / 'cout/COHORT249-RECORDS.bin', d / 'cout/columns.json'])
    out.append(('official five-stage columns_h (all columns, payload < 2^104)', p.returncode != 0, last(p)))
    p = run([COLK, d / 'cout/COHORT249-RECORDS.bin', d / 'cout/columns_k5.json'])
    out.append(('official eleven-stage columns_k', p.returncode != 0, last(p)))
    # the emitter's gate: it needs legality.json and columns.json with a PASS status; a refused word leaves none
    (d / 'bit').mkdir()
    shutil.copy(WD / 'bit/GEOMETRY.json', d / 'bit/GEOMETRY.json')
    p = run([PY, '-E', '-s', '-B', AD / 'emit.py', '--word', wp, '--local-check', d, '--out', d / 'bit', '--isometries',
             PARENT / 'data/eleven/residual-isometries.json', '--hosting', HOST])
    out.append(('hosted emitter (needs PASS receipts of the two official checkers)', p.returncode != 0, last(p)))
    return out, d


def record(name, what, stages, require_reject_at=None):
    rej = [s for s in stages if s[1]]
    assert rej, ('ACCEPTED', name, stages)
    controls.append(dict(name=name, mutation=what, first_rejecting_stage=rej[0][0], message=rej[0][2],
                         stages=[dict(stage=s, rejected=r, message=m) for s, r, m in stages]))
    print('   REJECTED  %-26s first at: %s  [%s]' % (name, rej[0][0], rej[0][2][:70]))
    if require_reject_at:
        assert any(s[0].startswith(require_reject_at) and s[1] for s in stages), (name, require_reject_at, stages)


# ---------------------------------------------------------------------------------------------------- word-level
w = copy.deepcopy(w0)
tot = w['ret'][0]
k = max(i for i, g in enumerate(w['A']) if g[1] == tot)
dropped = w['A'].pop(k)
st, _ = through_chain(w, 'm1')
record('M1 dropped gate', 'deleted phase-A gate %d (frame %d, destination %d = the first retained total, %d sources)' % (k, dropped[0], dropped[1], len(dropped[2])),
       st, 'relaxed independent checker')
assert all(s[1] for s in st[:1] + st[2:3]), st      # the checker and columns_h both refuse; the emitter cannot run

w = copy.deepcopy(w0)
kb = len(w['B']) // 2
old = w['B'][kb][0]; zero = w['start'][2 * V]
w['B'][kb][0] = zero
st, _ = through_chain(w, 'm2')
record('M2 wrong frame', 'phase-B gate %d moved from frame %d to the zero frame %d' % (kb, old, zero), st, 'relaxed independent checker')

# M3: Fibonacci-growth block on helpers u, v (both at the zero frame at the start of phase A).  Over F2 the six-gate cycle
# (u += v, v += u) x 3 is the identity, so every column is restored and every frame is untouched; the integer bound grows
# like Fibonacci numbers.  Smallest block (in cycles) whose payload the probe reports >= 105 bits.
u, vv = 2 * V, 2 * V + 1
assert w0['start'][u] == w0['start'][vv] == zero
for cycles in range(1, 40):
    w = copy.deepcopy(w0)
    blk = []
    for _ in range(cycles * 3):
        blk += [[zero, u, [vv]], [zero, vv, [u]]]
    w['A'] = blk + w['A']
    d = MD / ('m3probe%d' % cycles); d.mkdir(); wp = d / 'word.json.gz'; save_word(w, wp)
    run([PY, '-I', '-B', B / 'export_records.py', wp, d / 'records'])
    run([PY, '-I', '-B', B / 'regression/stage_cohort.py', d / 'records', d / 'records', d / 'cin', d / 'cout'])
    p = run([PROBE, d / 'cout/COHORT249-RECORDS.bin', d / 'cout/probe.json'])
    bits = json.loads((d / 'cout/probe.json').read_text())['payload_prefix_bits'] if p.returncode == 0 else None
    if bits and bits >= 105: break
assert bits and bits >= 105, bits
st, _ = through_chain(w, 'm3')
assert not st[0][1] and not st[1][1], ('M3 must be a legal, F2-correct word that only the payload bound refuses', st)
record('M3 payload overflow', '%d cycles of the F2-neutral Fibonacci block (%d extra ADDs) at the start of phase A: payload %d bits >= 104 (shipped word: 95); '
       'the relaxed checker and legality PASS' % (cycles, 12 * cycles, bits), st, 'official five-stage columns_h')
assert 'payloadfiniteprefix2^104' in st[2][2] or 'payload' in st[2][2], st[2]

# ---------------------------------------------------------------------------------------------------- template-level
BIT = WD / 'bit'
tpl = json.loads(gzip.decompress((BIT / 'GLOBAL-TEMPLATE.json.gz').read_bytes()))
glob = json.loads((BIT / 'GLOBAL.json').read_text())


def tamper(tag, edit, glob_edit=None, expect=None):
    d = MD / tag; (d / 'bit').mkdir(parents=True)
    for f in ('GEOMETRY.json',): shutil.copy(BIT / f, d / 'bit' / f)
    t = copy.deepcopy(tpl); edit(t)
    blob = json.dumps(t, separators=(',', ':'), sort_keys=True).encode()
    (d / 'bit/GLOBAL-TEMPLATE.json.gz').write_bytes(gzip.compress(blob, mtime=0))
    g = copy.deepcopy(glob); g['template_sha256'] = hashlib.sha256(blob).hexdigest()       # re-hashed: only semantics can catch it
    if glob_edit: glob_edit(g)
    (d / 'bit/GLOBAL.json').write_text(json.dumps(g, indent=2) + '\n')
    p = run([PY, '-E', '-s', '-B', AD / 'audit.py', WD, WD / 'nine', d / 'bit'])
    if expect: assert p.returncode != 0 and expect in p.stderr, (tag, 'refused for another reason', p.stderr[-600:])
    return [('independent hosted audit (audit.py)', p.returncode != 0, last(p) + ' :: ' + (expect or ''))], d


call0 = lambda t: t['calls'][0]
st, _ = tamper('m4a', lambda t: call0(t)['owners'].__setitem__(2 * V + 1, copy.deepcopy(call0(t)['owners'][2 * V])),
               expect='len({(f,tuple(route)) for f,route in own})==2*V+R')
record('M4a cell collision', 'call 0: helper 1 given helper 0\'s physical family and hosted cells (two helpers on one owner AND one cell range; #442 disjoint-cells rule)', st)
fam0 = call0(tpl)['owners'][0][0]
st, _ = tamper('m4b', lambda t: call0(t)['owners'][2 * V].__setitem__(0, fam0), expect='pair[i]!=p')
record('M4b hosted on invoked pair', 'call 0 (pair %d): helper 0 re-homed to family %d, a data family the call itself acts on' % (call0(tpl)['pair'], fam0), st)
st, _ = tamper('m5', lambda t: None, lambda g: g.__setitem__('profile', dict(g['profile'], **{'56': g['profile']['56'] - 1, '55': 1})), expect='P==Counter(')
record('M5 profile claim', 'GLOBAL.json claims one rank-56 call as rank-55 (cheaper price) over the same template', st)

# ---------------------------------------------------------------------------------------------------- assembly-level
d = MD / 'm6'; (d / 'bit').mkdir(parents=True)
for f in ('GLOBAL-TEMPLATE.json.gz', 'GEOMETRY.json', 'AUDIT.json'): shutil.copy(BIT / f, d / 'bit' / f)
g = copy.deepcopy(glob); g['v'] = 112
(d / 'bit/GLOBAL.json').write_text(json.dumps(g, indent=2) + '\n')
p = run([PY, '-I', '-B', AD / 'assemble.py', d / 'bit', str(R), PARENT, d / 'RESULT.json', 'pr535', str(WORD.parent / 'complex-b.json')])
assert p.returncode != 0 and 'rem == 0' in p.stderr, ('M6 refused for another reason', p.stderr[-600:])
record('M6 v tied to complex v', 'GLOBAL.json v := 112 (the cited complex word\'s port count) with the 111-port bit audit',
       [('assemble.py (rank-mass deficit must fit nine copy ranks at the bit v)', p.returncode != 0, last(p))])
d = MD / 'm7'; (d / 'bit').mkdir(parents=True); shutil.copy(WD / 'bit/GEOMETRY.json', d / 'bit/GEOMETRY.json')
p = run([PY, '-E', '-s', '-B', C / 'eleven/emit.py', '--word', WORD, '--local-check', WD, '--out', d / 'bit', '--isometries',
         PARENT / 'data/eleven/residual-isometries.json', '--hosting', HOST])
assert p.returncode != 0 and "(8,120" in p.stderr, ('M7 refused for another reason', p.stderr[-600:])
record('M7 stock #493 emitter', 'PR #493\'s unmodified emit.py on the 111-port word', [('stock emitter (hard-coded v == 120)', p.returncode != 0, last(p))])

OUT.write_text(json.dumps(dict(all_rejected=True, controls=controls), indent=1) + '\n')
print('PASS %d mutation controls, every one rejected' % len(controls))
