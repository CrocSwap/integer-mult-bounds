"""harness: exact pricing harness for B-phase delivery rewrites on gauge44-lineage words.
Edits: dict(delete=[B idx], insert=[(pos, gate)], tail=[(early_pos, gate)], prepend=[gate]) on a base word, all indices
refer to the BASE word (as in build_tri.py).  New gates carry frame [] (frames are re-solved exactly).
Exactness screen: the composed map of B + early tails + cleanup prepends is unchanged mod p (sufficient for the whole
program map, since A/cut and the remaining cleanup are untouched).  Pricing: exact optimal frames with tails, cone caps
(recomputed for the candidate) and cut equality."""
import copy, gzip, hashlib, json, resource, signal, sys
import frames as F
from word import inline, recount
from model import cone_caps
from exchange import coef_mod
V = 112; PR = 2147483629
# Cost weights are the per-rank moment lower bounds at an endpoint b near the frontier root (override with IMB_B or the
# b argument). Any nearby b ranks frame assignments identically for these words; kappa is always priced exactly in kappa.py.
DEFAULT_B = "67018507072324140917/40000000000000000000000"   # seven-slot k8 T16 complex lower endpoint (#1094)
def regs(e): return e[1:3] if e[0] == 'add' else e[1:2]
def load(p): return json.load(gzip.open(p))
def compile_edits(w, ed):
    B = w['B']; dele = set(ed.get('delete', [])); at = {}
    for p, g in ed.get('insert', []): at.setdefault(p, []).append(list(g[:-1]) + [list(g[-1])] if isinstance(g[-1], list) else list(g) + [[]])
    out = []
    for i, e in enumerate(B):
        out.extend(at.get(i, []))
        if i in dele: continue
        out.append(list(e[:-1]) + [list(e[-1]) if e[-1] is not None else []])
    out.extend(at.get(len(B), []))
    w2 = dict(w); w2['B'] = out
    pre = [list(g[:-1]) + [[256, 128, 64, 32, 16, 8, 4, 2, 1]] for g in ed.get('prepend', [])]
    C = pre + [list(g) for g in w['cleanup']]; sh = len(pre)
    early = [[i + sh, list(U)] for i, U in w['early_cleanup']]
    ins = []
    for j, g in ed.get('tail', []):
        C.append(list(g[:-1]) + [[]]); ins.append((j, len(C) - 1))
    for j, ci in sorted(ins): early.insert(j, [ci, []])      # ascending, sequential (build_tri.py semantics)
    w2['cleanup'] = C; w2['early_cleanup'] = early
    return w2
def seg_rows(w):
    rows = {}
    seq = list(w['B']) + [w['cleanup'][i] for i, U in w['early_cleanup']]
    nearly = {i for i, U in w['early_cleanup']}
    seq += [g for g in w['cleanup'][:w.get('_npre', 0)] if True]
    for e in seq:
        for q in regs(e): rows.setdefault(q, {q: 1})
        q = coef_mod(e); t = e[1]
        if e[0] == 'scale': rows[t] = {k: x * q % PR for k, x in rows[t].items()}
        else:
            d = rows[t]
            for k, x in rows[e[2]].items():
                y = (d.get(k, 0) + q * x) % PR
                if y: d[k] = y
                else: d.pop(k, None)
    return rows
def exact_same(w0, w1, npre):
    a = seg_rows(dict(w0, _npre=0)); b = seg_rows(dict(w1, _npre=npre))
    return all(a.get(q, {q: 1}) == b.get(q, {q: 1}) for q in set(a) | set(b))
class Timeout(Exception): pass
def _alarm(sig, frm): raise Timeout()
class Pricer:
    def __init__(self, base_path, b=None, check_literal=True):
        import os; b = b or os.environ.get("IMB_B", DEFAULT_B)
        self.base = load(base_path) if isinstance(base_path, str) else base_path; self.costs = F.Costs(b); self.c1 = self.costs.c[1]
        caps, _ = cone_caps(self.base); self.caps = caps
        g = F.Graph(inline(self.base, True), check_literal=check_literal, tail_mutable=True, caps=caps, cut_equality=True)
        r = F.optimal_frames(inline(self.base, True), self.costs, check_literal=check_literal, graph=g)
        self.base_cost = r["cost"]; self.base_profile = dict(sorted(r["profile"].items()))
    def price(self, ed, want_word=False, timeout=90):
        w = self.base; npre = len(ed.get('prepend', []))
        try:
            w1 = compile_edits(w, ed)
        except Exception as e: return dict(status="compile:" + str(e)[:60])
        if not exact_same(w, w1, npre): return dict(status="inexact")
        signal.signal(signal.SIGALRM, _alarm); signal.alarm(timeout)
        try:
            caps, comp = cone_caps(w1)
            ent = set(map(int, w1['start_extra'])); low = set(map(int, w1['helper_final']))
            if any(e[2] in ent | low for e in comp): return dict(status="compensation-touches-residual")
            g = F.Graph(inline(w1, True), check_literal=False, tail_mutable=True, caps=caps, cut_equality=True)
            r = F.optimal_frames(inline(w1, True), self.costs, check_literal=False, graph=g)
        except F.Infeasible as e: return dict(status="infeasible", why=str(e.args[0][:3]) if e.args else "")
        except ValueError as e: return dict(status="error:" + str(e)[:80])
        except Timeout: return dict(status="timeout")
        finally: signal.alarm(0)
        out = dict(status="ok" if r["certified"] else "uncertified", delta=r["cost"] - self.base_cost, profile=dict(sorted(r["profile"].items())))
        if want_word:
            from writeback import write_back
            out["word"] = write_back(w1, g, r["assign"])
        if resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024 ** 3 > 6: out["rss_exit"] = True
        return out
