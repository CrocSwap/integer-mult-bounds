# Apache-2.0.  Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.  Independent Lemma G checker: imports no package script.
"""Independent Lemma G checker: labels, scalar replay, accounting.  Reads only the EMITTED artefacts of one variant
(CANONICAL-WORD.json.gz, LOCAL-PROGRAMS.json.gz or the hosted GLOBAL-TEMPLATE's local_programs). No package script is imported.

Semantics checked (see LEMMA-G.md):
  every register r carries a label lam(r) in the frame table; private centre copies ('C',k) too.
  G0  every scalar add / copy has both operands at ONE current label equal to the annotated frame; scale is annotated at the
      operand's label; a clear (re)declares the clean private copy at the annotated frame.
  G1  virtual entrance: an entering helper (start frame E != 0) starts at label E, receives exactly one R_E^-1 wrapper before any
      other event that touches it, and exactly one L_E^-1 wrapper after its last touch; no physical T_E (no adapter on it).
  G2  every transition of a non-private register is an ascending nested climb A < B charged |B|-|A| (no live copy meanwhile).
  G3  centre phase: copy at the centre's current label; every step of a copy is nested and strictly monotone (down in the forward
      orientation, up in the backward one), charged |A|-|B|; every scatter/gather meets the target at the copy's label; the copy is
      cleared; no non-private transition while a copy is live.
  G4  endpoint labels: start = word's start (sources: port lines, targets: 0, helpers: 0 or E), final = word's final.
  S   the scalar matrix of the stream (frames stripped) is exactly (x,s,y)->(x,s,y+x) forward and (x-y,s,y) backward, all columns,
      private copies cleared.
  ACC paid profile recount; per-register climb mass telescopes to dim(final)-dim(start); centre steps sum to dim(c_k) (bottom 0).
"""
import gzip, hashlib, json
from collections import Counter, defaultdict
from fractions import Fraction as Q
from pathlib import Path

PHASES = ['zero_frame_precondition', 'entry_adapters', 'A', 'centers', 'B', 'final', 'exit_adapters', 'full_frame_cleanup', 'done']


def rank2(vs):
    p = {}
    for x in vs:
        while x:
            b = x.bit_length() - 1
            if b not in p: p[b] = x; break
            x ^= p[b]
    return len(p)


class Frames:
    def __init__(self, frames):
        self.F = [tuple(f) for f in frames]; self.dim = [rank2(f) for f in self.F]
        assert all(self.dim[i] == len(f) for i, f in enumerate(self.F)), 'frame rows not independent'
        self._sub = {}
    def sub(self, a, b):      # frame a contained in frame b
        k = (a, b)
        if k not in self._sub: self._sub[k] = rank2(list(self.F[a]) + list(self.F[b])) == self.dim[b]
        return self._sub[k]


def digest(x): return hashlib.sha256(json.dumps(x, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def load(vdir, programs_from='template'):
    vdir = Path(vdir); sc = vdir / 'split-centres'
    c = json.loads(gzip.decompress((sc / 'CANONICAL-WORD.json.gz').read_bytes()))
    lp = json.loads(gzip.decompress((sc / 'LOCAL-PROGRAMS.json.gz').read_bytes()))
    tpl = None
    for p in (vdir / 'hosted' / 'GLOBAL-TEMPLATE.json.gz', sc / 'GLOBAL-TEMPLATE.json.gz'):
        if p.exists(): tpl = json.loads(gzip.decompress(p.read_bytes())); break
    progs = tpl['local_programs'] if (programs_from == 'template' and tpl) else lp
    for o in ('forward', 'backward'): assert progs[o] == lp[o], 'template programs differ from LOCAL-PROGRAMS'
    rec = json.loads((sc / 'CLIFFORD-RECIPES.json').read_text())
    ra = sc / 'RESIDUAL-ADAPTERS.json'
    wraps = json.loads(ra.read_text())['recipes'] if ra.exists() else {}
    # the .gz inputs are pinned by the sha256 of their DECOMPRESSED json (key without '.gz'): the gzip container bytes depend on the zlib of the Python in use
    shas = {(p.name[:-3] if p.name.endswith('.gz') else p.name): hashlib.sha256(gzip.decompress(p.read_bytes()) if p.name.endswith('.gz') else p.read_bytes()).hexdigest()
            for p in sorted(sc.glob('*')) if p.name in ('CANONICAL-WORD.json.gz', 'LOCAL-PROGRAMS.json.gz', 'CLIFFORD-RECIPES.json', 'RESIDUAL-ADAPTERS.json')}
    return dict(c=c, progs=progs, tpl=tpl, rec=rec, wraps=wraps, shas=shas, vdir=str(vdir))


def check_labels(c, events, back):
    """Returns (violations, info).  violations: list of (clause, message)."""
    v, R = c['v'], c['R']; n = 2 * v + R; Fr = Frames(c['frames']); start, final = c['start'], c['final']
    viol = []; bad = lambda cl, msg: viol.append((cl, msg)) if len(viol) < 200 else None
    lam = {('L', r): start[r] for r in range(n)}
    entering = {r for r in range(2 * v, n) if start[r] != 0}
    # G4 start labels
    P = c['ports']
    for i in range(v):
        if Fr.F[start[i]] and rank2(list(Fr.F[start[i]]) + [P[i]]) != 1 or Fr.dim[start[i]] != 1: bad('G4', f'source {i} start not its port line')
        if start[v + i] != 0: bad('G4', f'target {i} does not start at 0')
    phase = -1; live = set(); touched_after_post = set(); pre = {}; post = {}; first_touch = {}
    paid = Counter(); climb_mass = Counter(); centre_steps = defaultdict(list); centre_copy_frame = {}
    gates_at_nonzero = []   # (event index, kind, dst, src, frame)
    nontrivial_wrapper_frames = {}
    def touch(r, idx):
        if r in post: touched_after_post.add(r)
        first_touch.setdefault(r, idx)
    for idx, e in enumerate(events):
        tag = e[0]
        if tag == 'phase':
            k = PHASES.index(e[1]) if e[1] in PHASES else None
            if k is None or k != phase + 1: bad('ORDER', f'phase order at {idx}: {e[1]}')
            phase = k if k is not None else phase
            continue
        ph = PHASES[phase] if phase >= 0 else None
        if tag == 'scalar':
            op, f = e[1], e[2]; t = tuple(op[1]); kind = op[0]
            if kind == 'add':
                s = tuple(op[2])
                for x in (t, s):
                    if x[0] == 'L': touch(x[1], idx)
                lt, ls = lam.get(t), lam.get(s)
                if not (lt == ls == f): bad('G0', f'add at {idx} {t}<-{s} frame {f} but labels {lt},{ls} ({ph})')
                if f != 0 and t[0] == 'L' and s[0] == 'L': gates_at_nonzero.append((idx, ph, t[1], s[1], f))
                if t[0] == 'C' and back and ph == 'centers': live.add(t[1])
            elif kind == 'copy':
                s = tuple(op[2]); touch(s[1], idx)
                if lam.get(s) != f: bad('G3', f'copy at {idx} from {s} at label {lam.get(s)} but frame {f}')
                if t in lam and lam[t] != f: bad('G3', f'copy into {t} declared at {lam[t]} but frame {f}')
                lam[t] = f; live.add(t[1]); centre_copy_frame[t[1]] = f
            elif kind == 'scale':
                if t[0] == 'L': touch(t[1], idx)
                if lam.get(t) != f: bad('G0', f'scale at {idx} {t} label {lam.get(t)} frame {f}')
            elif kind == 'clear':
                if t[0] != 'C': bad('G3', f'clear of a non-private register at {idx}')
                lam[t] = f; live.discard(t[1])
            else: bad('G0', f'unknown scalar {kind}')
        elif tag == 'climb':
            _, part, r, a, b, rk = e; touch(r, idx)
            if part != ph: bad('ORDER', f'climb at {idx} tagged {part} in phase {ph}')
            if live: bad('G3', f'climb at {idx} of {r} while centre copy {sorted(live)} live')
            if lam[('L', r)] != a: bad('G2', f'climb at {idx} of {r} from {a} but label {lam[("L", r)]}')
            if not (Fr.sub(a, b) and Fr.dim[b] > Fr.dim[a]): bad('G2', f'climb at {idx} of {r} {a}->{b} not ascending nested')
            if rk != Fr.dim[b] - Fr.dim[a]: bad('ACC', f'climb at {idx} charged {rk} != {Fr.dim[b] - Fr.dim[a]}')
            lam[('L', r)] = b; paid[rk] += 1; climb_mass[r] += rk
        elif tag == 'center':
            _, k, a, b, rk = e; C = ('C', k)
            if ph != 'centers': bad('ORDER', f'centre step at {idx} outside centre phase')
            if lam.get(C) != a: bad('G3', f'centre step at {idx}: copy {k} at {lam.get(C)} not {a}')
            if not back:
                if not (Fr.sub(b, a) and Fr.dim[a] > Fr.dim[b]): bad('G3', f'centre step at {idx} {a}->{b} not a strict nested descent')
            else:
                if not (Fr.sub(a, b) and Fr.dim[b] > Fr.dim[a]): bad('G3', f'centre step at {idx} {a}->{b} not a strict nested ascent')
            if rk != abs(Fr.dim[a] - Fr.dim[b]): bad('ACC', f'centre step at {idx} charged {rk}')
            if k not in live: bad('G3', f'centre step at {idx} on a dead copy {k}')
            lam[C] = b; paid[rk] += 1; centre_steps[k].append((a, b))
        elif tag == 'adapter':
            _, way, r, f = e; touch(r, idx)
            if way == 'old_to_new' and r in entering: bad('G1', f'entry adapter on entering helper {r} at {idx} (a physical T_E)')
            if way == 'new_to_old' and r in entering and final[r] != 1: bad('G1', f'exit adapter of entering helper {r} not at FULL')
            if way == 'old_to_new':
                if ph != 'entry_adapters' or f != start[r] or lam[('L', r)] != f: bad('G4', f'entry adapter {r} frame {f}')
            elif way == 'new_to_old':
                if ph != 'exit_adapters' or f != final[r] or lam[('L', r)] != f: bad('G4', f'exit adapter {r} frame {f}')
            else: bad('G4', f'unknown adapter {way}')
        elif tag == 'residual_adapter':
            _, side, r, f = e
            if r not in entering: bad('G1', f'wrapper on non-entering register {r}')
            if f != start[r]: bad('G1', f'wrapper {side} of {r} at frame {f} but start {start[r]}')
            if side == 'pre':
                if r in pre or r in first_touch: bad('G1', f'pre wrapper of {r} not the first event touching it')
                if ph != 'entry_adapters': bad('G1', f'pre wrapper of {r} outside entry adapters')
                pre[r] = idx; first_touch.setdefault(r, idx)
            elif side == 'post':
                if r in post: bad('G1', f'second post wrapper on {r}')
                if ph != 'full_frame_cleanup' or lam[('L', r)] != final[r]: bad('G1', f'post wrapper of {r} not after the full-frame cleanup')
                post[r] = idx
            else: bad('G1', f'unknown wrapper side {side}')
        else: bad('ORDER', f'unknown event {tag}')
    if phase != len(PHASES) - 1: bad('ORDER', 'stream does not end with done')
    for r in entering:
        if r not in pre: bad('G1', f'entering helper {r} without pre wrapper')
        if r not in post: bad('G1', f'entering helper {r} without post wrapper')
    if touched_after_post: bad('G1', f'registers touched after their post wrapper: {sorted(touched_after_post)[:5]}')
    for r in range(n):
        if lam[('L', r)] != final[r]: bad('G4', f'register {r} ends at {lam[("L", r)]} not {final[r]}')
        if climb_mass[r] != Fr.dim[final[r]] - Fr.dim[start[r]]: bad('ACC', f'climb mass of {r} does not telescope')
    if live: bad('G3', f'copies live at the end {sorted(live)}')
    cmass = {}
    for k, cf in enumerate(c['center_frames']):
        st = centre_steps.get(k, [])
        cmass[k] = sum(abs(Fr.dim[a] - Fr.dim[b]) for a, b in st)
        bottom = (st[-1][1] if st else cf) if not back else (st[0][0] if st else cf)
        if Fr.dim[bottom] != 0: bad('ACC', f'centre {k} bottom level {bottom} is not 0 (lowering mass {cmass[k]} < dim c_k)')
        if cmass[k] != Fr.dim[cf]: bad('ACC', f'centre {k} lowering mass {cmass[k]} != dim c_k {Fr.dim[cf]}')
    if dict(paid) != {int(r): z for r, z in c['local_profile'].items()}: bad('ACC', f'paid profile {dict(paid)} != word {c["local_profile"]}')
    info = dict(entering=len(entering), entrance_rank=sum(Fr.dim[start[r]] for r in entering), paid_profile=dict(sorted(paid.items())),
                local_mass=sum(k * z for k, z in paid.items()), nonzero_frame_gates=len(gates_at_nonzero),
                centre_paths={k: [s for s in st] for k, st in centre_steps.items()})
    return viol, info, gates_at_nonzero


def scalar_replay(c, events, back):
    """exact rational replay of the stream with frames stripped; returns list of violations ('S', msg)"""
    v, R = c['v'], c['R']; n = 2 * v + R
    st = {('L', r): {r: Q(1)} for r in range(n)}
    for e in events:
        if e[0] != 'scalar': continue
        op = e[1]; t = tuple(op[1]); k = op[0]
        if k == 'clear': st[t] = {}
        elif k == 'copy': st[t] = dict(st.get(tuple(op[2]), {}))
        elif k == 'scale':
            q = Q(op[2], op[3]); st[t] = {j: q * x for j, x in st[t].items()}
        else:
            s = tuple(op[2]); q = Q(op[3], op[4]); row = st.setdefault(t, {})
            for j, x in list(st.get(s, {}).items()):
                z = row.get(j, Q(0)) + q * x
                if z: row[j] = z
                else: row.pop(j, None)
    viol = []
    for r in range(n):
        exp = {r: Q(1)}
        if back and r < v: exp[v + r] = Q(-1)
        if not back and v <= r < 2 * v: exp[r - v] = Q(1)
        if st[('L', r)] != exp: viol.append(('S', f'column mismatch at register {r}'))
        if len(viol) > 20: break
    for t, row in st.items():
        if t[0] == 'C' and row: viol.append(('S', f'private copy {t} not cleared'))
    return viol


def classify(c, gates):
    """lemma instances among the nonzero-frame gates: gauge compensations (target <- entering helper) and kernel updates (helper <- helper)"""
    v = c['v']; start = c['start']
    comp = [g for g in gates if g[1] == 'A' and v <= g[2] < 2 * v and start[g[3]] != 0 and g[4] == start[g[3]]]
    kern = [g for g in gates if g[1] == 'A' and g[2] >= 2 * v and g[3] >= 2 * v and start[g[3]] != 0 and g[4] == start[g[3]]]
    return comp, kern
