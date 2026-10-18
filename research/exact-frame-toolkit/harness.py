"""harness: pricing harness for B-phase delivery rewrites on gauge44-lineage words.
Edits: dict(delete=[B idx], insert=[(pos, gate)], tail=[(early_pos, gate)], prepend=[gate]) on a base word, all indices
refer to the BASE word (as in build_tri.py).  New gates carry frame [] (frames are re-solved by frames.py).

Program semantics (unchanged independent/audit_local.py): precondition + compensation + A + cut + B + tail + rest, where the
compensation is DERIVED from the A+cut+B map (port rows, helper columns), tail = the early-cleanup gates and rest = the other
cleanup gates (prepends run first in rest).  Screens, in order:
  1. program_violation: the auditor's static program rules (ranges, dyadic units, self adds, target reads, duplicate
     early gates, remaining cleanup only on FULL-end registers);
  2. exact_same: the B + tail + prepend map is unchanged mod p;
  3. the derived compensation is unchanged (exact).  Without 3, a port written in B and undone in the tail passes 2 but
     changes the compensation, so the whole program changes (status 'compensation-changed').
1-3 with A, cut, precondition and the original remaining cleanup untouched give an unchanged whole-program map mod p.
Every candidate reported with a negative delta, and every word returned with want_word=True, is then written back and run
through the unchanged audit_local.py (exact rational endpoints in both orientations, frames, cones); a rejection becomes
status 'audit-rejected'.  Pricing: frames.optimal_frames with tails, recomputed cone caps and cut equality.  `delta` is in
surrogate units (frames.Costs); with Pricer(..., interval=True) each result also carries rigorous true-moment bounds."""
import copy, gzip, hashlib, json, sys
from fractions import Fraction as Q
import frames as F
from word import inline, recount
from model import cone_caps
from exchange import coef_mod
from compat import Timeout, deadline, peak_rss_gib
V = 112; PR = 2147483629
# Cost weights are the per-rank moment lower bounds at an endpoint b near the frontier root (override with IMB_B or the
# b argument). Deltas compare per-call moments at this b only; kappa is never inferred from them (kappa.py, package chain).
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
    """B + tail + prepend map unchanged mod p.  Not sufficient alone: see the module docstring (compensation)."""
    a = seg_rows(dict(w0, _npre=0)); b = seg_rows(dict(w1, _npre=npre))
    return all(a.get(q, {q: 1}) == b.get(q, {q: 1}) for q in set(a) | set(b))
def _dyadic(n, d):
    if d == 0: return False
    den = abs(d)
    if den & (den - 1): den = Q(n, d).denominator      # the auditor reduces the fraction first
    return den & (den - 1) == 0
def program_violation(w):
    """the static program rules of audit_local.run, or None.  Gate frames are not checked here (frames.Graph models them)."""
    v = w['report']['v']; R = w['report']['R']; n = 2 * v + R
    for e in w['A'] + w['cut'] + w['B'] + w['precondition'] + w['cleanup']:
        if e[0] not in ('add', 'scale'): return 'unknown scalar primitive'
        if not all(0 <= k < n for k in regs(e)): return 'register out of range'
        num, den = (e[3], e[4]) if e[0] == 'add' else (e[2], e[3])
        if not _dyadic(num, den): return 'non-dyadic scalar'
        if e[0] == 'scale' and (num == 0 or abs(num) & (abs(num) - 1)): return 'non-unit scale'
        if e[0] == 'add' and e[1] == e[2]: return 'self add'
    if any(e[0] == 'add' and v <= e[2] < 2 * v and not v <= e[1] < 2 * v for e in w['A'] + w['B']): return 'non-target reads target'
    ids = [i for i, U in w['early_cleanup']]
    if len(set(ids)) != len(ids): return 'duplicate early cleanup gate'
    low = {int(q) for q, U in w.get('helper_final', {}).items() if len(F.basis(tuple(U))) < 9}
    ports = range(v, 2 * v)    # port end frames are the hyperplanes perp(port), never FULL
    early = set(ids)
    if any(any(q in low or q in ports for q in regs(e)) for i, e in enumerate(w['cleanup']) if i not in early): return 'full cleanup reads a low end'
    return None
class Pricer:
    def __init__(self, base_path, b=None, check_literal=True, interval=False):
        import os; b = b or os.environ.get("IMB_B", DEFAULT_B)
        self.base = load(base_path) if isinstance(base_path, str) else base_path; self.costs = F.Costs(b); self.c1 = self.costs.c[1]
        self.interval = interval
        caps, self.compensation = cone_caps(self.base); self.caps = caps
        g = F.Graph(inline(self.base, True), check_literal=check_literal, tail_mutable=True, caps=caps, cut_equality=True)
        r = F.optimal_frames(inline(self.base, True), self.costs, check_literal=check_literal, graph=g, interval=interval)
        self.base_cost = r["cost"]; self.base_profile = dict(sorted(r["profile"].items())); self.base_certified = r["certified"]
        self.base_interval = r.get("interval")
    def price(self, ed, want_word=False, timeout=90):
        w = self.base; npre = len(ed.get('prepend', []))
        try:
            w1 = compile_edits(w, ed)
        except Exception as e: return dict(status="compile:" + str(e)[:60])
        why = program_violation(w1)
        if why: return dict(status="rule:" + why)
        if not exact_same(w, w1, npre): return dict(status="inexact")
        try:
            with deadline(timeout):
                caps, comp = cone_caps(w1)
                if comp != self.compensation: return dict(status="compensation-changed")
                ent = set(map(int, w1['start_extra'])); low = set(map(int, w1['helper_final']))
                if any(e[2] in ent | low for e in comp): return dict(status="compensation-touches-residual")
                g = F.Graph(inline(w1, True), check_literal=False, tail_mutable=True, caps=caps, cut_equality=True)
                r = F.optimal_frames(inline(w1, True), self.costs, check_literal=False, graph=g, interval=self.interval)
        except F.Infeasible as e: return dict(status="infeasible", why=str(e.args[0][:3]) if e.args else "")
        except ValueError as e: return dict(status="error:" + str(e)[:80])
        except Timeout: return dict(status="timeout")
        out = dict(status="ok" if r["certified"] else "uncertified", delta=r["cost"] - self.base_cost, profile=dict(sorted(r["profile"].items())))
        if self.interval: out.update(self.compare(r["profile"], r["interval"]))
        if want_word or out["delta"] < 0:
            from writeback import write_back, audit
            word = write_back(w1, g, r["assign"])
            ok, rep, sha = audit(word); out["audit"] = ok
            if not ok: out["status"] = "audit-rejected"; out["why"] = rep
            if want_word: out["word"] = word
        rss = peak_rss_gib()
        if rss is not None and rss > 6: out["rss_exit"] = True   # peak above 6 GiB: recycle this worker
        return out
    def compare(self, profile, iv):
        """true-moment comparison with the base at b (units of 2^-unit_bits moment).
        realized_delta_units: bounds of (H_candidate - H_base) . T(b) for the two returned assignments; gain_certified: its
        upper bound is negative.  max_gain_units: no frame assignment of the candidate program has a per-call moment at b
        below the base's returned assignment by more than this (rigorous; it includes both interval widths)."""
        c = self.costs; unit = 1 << c.unit_bits; d = {}
        for r in set(profile) | set(self.base_profile): d[r] = profile.get(r, 0) - self.base_profile.get(r, 0)
        lo = sum(n * (c.exact[r] if n > 0 else c.upper[r]) for r, n in d.items()); hi = sum(n * (c.upper[r] if n > 0 else c.exact[r]) for r, n in d.items())
        gain = max(Q(0), self.base_interval["upper"] - iv["lower"])
        return dict(realized_delta_units=(float(lo * unit), float(hi * unit)), max_gain_units=float(gain * unit), interval_width_units=iv["width_units"],
                    gain_certified=hi < 0)
