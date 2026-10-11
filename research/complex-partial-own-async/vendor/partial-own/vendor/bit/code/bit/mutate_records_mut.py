"""Record-level negative controls aimed at the mutable-source interface, for the official PR #266 cohort checkers as
generalised by PR #370 (legality_h NCOPY = 9) and PR #381 (columns_k, here KPAIRS = 5: eleven stages).
usage: mutate_records_mut.py WORD.json.gz RECORDDIR COHORT_IN COHORT_OUT LEGALITY_BIN COLUMNS_H_BIN COLUMNS_K_BIN
Each mutant is a changed COHORT249-RECORDS.bin; the unchanged legality must still pass where stated (the mutant is a
semantic one) and both column checkers must reject it:
  - drop one cleanup ADD into a source register (phase 5, destination < v);
  - corrupt a source packet: duplicate (cancel) the last phase-2 ADD into a source register that targets read in phase B,
    and duplicate the matching cleanup ADD, so every source is still restored but the delivered packet is wrong;
  - leave a source unrestored: delete every cleanup ADD into that source register.
Prepared by eumemic with substantial Anthropic Claude assistance; Apache-2.0."""
import gzip
import json
import shutil
import struct
import subprocess
import sys

wp, rd, cin, cout, leg, colh, colk = sys.argv[1:8]
w = json.load(gzip.open(wp, "rt"))
v = w["v"]
rec = open(rd + "/249-records.bin", "rb").read()
n = len(rec) // 24
R = [list(struct.unpack_from("<6i", rec, 24 * i)) for i in range(n)]
pack = lambda rows: b"".join(struct.pack("<6i", *r) for r in rows)
adds = {ph: [i for i, e in enumerate(R) if e[0] == 1 and e[5] == ph] for ph in (2, 5)}

XA = sorted({s for g in w["B"] for s in g[2] if s < v})[0]
ia = max(i for i, g in enumerate(w["A"]) if g[1] == XA)
assert len(w["A"][ia][2]) == 1
ka = sum(len(g[2]) for g in w["A"][:ia])                       # ordinal of that gate's ADD among phase-2 ADDs
zg = [("A", i) for i, g in enumerate(w["A"]) if not (v <= g[1] < 2 * v)] + \
     [("B", i) for i, g in enumerate(w["B"]) if not (v <= g[1] < 2 * v)]
pc = len(zg) - 1 - zg.index(("A", ia))                         # C gate that is its literal inverse
kc = sum(len(g[2]) for g in w["C"][:pc])
ra, rc = adds[2][ka], adds[5][kc]
assert R[ra][1:3] == [XA, w["A"][ia][2][0]] and R[rc][1:3] == [XA, w["A"][ia][2][0]]


def run(binary, recs, legality=False):
    tmp = cout + "-mutmut"
    shutil.rmtree(tmp, ignore_errors=True)
    shutil.copytree(cout, tmp)
    open(tmp + "/COHORT249-RECORDS.bin", "wb").write(recs)
    if legality:
        r = subprocess.run([binary, cin, tmp, tmp + "/x.json"], capture_output=True, text=True)
    else:
        r = subprocess.run([binary, tmp + "/COHORT249-RECORDS.bin", tmp + "/x.json"], capture_output=True, text=True)
    shutil.rmtree(tmp, ignore_errors=True)
    return r.returncode != 0, ((r.stderr.strip().splitlines() or ["?"])[-1])[:80]


first_c = next(i for i in adds[5] if R[i][1] < v)
m1 = pack(R[:first_c] + R[first_c + 1:])
m2 = pack(R[:ra + 1] + [R[ra]] + R[ra + 1:rc] + [R[rc]] + R[rc:])
m3 = pack([e for i, e in enumerate(R) if not (e[0] == 1 and e[5] == 5 and e[1] == XA)])
ok = True
for name, m in [("drop one cleanup ADD into a source register", m1),
                ("corrupt a source packet read in phase B (cleanup adjusted: every source still restored)", m2),
                ("leave source register %d unrestored (all its cleanup ADDs deleted)" % XA, m3)]:
    lrej, lmsg = run(leg, m, legality=True)
    hrej, hmsg = run(colh, m)
    krej, kmsg = run(colk, m)
    ok &= hrej and krej and not lrej
    print("   legality %s; five-stage columns %s [%s]; eleven-stage columns %s [%s]  <- %s" %
          ("passes (frames unchanged)" if not lrej else "REJECTS", "REJECTED" if hrej else "ACCEPTED!!", hmsg,
           "REJECTED" if krej else "ACCEPTED!!", kmsg, name))
assert ok, "a record-level mutable-source mutant was accepted"
print("PASS all 3 record-level mutable-source mutants rejected by both column checkers (legality unchanged)")
