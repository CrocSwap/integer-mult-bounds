"""controls: negative controls for the k8 CB2 composition, applied directly to the composed word and judged by
the upstream independent audit_local.py (each mutant must be REJECTED; the honest word must PASS).
Per site (t, H, A): drop_restore, drop_donation, flip_donation_sign, keep_fused_read, drop_donation_and_restore.
usage: python -B controls.py BASE_PRE.json.gz COMPOSED.json.gz COMPOSE.json OUT.json"""
import copy, gzip, json, os, subprocess, sys, tempfile
from paths import AUDIT_LOCAL; AUD = str(AUDIT_LOCAL)
from compat import child_env
FULL = [256, 128, 64, 32, 16, 8, 4, 2, 1]
def load(p): return json.loads(gzip.decompress(open(p, 'rb').read()))
def audit(w, d):
    p = os.path.join(d, "W.json.gz"); open(p, "wb").write(gzip.compress(json.dumps(w, separators=(',', ':')).encode(), mtime=0))
    a = subprocess.run([sys.executable, "-B", AUD, "--word", p, "--output", os.path.join(d, "A.json")], capture_output=True, text=True, encoding="utf-8", errors="replace", env=child_env())
    lines = (a.stdout + a.stderr).strip().splitlines(); msg = lines[-1] if lines else ""
    return ("PASS" if a.returncode == 0 else "REJECT"), msg[-150:]
def drop_cleanup(w, ci):
    w['cleanup'] = w['cleanup'][:ci] + w['cleanup'][ci + 1:]
    w['early_cleanup'] = [[i - 1 if i > ci else i, U] for i, U in w['early_cleanup']]
def base_to_out(base, ed):
    dele = set(ed['delete']); nins = {}
    for p, g in ed['insert']: nins[p] = nins.get(p, 0) + 1
    m = {}; out = 0
    for i in range(len(base['B']) + 1):
        out += nins.get(i, 0); m[i] = out
        if i < len(base['B']) and i not in dele: out += 1
    return m
if __name__ == "__main__":
    base, w0, comp, outp = load(sys.argv[1]), load(sys.argv[2]), json.load(open(sys.argv[3], encoding="utf-8")), sys.argv[4]
    ed = comp['edits']; pos = base_to_out(base, ed); res = []; d = tempfile.mkdtemp(prefix="eft-controls-")
    st, msg = audit(w0, d); res.append(dict(name="honest", outcome=st, msg=msg)); print("honest", st, flush=True); assert st == "PASS", msg
    for (t, A, H, p) in comp['sites']:
        don = [i for i, g in enumerate(w0['B']) if g[0] == 'add' and g[1] == H and g[2] == A]; assert len(don) == 1, don; di = don[0]
        pre = [i for i, g in enumerate(w0['cleanup'][:len(ed['prepend'])]) if g[1] == H and g[2] == A]; assert len(pre) == 1, pre; ci = pre[0]
        rd = [i for i in ed['delete'] if base['B'][i][0] == 'add' and base['B'][i][1] == t and base['B'][i][2] == A]; assert len(rd) == 1, rd
        muts = {}
        w = copy.deepcopy(w0); drop_cleanup(w, ci); muts['drop_restore'] = w
        w = copy.deepcopy(w0); del w['B'][di]; muts['drop_donation'] = w
        w = copy.deepcopy(w0); g = w['B'][di]; w['B'][di] = g[:3] + [-g[3]] + g[4:]; muts['flip_donation_sign'] = w
        w = copy.deepcopy(w0); w['B'].insert(pos[rd[0]], list(base['B'][rd[0]])); muts['keep_fused_read'] = w
        w = copy.deepcopy(w0); drop_cleanup(w, ci); del w['B'][di]; muts['drop_donation_and_restore'] = w
        for name, w in muts.items():
            st, msg = audit(w, d); res.append(dict(name=f"{name}@{t}", outcome=st, msg=msg)); print(f"{name}@{t}", st, msg[-100:], flush=True)
    json.dump(res, open(outp, "w", encoding="utf-8", newline="\n"), indent=1)
    print("honest PASS; rejected", sum(1 for c in res[1:] if c['outcome'] == 'REJECT'), "of", len(res) - 1)
