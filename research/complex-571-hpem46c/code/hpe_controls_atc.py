"""controls_hpe_atc.py HPE-WORD.json.gz ROUTING OUTDIR : raw-word negative controls for the HPE extension of
audit_and_transport.py.  Every mutation MUST be rejected (AssertionError); the unmutated word MUST pass."""
import copy, gzip, json, shutil, sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import hpe_audit_and_transport as atc

src, routing, outdir = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
word = json.load(gzip.open(src))
v, R = word['report']['v'], word['report']['R']; n = 2*v + R
regs = lambda e: [e[1]] + ([e[2]] if e[0] == 'add' else [])
FULL = [1 << i for i in range(8, -1, -1)]


def trial(w):
    tmp = Path(tempfile.mkdtemp())
    p = tmp/'w.json.gz'; p.write_bytes(gzip.compress(json.dumps(w).encode(), mtime=0))
    try:
        atc.run(p, routing, tmp/'out')
        return True
    except AssertionError:
        return False
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


assert trial(word), 'unmutated HPE word must pass'
results = []


def reject(name, mut):
    w = copy.deepcopy(word); mut(w)
    assert not trial(w), 'HPE mutation accepted: ' + name
    results.append(name); print('rejected', name, flush=True)


cl = word['cleanup']
first = {}
for i, e in enumerate(cl):
    for r in regs(e): first.setdefault(r, i)
# a cleanup gate whose source register was written by an earlier cleanup gate: moving it ahead does not commute
nc = next(i for i, e in enumerate(cl) if e[0] == 'add' and any(cl[j][0] in ('add', 'scale') and cl[j][1] == e[2] for j in range(i)))
h0 = next(iter(word['helper_final'])); i0, U0 = word['early_cleanup'][0]


def move_noncommuting(w):  # frame FULL so only the scalar replay can object
    w['early_cleanup'].append([nc, FULL])
reject('early cleanup gate that does not commute with the skipped cleanup prefix', move_noncommuting)
reject('helper final frame not containing its last gate frame', lambda w: w['helper_final'].__setitem__(h0, w['helper_final'][h0][1:]))
reject('helper final frame on a register still touched by the FULL cleanup',
       lambda w: (w['early_cleanup'].pop(0)))
reject('early gate dropped from the program (helper not restored)',
       lambda w: (w['cleanup'].pop(i0), w['early_cleanup'].pop(0), [x.__setitem__(0, x[0]-1) for x in w['early_cleanup'] if x[0] > i0]))
reject('early gate frame below its registers\' frames', lambda w: w['early_cleanup'][0].__setitem__(1, U0[:-1]))
reject('hyperplane end on a non-entering helper', lambda w: (w['start_extra'].pop(h0)))
reject('profile not updated (paid climbs misreported)', lambda w: w['report']['local_profile'].__setitem__('1', w['report']['local_profile']['1']-3))
reject('profile without 8 partner U->FULL climb charges', lambda w: w['report']['local_profile'].__setitem__('1', w['report']['local_profile']['1']-8))
reject('duplicate early gate', lambda w: w['early_cleanup'].append(list(w['early_cleanup'][0])))

# Constructor controls for build_hpe's commutation rule (an early gate h -= p may skip earlier cleanup gates on p only
# when they commute with it, i.e. only read p).  base = the word without its hyperplane ends; a skipped gate that WRITES
# the partner (an addition into p or a scale of p) or touches h must make build_hpe.apply refuse the recipe, while a
# skipped gate that only reads p is accepted.
import build_hpe
base = copy.deepcopy(word); base.pop('early_cleanup'); base.pop('helper_final')
hf = {int(h) for h in word['helper_final']}
changes = []
for i, U in word['early_cleanup']:                  # pair each early gate with its helper via the gate's target
    h = cl[i][1]
    assert h in hf and word['helper_final'][str(h)] == U
    changes.append(dict(helper=h, cleanup_index=i, frame=U))
z0 = changes[0]; g0 = cl[z0['cleanup_index']]; p0 = g0[2]
x0 = next(r for r in range(2*v, n) if r not in {z['helper'] for z in changes} | {cl[z['cleanup_index']][2] for z in changes})
NONCOMMUTE = 'cleanup gate does not commute with the skipped cleanup gates on its registers'
ONEGATE = 'helper must have exactly this one cleanup gate'


def build_with(w):
    return build_hpe.apply(w, changes)


def inserted(pre):
    """base with gate `pre` inserted at cleanup position 0; the changes' indices shift by one"""
    w = copy.deepcopy(base); w['cleanup'].insert(0, pre)
    return w, [dict(z, cleanup_index=z['cleanup_index'] + 1) for z in changes]


def cfail(name, w, ch, expect):
    """the constructor must refuse with the pinned message `expect`"""
    try:
        build_hpe.apply(w, ch)
    except AssertionError as e:
        assert expect in str(e), ('constructor control %r failed with the wrong message: %s' % (name, e))
        results.append('constructor: ' + name); print('rejected constructor:', name, '--', expect, flush=True); return
    raise AssertionError('HPE constructor mutation accepted: ' + name)


build_hpe.apply(*inserted(['add', x0, p0, -1, 1, FULL]))   # positive: a skipped gate that only reads the partner commutes
cfail('skipped cleanup gate adds into the partner', *inserted(['add', p0, x0, -1, 1, FULL]), NONCOMMUTE)
cfail('skipped cleanup gate scales the partner', *inserted(['scale', p0, -1, 1, FULL]), NONCOMMUTE)
cfail('extra cleanup gate reading the helper (one-gate rule)', *inserted(['add', x0, z0['helper'], -1, 1, FULL]), ONEGATE)
cfail('extra cleanup gate adding into the helper (one-gate rule)', *inserted(['add', z0['helper'], x0, -1, 1, FULL]), ONEGATE)
# Real helpers admitted only by the commutation rule: their partner has an earlier cleanup gate x -= p (reads p).
# Flipping that gate in place to p -= x (writes p) must be refused by the commutation assert.
first = {}
for i, e in enumerate(cl):
    for r in regs(e): first.setdefault(r, i)
relaxed = [z for z in changes if any(first[r] < z['cleanup_index'] for r in regs(cl[z['cleanup_index']]))]
for z in relaxed:
    i = z['cleanup_index']; p = cl[i][2]
    j = next(j for j in range(i) if p in regs(cl[j]))
    e = cl[j]; assert e[0] == 'add' and e[2] == p and e[1] != p, ('skipped gate on a relaxed helper is not a reader', j, e)
    build_hpe.apply(copy.deepcopy(base), changes)       # positive: the real word's own changes
    w = copy.deepcopy(base); w['cleanup'][j] = ['add', p, e[1]] + e[3:]
    cfail('real helper %d: skipped gate %d flipped from %d -= %d to %d -= %d' % (z['helper'], j, e[1], p, p, e[1]), w, changes, NONCOMMUTE)
print('relaxed helpers', [z['helper'] for z in relaxed], flush=True)
outdir.mkdir(parents=True, exist_ok=True)
(outdir/'HPE-ATC-CONTROLS.json').write_text(json.dumps(dict(status='PASS_HPE_RAW_WORD_CONTROLS', word=str(src), rejected=results), indent=1) + '\n')
print('PASS', len(results), 'HPE raw-word mutations rejected')
