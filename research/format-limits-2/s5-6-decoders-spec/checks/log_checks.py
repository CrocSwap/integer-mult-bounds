"""CHECKED (log): facts read off the shipped flip-walk logs in evidence/ (sha256-pinned in SOURCES.part.json).  Not re-runs.
D2: absorbing a frame line into an exact n=8 P112 decoder costs +1 (single) / +2 (pair) in every sampled state.
D1/D3: walk logs on P112 (no n>8 state at cost<=64 in ~1.5e8 iterations), P113 (best 65), P111 punctures (n up to 11 at cost<=64) and P104."""
import glob, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fails = 0
def ok(tag, cond, info=""):
    global fails
    print(("PASS " if cond else "FAIL ") + tag + (" | " + info if info else ""), flush=True)
    fails += (not cond)
rd = lambda p: open(os.path.join(ROOT, p)).read()
st = sg = pr = 0
for i in (1, 2, 3):
    t = rd("evidence/D2/cen%d.out" % i)
    s, bad, nint = map(int, re.search(r"states (\d+) bad (\d+) integer-ext frac \{True: (\d+)\}", t).groups())
    single = re.search(r"single \(dcst,integer\): \[\(\(1, True\), (\d+)\)\]", t); pair = re.search(r"pair dcst: \[\(2, (\d+)\)\]", t)
    ok("D2.log.cen%d-all-singles-+1-all-pairs-+2" % i, bad == 0 and single and pair and "min single 1" in t, "%d states" % s)
    st += s; sg += int(single.group(1)); pr += int(pair.group(1))
ok("D2.log.totals-33981-states-271848-singles-951468-pairs", (st, sg, pr) == (33981, 271848, 951468), "%d / %d / %d" % (st, sg, pr))
def done(p):
    return [dict(zip(("it", "uniq", "best", "ngt8", "maxn"), map(int, re.search(r"it=(\d+) uniq<=64:(\d+) bestever=(\d+) .*n>8@<=64:(\d+) maxn=(\d+)", l).groups()))) for l in rd(p).split("\n") if "DONE" in l]
for i in (1, 2, 3):
    d = done("evidence/D2/d%d.out" % i)[0]
    ok("D1.log.P112-walk-d%d-no-state-below-64-none-with-n>8" % i, d["best"] == 64 and d["ngt8"] == 0 and d["maxn"] == 8 and d["it"] > 4e7, "%.1e iterations" % d["it"])
for i in (1, 2):
    d = done("evidence/D2/w%d.out" % i)[0]
    ok("D2.log.P113-walk-w%d-best-65" % i, d["best"] == 65 and d["uniq"] == 0 and d["it"] > 2e8)
for g in ("g0", "g1", "g30", "g48", "g70", "g111", "c2_0", "c2_111"):
    d = done("evidence/D3/%s.out" % g)[0]
    ok("D3.log.P111-walk-%s-best-63" % g, d["best"] == 63 and d["uniq"] > 0, "%d distinct states at <=64, n>8 states %d, max n %d" % (d["uniq"], d["ngt8"], d["maxn"]))
for g in ("c1_0", "c1_111"):
    d = done("evidence/D3/%s.out" % g)[0]
    ok("D3.log.P111-cap1-%s-best-64" % g, d["best"] == 64)
for s in "abc":
    t = rd("evidence/D3/B14_flip_3%s.out" % s)
    ok("D3.log.P104-walker-%s-hit-56" % s, "NEW MIN cost=56" in t or "c56" in t)
ok("D1.log.no-SAT-result-exists", open(os.path.join(ROOT, "evidence/D1/B14_satlift.log")).read() == "" and rd("evidence/D1/B14_satlift.exit").strip() == "143"
   and rd("evidence/D1/B72_sat_n9_o3.log").startswith("vars 23904 clauses 1540851") and rd("evidence/D1/B72_sat_n9_o3.exit").strip() == "143",
   "both solver runs were killed (exit 143) without a result; there is no UNSAT proof or DRAT file")
raise SystemExit(1 if fails else 0)
