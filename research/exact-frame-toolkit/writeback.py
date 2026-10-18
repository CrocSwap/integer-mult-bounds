"""writeback: write a solved frame assignment back into a gauge44-lineage word (A/B gate frames, early-cleanup
tails), recompute report.local_profile / width_inventory / local_rank_mass with the lineage's recount, and run the
lineage's independent audit (research/gauge44-frames-x/independent/audit_local.py) on the result."""
import gzip, json, collections, copy, hashlib, subprocess, sys, tempfile, os
import frames as F
from word import recount
from paths import AUDIT_LOCAL as AUD
from compat import child_env
def write_back(word, g, assign):
    w2 = copy.deepcopy(word)
    for k in g.var:
        regs, F0, sec, idx = g.nodes[k]; Fv = list(F.basis(tuple(assign[k])))
        if sec in ("A", "B"): w2[sec][idx][-1] = Fv
        elif sec == "tail": w2["early_cleanup"][idx][1] = Fv
    for k, (regs, F0, sec, idx) in enumerate(g.nodes):   # forced (L == U) mutable vertices carry their forced frame in nodes
        if k not in g.varset and sec in ("A", "B") and k in set(g.mutable): w2[sec][idx][-1] = list(F0)
        elif k not in g.varset and sec == "tail" and k in set(g.mutable): w2["early_cleanup"][idx][1] = list(F0)
    paid, centre, widths, starts, ends, endB = recount(w2)
    rep = dict(w2["report"]); rep["local_profile"] = {str(k): v for k, v in sorted(paid.items())}; rep["local_rank_mass"] = sum(k * v for k, v in paid.items())
    rep["width_inventory"] = {str(k): v for k, v in sorted(collections.Counter(widths).items())}; w2["report"] = rep
    return w2
def canon(w): return json.dumps(w, sort_keys=True, separators=(",", ":")).encode()
def audit(w, keep=None):
    d = tempfile.mkdtemp(prefix="eft-audit-"); p = os.path.join(d, "FULL-WORD.json.gz")
    open(p, "wb").write(gzip.compress(canon(w), mtime=0))
    r = subprocess.run([sys.executable, "-B", AUD, "--word", p, "--output", os.path.join(d, "AUDIT.json")], capture_output=True, text=True, encoding="utf-8", errors="replace", env=child_env())
    ok = r.returncode == 0
    msg = (r.stdout + r.stderr).strip().splitlines()[-1][:160] if (r.stdout + r.stderr).strip() else ""
    if keep:
        import shutil; shutil.copy(p, keep)
    rep = json.load(open(os.path.join(d, "AUDIT.json"), encoding="utf-8")) if ok else msg
    import shutil; shutil.rmtree(d, ignore_errors=True)
    return ok, rep, hashlib.sha256(canon(w)).hexdigest()
