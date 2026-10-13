#!/usr/bin/env python3
"""build_tri.py BASE_WORD RECIPE OUT_WORD [--control NAME]

Standard library only. Applies a NewBArch triangle-hybrid recipe to the X4 word (1e1d99ba) and writes a FULL-WORD.json.gz.
Recipe keys (all indices refer to the BASE word):
  base_sha256      sha256 of the decompressed base JSON (checked)
  B_delete         list of B indices removed
  B_insert         list of [pos, gate]: gate (with frame) inserted before base B gate pos (list order kept)
  B_frames         {index: frame}: explicit re-chosen frame of a kept base B gate
  tail_insert      list of [early_index, gate]: gates appended to cleanup in list order, then registered as early cleanup at early_index (ascending)
  cleanup_prepend  list of gates prepended to the full cleanup (early indices are shifted)
  local_profile    report.local_profile of the result
  expect_sha256    sha256 of the decompressed result (checked unless a control is requested)
Controls (each must be REJECTED by audit_local; see controls.json):
  drop_restore     omit cleanup_prepend (end value of the holder not restored)
  restore_full     move tail_insert gates into the full cleanup (FULL frame) instead of early cleanup
  drop_preread     omit the inserted entrance pre-reads (inserted target += E gates at pos < first donation)
  donation_after   insert each donation after its reading target's read instead of before it
  NAME@X           the same control restricted to the instance whose packet register is X (recipe 'variants')
"""
import sys, json, gzip, hashlib, copy

FULL = [256, 128, 64, 32, 16, 8, 4, 2, 1]

def load(p):
    raw = gzip.decompress(open(p, 'rb').read()); return json.loads(raw), hashlib.sha256(raw).hexdigest()

def apply(w, rc, control=None):
    w = copy.deepcopy(w); B = w['B']
    S = None
    if control and '@' in control:                     # per-instance control: name@X mutates only instance X's gates
        control, x = control.split('@'); x = int(x)
        vv = [s for s in rc['variants'] if s['X'] == x][0]; S = {vv['X'], vv['E'], *vv['hold']}
    sel = lambda g: S is None or bool({g[1], g[2]} & S)
    dele = set(rc['B_delete']); fr = {int(k): f for k, f in rc['B_frames'].items()}
    ins = [list(x) for x in rc['B_insert']]
    don = [x for x in ins if not (112 <= x[1][1] < 224)]           # donations: destination is not a target
    first_don = min(p for p, _ in don) if don else 0
    if control == 'drop_preread':
        ins = [x for x in ins if not (x[0] < first_don and 112 <= x[1][1] < 224 and sel(x[1]))]
    if control == 'donation_after':
        new = []
        for p, g in ins:
            if g in [d[1] for d in don] and sel(g):
                rd = [i for i, e in enumerate(B) if i >= p and e[0] == 'add' and e[2] == g[1] and 112 <= e[1] < 224]
                p = rd[0] + 1
            new.append([p, g])
        ins = new
    at = {}
    for p, g in ins: at.setdefault(p, []).append(list(g))
    out = []
    for i, e in enumerate(B):
        out.extend(at.get(i, []))
        if i in dele: continue
        e = list(e)
        if i in fr: e = e[:-1] + [list(fr[i])]
        out.append(e)
    out.extend(at.get(len(B), []))
    w['B'] = out
    pre = [list(g) for g in rc['cleanup_prepend'] if not (control == 'drop_restore' and sel(g))]
    tails = [list(x) for x in rc['tail_insert']]
    if control == 'restore_full':
        pre = pre + [g[1][:-1] + [FULL] for g in tails if sel(g[1])]; tails = [g for g in tails if not sel(g[1])]
    C = pre + w['cleanup']; sh = len(pre)
    early = [[i + sh, U] for i, U in w['early_cleanup']]
    idx = []
    for j, g in tails: C.append(list(g)); idx.append((j, len(C) - 1, list(g[-1])))   # appended in recipe order
    for j, ci, U in sorted(idx): early.insert(j, [ci, U])                               # then registered at their early index
    w['cleanup'] = C; w['early_cleanup'] = early
    w['report'] = dict(w['report']); w['report']['local_profile'] = rc['local_profile']
    return w

def main():
    a = sys.argv[1:]; control = None
    if '--control' in a: k = a.index('--control'); control = a[k + 1]; del a[k:k + 2]
    base, out = a[0], a[2]
    w, sha = load(base); rc = json.load(open(a[1]))
    if sha != rc['base_sha256']: raise SystemExit('base sha mismatch ' + sha)
    w2 = apply(w, rc, control)
    raw = json.dumps(w2, separators=(',', ':')).encode()
    open(out, 'wb').write(gzip.compress(raw, mtime=0))
    s = hashlib.sha256(raw).hexdigest()
    if control is None and s != rc['expect_sha256']: raise SystemExit('result sha mismatch ' + s)
    print(json.dumps(dict(control=control, sha256=s)))

if __name__ == '__main__':
    main()
