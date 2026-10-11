"""Mutation controls of the one-owner rule on EVERY register class, run through the generating scripts (hosted_gk.py, integrate_gk.py).  Apache-2.0.
Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.
usage: controls_hosting.py VARIANT_WORKDIR SELECTION.json KEY OUT.json      (cwd = VARIANT_WORKDIR, as the inherited scripts expect)
Register classes of one invocation: active data wires, hosted helpers (data families), banked helpers (bank families), the private namespace
(centres, reserved tableau, coefficient), copies (replicas).  The rule: an entering helper is the only owner of its physical family in the invocation;
a family of the data class has one owner; nothing is owned in the private namespace.
(a) the generator's rule function `hosted_gk.one_helper_rule` is run on mutated owner arrays of a real invocation, one mutation per class;
(b) the whole hosting generator is run with a bank tiling that puts eight entering helpers of ONE invocation on one bank family, each with a disjoint
    9-cell footprint (8 residual cells and a spectator in the pad): hosted_gk.py must refuse it, while the unmutated tiling must be accepted;
(c) the parent-template generator integrate_gk.py is run on the same mutated tiling and must refuse it.
(The independent audit has its own controls for the same layout in audit_hosted_gk.py, and replay_gk.py for the parent template.)"""
import copy, gzip, json, os, runpy, shutil, sys, tempfile
from collections import Counter
from pathlib import Path
CODE = Path(__file__).resolve().parent; sys.path.insert(0, str(CODE))
import gk_common as GC
import hosted_gk as HG
work = Path(sys.argv[1]).resolve(); selp = Path(sys.argv[2]).resolve(); key = sys.argv[3]; outp = Path(sys.argv[4]).resolve()
os.chdir(work)
V, L, M, DATA = GC.V, GC.L, GC.M, GC.DATA
can = json.load(gzip.open('split-centres/CANONICAL-WORD.json.gz')); R = can['R']
widths = [L - len(can['frames'][can['start'][2 * V + i]]) for i in range(R)]
hosted = json.loads(gzip.decompress((work / 'hosted/GLOBAL-TEMPLATE.json.gz').read_bytes())); W = hosted['live']
call = next(c for c in hosted['calls'] if any(o[1][0] == 2 and len(o[1]) == 4 for o in c['owners'][2 * V:]))      # an invocation with banked entering helpers
good = call['owners']; HG.one_helper_rule(good, widths, W)
out = []
def refused(name, fn, must):
    o = copy.deepcopy(good); fn(o)
    try: HG.one_helper_rule(o, widths, W)
    except AssertionError as e:
        assert must in str(e), (name, str(e)); out.append(dict(control=name, rejected_by='hosted_gk.one_helper_rule', message=str(e)[:100]))
    else: raise AssertionError('accepted by the generator rule: ' + name)
ent = [i for i in range(2 * V, 2 * V + R) if good[i][1][0] == 2 and len(good[i][1]) == 4]; a, b = ent[0], ent[1]
host_ = [i for i in range(2 * V, 2 * V + R) if good[i][1][0] in (3, 4)]
def join(o):       # bank class: b joins a's bank family at the next free cells with a spectator of its own
    fa = o[a][0]; free = 64; o[b] = [fa, [2, free, widths[b - 2 * V], [free + widths[b - 2 * V]]]]
refused('bank class: two entering helpers on one bank family', join, 'shares its bank family')
refused('bank class: spectator is a residual cell of its own helper', lambda o: o[a][1].__setitem__(3, [o[a][1][1]]), 'footprints overlap')
refused('bank class: an active data wire on a bank family', lambda o: o.__setitem__(3, [DATA, [1, 0, 3]]), 'bank family owned by a non-helper')
refused('data class: two hosted helpers on one data family', lambda o: o.__setitem__(host_[1], [o[host_[0]][0], o[host_[1]][1]]), 'two owners on one data family')
refused('data class: a hosted helper on an active data family', lambda o: o.__setitem__(host_[0], [o[0][0], o[host_[0]][1]]), 'two owners on one data family')
refused('private namespace: a bank owner in the centres', lambda o: o.__setitem__(a, [W + 3, o[a][1]]), 'private namespace')
refused('private namespace: a bank owner in the reserved tableau', lambda o: o.__setitem__(a, [W + len(can['centers']) + 5, o[a][1]]), 'private namespace')
refused('private namespace: a bank owner at the coefficient registers', lambda o: o.__setitem__(a, [hosted['physical'] - 1, o[a][1]]), 'private namespace')
# ---- (b), (c): a tiling with eight entering helpers of one invocation per bank family
def packed_tile(items):
    """the layout of 'nine-cell bank slots': entering helpers in replica order, as many per bank family as fit with a disjoint spectator cell each
    (eight residuals of width 8 and eight spectators in the pad of 9), whatever their replica"""
    wide = [x for x in items if x[2] == L]; ent_ = [x for x in items if x[2] < L]
    assign, nb, pads = saved(wide) if wide else ({}, 0, Counter())
    if not ent_: return assign, nb, pads
    pads = Counter(pads); banks = []
    for x in ent_:      # every footprint is nine cells (w residual + 9 - w spectators), so a bank takes M // 9 = 8 of them
        if not banks or len(banks[-1]) == M // L: banks.append([])
        banks[-1].append(x)
    for bk, mem in enumerate(banks):
        cells = sum(y[2] for y in mem); off = 0; spec = cells
        for rep, h, w in mem:
            assign[(rep, h)] = (nb + bk, off, w, False, tuple(range(spec, spec + L - w))); off += w; spec += L - w
        assert spec <= M
        for part in GC.split_pad(M - cells): pads[part] += 1
    return assign, nb + len(banks), pads
saved = GC.tile
tmpd = Path(tempfile.mkdtemp(prefix='gkhost-', dir=work))
try:
    HG.ONEPER = True; HG.SELECTION = str(selp); HG.KEY = key; HG.DISCOVER = False; HG.DISCOVER_TO = None
    HG.tile = saved; HG.main(Path('split-centres'), tmpd / 'ok')                                  # the real tiling is accepted
    HG.tile = packed_tile
    try: HG.main(Path('split-centres'), tmpd / 'packed')
    except AssertionError as e:
        assert 'shares its bank family' in str(e), str(e); out.append(dict(control='hosting generator: eight entering helpers of one invocation on one bank family', rejected_by='hosted_gk.py', message=str(e)[:100]))
    else: raise AssertionError('hosted_gk.py accepted the packed bank tiling')
finally: HG.tile = saved
# parent template generator, in a throw-away copy of the variant directory
t2 = tmpd / 'parent'; t2.mkdir(); os.symlink(work / 'work', t2 / 'work'); shutil.copytree(work / 'split-centres', t2 / 'split-centres'); shutil.copy(work / 'BIT-PRICE.json', t2 / 'BIT-PRICE.json')
GC.tile = packed_tile; os.chdir(t2)
try:
    try: runpy.run_path(str(CODE / 'integrate_gk.py'), run_name='__main__')
    except AssertionError as e:
        assert 'shares its bank family' in str(e), str(e); out.append(dict(control='parent template generator: eight entering helpers of one invocation on one bank family', rejected_by='integrate_gk.py', message=str(e)[:100]))
    else: raise AssertionError('integrate_gk.py accepted the packed bank tiling')
finally: GC.tile = saved; os.chdir(work)
shutil.rmtree(tmpd, ignore_errors=True)
outp.write_text(json.dumps(dict(status='PASS_ONE_OWNER_RULE_CONTROLS_ON_EVERY_REGISTER_CLASS', controls=out), indent=1) + '\n'); print(len(out), 'generator controls rejected')
