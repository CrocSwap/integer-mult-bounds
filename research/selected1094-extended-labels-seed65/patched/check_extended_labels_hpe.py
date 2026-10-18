# Apache-2.0.  Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.
# PATCHED COPY (seed65) of research/e8-lemma-g-lean/code/check_extended_labels.py at base 0b1cccf8:
#   original git blob bc1d9c32180a115e13c1a4d0ea670ecc7f51c819,
#   original sha256   9e072754d350e79e5657196bee30cd18ed0a0677628aa66d16a15ce2aab1d2ea.
# Patched by Sagar Thakrar with Anthropic Claude assistance (Apache-2.0).  Apart from this header, only the three lines
# marked PATCH(seed65) differ from the original: cold hyperplane-ended helpers (start frame 0, terminal frame U != FULL)
# are wrapped like entering helpers, and an HPE wrapper event carries a 5th field U that must equal the helper's terminal
# frame.  Everything else is verbatim, including the 50-entry violation cap and the lg_lib import used only by main().
# research/selected1094-extended-labels-seed65/verify.py rebuilds this file from the pinned original and compares bytes.
"""Instance check E (PROOF.md §3, hypothesis H1 for the conversion events).

The Lean theorem `LemmaG.Stream.conj_matrix` is applied to the COMPLETE emitted stream, with data adapters and residual
wrappers read as relabel events of an extended label set  (tag, frame):
  tag 'T'           the word's family T_F (canonical_frame); identity adapters keep it;
  ('pre', r)        a source before its (non-identity) entry adapter;          ('prew', r)  an entering helper before R_E^-1;
  ('post', r)       a target after its (non-identity) exit adapter;            ('done', r)  an entering helper after L_E^-1.
A register-specific tag is carried only by its register (and by a private copy taken from it), so G0 in the extended labels
says exactly: no add/copy meets a source before its entry adapter, a target after its exit adapter, or an entering helper
outside its wrappers, and every climb / centre step happens in the word's family.  The conversions themselves are pinned
as in lg_phys.run: each source has exactly one entry adapter (the non-identity monomial M_i, tag ('pre',i) -> 'T'), each
target exactly one exit adapter after its tag-'T' life (N_t^-1, 'T' -> ('post',t)); every other adapter has no serialized
operator, i.e. is the identity, and must sit at frame 0 (entry) or FULL (exit); each entering helper has exactly one pre and
one post wrapper keyed by its start frame (R_E^-1, L_E^-1).  The frame component (G0, G2, G3) is checked by #484's lg_lib.check_labels; this script
re-tracks the frames and adds the tags.

usage: check_extended_labels.py BASE VARIANT [VARIANT ...] [--mutants]     (BASE = the output directory of #484's verify.py)
Imports #484's lg_lib (read-only) for loading the emitted artefacts; exits non-zero on any violation."""
import json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / 'e8-complex-gauge-kernel' / 'code' / 'lemmaG'))
from lg_lib import load  # noqa: E402

FULL = 1                     # frame-table row of the full frame (as in lg_phys.run)


def check(c, events):
    v, R = c['v'], c['R']; n = 2 * v + R; start, final = c['start'], c['final']
    entering = {r for r in range(2 * v, n) if start[r] != 0 or final[r] != FULL}   # PATCH(seed65): + cold-HPE helpers (wrapped)
    assert len(c['frames'][FULL]) == 9 and not c['frames'][0], 'frame-table rows 0 and 1 are not the zero frame and FULL'
    tag = {}
    for r in range(n):
        tag[('L', r)] = ('pre', r) if r < v else ('prew', r) if r in entering else 'T'
    lam = {('L', r): start[r] for r in range(n)}
    viol = []; counts = dict(adds=0, copies=0, climbs=0, centre_steps=0, entry_adapters=0, exit_adapters=0, pre_wrappers=0, post_wrappers=0)
    bad = lambda m: viol.append(m) if len(viol) < 50 else None
    for idx, e in enumerate(events):
        k = e[0]
        if k == 'phase':
            continue
        if k == 'scalar':
            op, f = e[1], e[2]; t = tuple(op[1])
            if op[0] == 'add':
                s = tuple(op[2]); counts['adds'] += 1
                if (tag.get(t), lam.get(t)) != (tag.get(s), lam.get(s)): bad(f'add {idx}: {t} {(tag.get(t), lam.get(t))} vs {s} {(tag.get(s), lam.get(s))}')
            elif op[0] == 'copy':
                s = tuple(op[2]); counts['copies'] += 1
                if lam.get(s) != f: bad(f'copy {idx}: source {s} at {lam.get(s)} not {f}')
                tag[t], lam[t] = tag.get(s), f
            elif op[0] == 'clear':
                tag[t], lam[t] = 'T', f
            elif op[0] != 'scale':                       # scale: no label condition
                bad(f'unknown scalar {op[0]} at {idx}')
        elif k == 'climb':
            _, _, r, a, b, _ = e; x = ('L', r); counts['climbs'] += 1
            if tag[x] != 'T' or lam[x] != a: bad(f'climb {idx}: {r} at {(tag[x], lam[x])} not (T,{a})')
            lam[x] = b
        elif k == 'center':
            _, kk, a, b, _ = e; x = ('C', kk); counts['centre_steps'] += 1
            if tag.get(x) != 'T' or lam.get(x) != a: bad(f'centre step {idx}: copy {kk} at {(tag.get(x), lam.get(x))} not (T,{a})')
            lam[x] = b
        elif k == 'adapter':
            _, way, r, f = e; x = ('L', r)
            if lam[x] != f: bad(f'adapter {idx}: {r} at frame {lam[x]} not {f}')
            if way == 'old_to_new':
                counts['entry_adapters'] += 1
                want = ('pre', r) if r < v else 'T'          # a source converts exactly once; other entry adapters are identities
                if tag[x] != want: bad(f'entry adapter {idx}: {r} tag {tag[x]} not {want}')
                if r >= v and f != 0: bad(f'identity entry adapter {idx}: {r} at frame {f} not 0')
                tag[x] = 'T'
            elif way == 'new_to_old':
                counts['exit_adapters'] += 1
                if tag[x] != 'T': bad(f'exit adapter {idx}: {r} tag {tag[x]}')
                if not (v <= r < 2 * v) and f != FULL: bad(f'identity exit adapter {idx}: {r} at frame {f} not FULL')
                tag[x] = ('post', r) if v <= r < 2 * v else 'T'
            else:
                bad(f'unknown adapter {way} at {idx}')
        elif k == 'residual_adapter':
            _, side, r, f, *U = e; x = ('L', r)   # PATCH(seed65): an HPE wrapper carries a 5th field U
            if U != ([final[r]] if final[r] != FULL else []): bad(f'wrapper {idx}: {r} names terminal frame {U} not its final {final[r]}')   # PATCH(seed65)
            if f != start[r]: bad(f'wrapper {idx}: {r} keyed by frame {f} not its start {start[r]}')
            if lam[x] != f and side == 'pre': bad(f'pre wrapper {idx}: {r} at {lam[x]} not {f}')
            if side == 'pre':
                counts['pre_wrappers'] += 1
                if tag[x] != ('prew', r): bad(f'pre wrapper {idx}: {r} tag {tag[x]}')
                tag[x] = 'T'
            else:
                counts['post_wrappers'] += 1
                if tag[x] != 'T': bad(f'post wrapper {idx}: {r} tag {tag[x]}')
                tag[x] = ('done', r)
        else:
            bad(f'unknown event {k} at {idx}')
    for r in range(n):
        want = ('post', r) if v <= r < 2 * v else ('done', r) if r in entering else 'T'
        if tag[('L', r)] != want: bad(f'register {r} ends with tag {tag[("L", r)]} not {want}')
        if lam[('L', r)] != final[r]: bad(f'register {r} ends at frame {lam[("L", r)]} not {final[r]}')
    return viol, counts


def mutants(c, ev):
    """Necessity controls: each edit must be rejected (adapter edits on every word, wrapper edits on the wrapper words)."""
    v = c['v']; ev = list(ev); res = {}
    i = next(i for i, e in enumerate(ev) if e[0] == 'adapter' and e[1] == 'old_to_new' and e[2] < v)
    res['drop a source entry adapter'] = len(check(c, ev[:i] + ev[i + 1:])[0])
    res['duplicate a source entry adapter'] = len(check(c, ev[:i + 1] + [ev[i]] + ev[i + 1:])[0])
    j = next(i for i, e in enumerate(ev) if e[0] == 'adapter' and e[1] == 'new_to_old' and v <= e[2] < 2 * v); t = ('L', ev[j][2])
    k = max(i for i, e in enumerate(ev[:j]) if e[0] == 'scalar' and e[1][0] == 'add' and t in (tuple(e[1][1]), tuple(e[1][2])))
    res['target exit adapter before its last add'] = len(check(c, ev[:k] + [ev[j]] + ev[k:j] + ev[j + 1:])[0])
    if any(e[0] == 'residual_adapter' for e in ev):
        w = next(i for i, e in enumerate(ev) if e[0] == 'residual_adapter' and e[1] == 'pre')
        res['drop a pre wrapper'] = len(check(c, ev[:w] + ev[w + 1:])[0])
        w = next(i for i, e in enumerate(ev) if e[0] == 'residual_adapter' and e[1] == 'post'); r = ('L', ev[w][2])
        k = max(i for i, e in enumerate(ev[:w]) if e[0] == 'scalar' and e[1][0] == 'add' and r in (tuple(e[1][1]), tuple(e[1][2])))
        res['post wrapper before the helper\'s last add'] = len(check(c, ev[:k] + [ev[w]] + ev[k:w] + ev[w + 1:])[0])
    return res


def main():
    base, names = Path(sys.argv[1]), [a for a in sys.argv[2:] if not a.startswith('--')]
    out, ok = {}, True
    for name in names:
        d = load(base / name); c = d['c']; out[name] = {'inputs': d['shas']}
        for o in ('forward', 'backward'):
            viol, counts = check(c, d['progs'][o])
            out[name][o] = dict(violations=len(viol), first=viol[:5], **counts)
            ok &= not viol
            print(name, o, 'violations', len(viol), counts, flush=True)
            if '--mutants' in sys.argv:
                m = mutants(c, d['progs'][o]); out[name][o]['mutants_rejected'] = m
                ok &= all(x > 0 for x in m.values()); print(' ', 'mutants (violations each):', m, flush=True)
    print(json.dumps(out, indent=1, sort_keys=True))
    print('PASS extended labels' if ok else 'FAIL extended labels')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
