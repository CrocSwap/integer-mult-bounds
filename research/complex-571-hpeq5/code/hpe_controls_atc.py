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
reject('duplicate early gate', lambda w: w['early_cleanup'].append(list(w['early_cleanup'][0])))
outdir.mkdir(parents=True, exist_ok=True)
(outdir/'HPE-ATC-CONTROLS.json').write_text(json.dumps(dict(status='PASS_HPE_RAW_WORD_CONTROLS', word=str(src), rejected=results), indent=1) + '\n')
print('PASS', len(results), 'HPE raw-word mutations rejected')
