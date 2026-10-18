"""baseline: audit a word, compare the surrogate frame optimum with its published local profile (centre descents excluded) and
print the true-moment interval at b (frames.moment_interval).
usage: python -B baseline.py WORD.json.gz [ENDPOINT_B]"""
import sys, time, json, gzip, hashlib
import harness as C
from writeback import audit
if __name__ == "__main__":
    p = sys.argv[1]; w = C.load(p)
    t0 = time.time(); ok, rep, sha = audit(w); print("audit_local", ok, sha[:12] if sha else None, f"{time.time()-t0:.0f}s", flush=True)
    t0 = time.time(); P = C.Pricer(p, b=sys.argv[2] if len(sys.argv) > 2 else None, interval=True)
    pub = {int(k): v for k, v in w['report']['local_profile'].items()}
    print("pricer base profile", P.base_profile, f"{time.time()-t0:.0f}s"); print("published profile  ", dict(sorted(pub.items())))
    print("match (centre descents excluded)" if P.base_profile == {r: n for r, n in pub.items() if r != 8} else "DIFFERENT: the surrogate optimum differs from the published frames",
          "| base_cost", P.base_cost, "| surrogate certified", P.base_certified)
    iv = P.base_interval
    print(f"true-moment interval at b: width {iv['width_units']:.3g} units | fine profile {iv['fine_profile']} | surrogate not minimal: {iv['surrogate_not_minimal']}")
