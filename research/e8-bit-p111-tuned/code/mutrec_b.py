"""Record-level negative controls aimed at the phase-B source writes, for the official cohort checkers (PR #266's
legality and formal-column checkers as generalised by PR #370 and PR #381).
usage: mutrec_b.py WORD.json.gz RECORDDIR COHORT_IN COHORT_OUT LEGALITY_BIN COLUMNS_BIN [COLUMNS_BIN ...]
Each mutant is a changed COHORT249-RECORDS.bin.  Legality must still pass (no frame changes) and every column checker
must reject it:
  1 drop one cleanup ADD (phase 5) into a source register;
  2 corrupt a phase-B source write: duplicate (cancel) the first phase-4 ADD into a source register and duplicate the
    matching cleanup ADD, so every source is still restored but the Q-delivery the targets read is wrong;
  3 leave a source unrestored: delete every cleanup ADD into the destination of that phase-B source write.
Adapted from PR #493's mutate_records_mut.py (whose sites are phase-A source writes; this word has none).
Prepared by eumemic with substantial Anthropic Claude assistance; Apache-2.0."""
import gzip
import json
import shutil
import struct
import subprocess
import sys

wp, rd, cin, cout, leg = sys.argv[1:6]
cols = sys.argv[6:]
w = json.load(gzip.open(wp, "rt"))
v = w["v"]
rec = open(rd + "/249-records.bin", "rb").read()
R = [list(struct.unpack_from("<6i", rec, 24 * i)) for i in range(len(rec) // 24)]
pack = lambda rows: b"".join(struct.pack("<6i", *r) for r in rows)
adds = {ph: [i for i, e in enumerate(R) if e[0] == 1 and e[5] == ph] for ph in (4, 5)}
is_z = lambda r: not (v <= r < 2 * v)
ib = next(i for i, g in enumerate(w["B"]) if g[1] < v and len(g[2]) == 1)
XB, src = w["B"][ib][1], w["B"][ib][2][0]
kb = sum(len(g[2]) for g in w["B"][:ib])
zg = [("A", i) for i, g in enumerate(w["A"]) if is_z(g[1])] + [("B", i) for i, g in enumerate(w["B"]) if is_z(g[1])]
pc = len(zg) - 1 - zg.index(("B", ib))
kc = sum(len(g[2]) for g in w["C"][:pc])
rb, rc = adds[4][kb], adds[5][kc]
assert R[rb][1:3] == [XB, src] and R[rc][1:3] == [XB, src]


def run(binary, recs, legality=False):
    tmp = cout + "-mutb"
    shutil.rmtree(tmp, ignore_errors=True)
    shutil.copytree(cout, tmp)
    open(tmp + "/COHORT249-RECORDS.bin", "wb").write(recs)
    args = [binary, cin, tmp, tmp + "/x.json"] if legality else [binary, tmp + "/COHORT249-RECORDS.bin", tmp + "/x.json"]
    r = subprocess.run(args, capture_output=True, text=True)
    shutil.rmtree(tmp, ignore_errors=True)
    return r.returncode != 0, ((r.stderr.strip().splitlines() or ["?"])[-1])[:70]


first_c = next(i for i in adds[5] if R[i][1] < v)
muts = [("drop one cleanup ADD into a source register", pack(R[:first_c] + R[first_c + 1:])),
        ("corrupt a phase-B source write (cancelled, cleanup adjusted: every source still restored)",
         pack(R[:rb + 1] + [R[rb]] + R[rb + 1:rc] + [R[rc]] + R[rc:])),
        ("leave source register %d unrestored (all its cleanup ADDs deleted)" % XB,
         pack([e for e in R if not (e[0] == 1 and e[5] == 5 and e[1] == XB)]))]
ok = True
for name, m in muts:
    lrej, lmsg = run(leg, m, legality=True)
    res = [run(cb, m) for cb in cols]
    ok &= (not lrej) and all(x[0] for x in res)
    print("   legality %s; %s  <- %s" % ("passes (frames unchanged)" if not lrej else "REJECTS",
                                        "; ".join("%s %s [%s]" % (cb.rsplit('/', 1)[-1], "REJECTED" if r_[0] else "ACCEPTED!!",
                                                                   r_[1]) for cb, r_ in zip(cols, res)), name))
assert ok, "a record-level phase-B source mutant was accepted"
print("PASS all 3 record-level phase-B source mutants rejected by every column checker (legality unchanged)")
