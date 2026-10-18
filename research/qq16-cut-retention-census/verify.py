#!/usr/bin/env python3
"""In-place availability census of PR2443's two-cut QQ16 observation contract.

For each of the 224 port arrays observed by PR2443 (starship-s, head
545c05e1) this checker decides whether its value is still held, unchanged, by
some live logical field at two decode points of the pinned 19-event QQ16
recipe: (d1) immediately after B_1_2 and (d18) after the final terminal.

Model.  Fields are logical port arrays of four bank pairs (X/Y, 112 ports).
The local maps are the conserved F_s / B_(s,t) maps of
research/joint-query/evidence/CONSERVED-QQ16.md, equations (1) and (3) (also
the packet's F_contract/B_contract strings); the bridge and ordinary-terminal
semantics are those stated in PR2346 section 1.  Every value is tracked
exactly as a rational linear form in all 896 initial port arrays.  The
executable instance is the owner- and payload-constant subspace, on which
every actual cover route D_s acts as the identity.  Consequences:

* an inequality found here is an exact counterexample for the actual
  routed maps (an actual equality would restrict to equality here);
* a survival claim is accepted only with the symbolic support argument
  "no event in (cut, decode point] writes this field".

New code: Apache-2.0.  Prepared by thakrarsagar with substantial AI
assistance from Claude (Anthropic, Claude Opus 5.5).  No predecessor
executable is imported.
"""
from fractions import Fraction as Q
from hashlib import sha256
from io import BytesIO
from pathlib import Path
import gzip
import json
import random
import sys
import tarfile

ROOT = Path(__file__).resolve().parents[2]
PACKET = "research/joint-query/certificate.json.gz"
ARCHIVE = "research/community-frontier1042-audit/selected-replay.tar.gz"
PINS = {
    PACKET: "a5ed85fac5ebf3c091482a113ab0d351eb5a7892fe2841a35e16017ec1ff49f7",
    ARCHIVE: "22c3f4dce4b897a1d423d1388801933e288b6a6b1906cb15e1b16a5eb68db754",
}
TEMPLATE = "t16/global/base/split-centres/GLOBAL-TEMPLATE.json.gz"
TEMPLATE_PIN = "a179dad87651aba340a5a8ddbcd86a8e757cad87b8a1f8bad48106fbecd38518"
A = (0, 7, 20, 27, 36, 46, 57, 111)
T = (21, 37, 47, 76, 81, 87, 92, 110)
U = tuple(p for p in range(112) if p not in A + T)
J = (1, 2, 3, 4, 5, 6, 8, 12)
S = tuple(p for p in U if p not in J)
NP, NF = 4, 4 * 224          # bank pairs, port arrays
DECODE = (1, 18)             # event indices of the two decode points
ITEMS = ("x1_A", "x1_T", "y1_A", "y1_T", "x1_S", "y2_A", "C=x2_U")


class Fail(Exception):
    pass


def need(ok, message):
    if not ok:
        raise Fail(message)


def fid(pair, side, port):
    """Field / variable index; side 0 is X, side 1 is Y."""
    return pair * 224 + side * 112 + port


def fname(i):
    pair, rest = divmod(i, 224)
    side, port = divmod(rest, 112)
    block = "A" if port in A else "T" if port in T else "U"
    return "%s%d[%d,%s]" % ("XY"[side], pair, port, block)


# ---------------------------------------------------------------- forms
def lin(*terms):
    out = {}
    for c, f in terms:
        if c:
            for k, v in f.items():
                out[k] = out.get(k, 0) + c * v
    return {k: v for k, v in out.items() if v}


def key(f):
    return tuple(sorted(f.items()))


def normal_key(f):
    """Key of the line spanned by f (first coefficient scaled to one)."""
    if not f:
        return ()
    items = sorted(f.items())
    lead = items[0][1]
    return tuple((k, v / lead) for k, v in items)


# ---------------------------------------------------------------- sources
def load_sources(R_mutation=False):
    raw = {}
    for name, pin in PINS.items():
        data = (ROOT / name).read_bytes()
        need(sha256(data).hexdigest() == pin, "source pin " + name)
        raw[name] = data
    packet = json.loads(gzip.decompress(raw[PACKET]))
    with tarfile.open(fileobj=BytesIO(raw[ARCHIVE]), mode="r:gz") as tar:
        found = [m for m in tar.getmembers() if m.name == TEMPLATE]
        need(len(found) == 1 and found[0].isfile(), "one template member")
        data = tar.extractfile(found[0]).read()
    need(sha256(data).hexdigest() == TEMPLATE_PIN, "template member pin")
    recipe = json.loads(gzip.decompress(data))["recipe"]
    R = [[Q(row.get(str(p), "0")) for p in range(112)] for row in packet["R_rows"]]
    K = [[Q(row.get(str(i), "0")) for i in range(8)] for row in packet["K_rows"]]
    if R_mutation:
        R[0][U[0]] += 1
    need((tuple(packet["A_ports"]), tuple(packet["T_ports"]), tuple(packet["U_ports"])) == (A, T, U),
         "port partition")
    for ports, g in ((U, 48), (A, 4), (T, 4)):
        need(all(sum(R[i][p] * R[j][p] for p in ports) == g * (i == j)
                 for i in range(8) for j in range(8)), "Gram identity")
    need(all(K[p][i] == R[i][p] / 4 for p in range(112) for i in range(8)), "K = R^T/4")
    need(packet["F_contract"].startswith("f=R_s x. X_U=x_U-K_s,U f; X_A=P_s,A ell_s,T x; X_T=P_s,T f."),
         "packet forward contract")
    need(packet["B_contract"].startswith("u=E_t y; a=ell_s,T x; b=R_s u. Y_A=u_A; Y_U=y_U+K_s,U a; "
                                         "Y_T=u_T-P_s,T(b+11a). X_U=x_U-y_U; X_A=x_A+y_A-u_A; X_T=P_s,T(b+12a)."),
         "packet backward contract")
    need(len(recipe) == 19, "19-event recipe")
    need([e["pair"] for e in recipe if e["kind"] == "local"] == [0, 0, 0, 1, 1, 2, 2, 3, 3], "local pairs")
    need(all(e["reverse"] == bool(e["stage"] % 2) for e in recipe if e["kind"] == "local"), "orientations")
    need(recipe[-1] == {"kind": "terminal", "pairs": 4}, "terminal")
    return R, recipe, {PACKET: PINS[PACKET], ARCHIVE: PINS[ARCHIVE], ARCHIVE + "::" + TEMPLATE: TEMPLATE_PIN}


# ---------------------------------------------------------------- maps
class Model:
    """Constant-subspace realisation of the conserved maps (all D_s = I)."""

    bad_backward = False

    def __init__(self, R):
        self.R = R

    def query(self, x, ports):            # R_ports x_ports : 8 forms
        return [lin(*((self.R[i][p], x[p]) for p in ports)) for i in range(8)]

    def sect(self, q, ports):              # P_V q = R_V^T q / 4 on V (also K restricted to V)
        return {p: lin(*((self.R[i][p] / 4, q[i]) for i in range(8))) for p in ports}

    def forward(self, x, y):
        f = self.query(x, range(112))
        k = self.sect(f, U)
        nx = {p: lin((1, x[p]), (-1, k[p])) for p in U}
        nx.update(self.sect(self.query(x, T), A))      # X_A = P_A ell_T x
        nx.update(self.sect(f, T))                     # X_T = P_T f
        ny = {p: lin((1, y[p]), (1, nx[p])) for p in U}
        for p in A + T:                                # conserved selected sums
            ny[p] = lin((1, x[p]), (1, y[p]), (-1, nx[p]))
        return nx, ny

    def backward(self, x, y):
        # u = E_t y = y + P_A (B_t y_U + ell_T y_T): only the A block changes.
        c = [lin((1, g), (1, h)) for g, h in zip(self.query(y, U), self.query(y, T))]
        corr = self.sect(c, A)
        u = dict(y)
        sign = -1 if self.bad_backward else 1
        for p in A:
            u[p] = lin((1, y[p]), (sign, corr[p]))
        a = self.query(x, T)
        b = self.query(u, range(112))
        ka = self.sect(a, U)
        ny, nx = {}, {}
        for p in U:
            ny[p] = lin((1, y[p]), (1, ka[p]))
            nx[p] = lin((1, x[p]), (-1, y[p]))
        for p in A:
            ny[p] = u[p]
            nx[p] = lin((1, x[p]), (1, y[p]), (-1, u[p]))
        t11 = self.sect([lin((1, bi), (11, ai)) for bi, ai in zip(b, a)], T)
        t12 = self.sect([lin((1, bi), (12, ai)) for bi, ai in zip(b, a)], T)
        for p in T:
            ny[p] = lin((1, u[p]), (-1, t11[p]))
            nx[p] = t12[p]
        return nx, ny


def run(R, recipe, terminal_selected="identity", drop=None, zero_other_pairs=False, model=Model):
    """Return the 19 post-event states (lists of 896 forms) and symbolic write sets."""
    m = model(R)
    state = [{i: Q(1)} if (i < 224 or not zero_other_pairs) else {} for i in range(NF)]
    states, writes = [], []
    for index, e in enumerate(recipe):
        new = list(state)
        written = set()
        if index != drop:
            if e["kind"] == "local":
                k = e["pair"]
                x = {p: state[fid(k, 0, p)] for p in range(112)}
                y = {p: state[fid(k, 1, p)] for p in range(112)}
                nx, ny = m.backward(x, y) if e["reverse"] else m.forward(x, y)
                for p in range(112):
                    new[fid(k, 0, p)], new[fid(k, 1, p)] = nx[p], ny[p]
                written = {fid(k, s, p) for s in (0, 1) for p in range(112)}
            elif e["kind"] == "bridge":
                i, j, c = e["src"], e["dst"], e["coefficient"]
                for p in U:      # X_j,U += c X_i,U ; Y_i,U -= c Y_j,U   (PR2346 section 1)
                    new[fid(j, 0, p)] = lin((1, state[fid(j, 0, p)]), (c, state[fid(i, 0, p)]))
                    new[fid(i, 1, p)] = lin((1, state[fid(i, 1, p)]), (-c, state[fid(j, 1, p)]))
                written = {fid(j, 0, p) for p in U} | {fid(i, 1, p) for p in U}
            else:                # (X_U, Y_U) -> (Y_U, -X_U); selected ports optional
                ports = range(112) if terminal_selected == "signed_exchange" else U
                for k in range(NP):
                    for p in ports:
                        new[fid(k, 0, p)] = state[fid(k, 1, p)]
                        new[fid(k, 1, p)] = lin((-1, state[fid(k, 0, p)]))
                written = {fid(k, s, p) for k in range(NP) for s in (0, 1) for p in ports}
        state = new
        states.append(state)
        writes.append(written)
    return states, writes


# ---------------------------------------------------------------- contract
def observations(states):
    """PR2443's 224 observed arrays: (item, cut event index, field, form)."""
    obs = []
    for item, side, ports in (("x1_A", 0, A), ("x1_T", 0, T), ("y1_A", 1, A), ("y1_T", 1, T),
                              ("x1_S", 0, S)):
        obs += [(item, 0, fid(0, side, p)) for p in ports]
    obs += [("y2_A", 1, fid(0, 1, p)) for p in A]
    obs += [("C=x2_U", 1, fid(0, 0, p)) for p in U]
    need(len(obs) == 224 and len({(c, f) for _, c, f in obs}) == 224, "224 distinct observations")
    return [(item, cut, f, states[cut][f]) for item, cut, f in obs]


def decoder_check(R, states, model=Model, x1_U=None):
    """PR2443's ordered decoder recovers all 224 pair-0 inputs in this model.

    With `x1_U` given, the decoder uses those forms for x1 on the U96 ports instead of
    the retained F0-cut x1_S records (the L2 variant; see leads)."""
    m = model(R)
    s0, s1 = states[0], states[1]
    x1 = {p: s0[fid(0, 0, p)] for p in range(112)}
    if x1_U is not None:
        x1.update(x1_U)
    y1 = {p: s0[fid(0, 1, p)] for p in range(112)}
    y2A = {p: s1[fid(0, 1, p)] for p in A}
    C = {p: s1[fid(0, 0, p)] for p in U}
    need(all(C[p] == {fid(0, 1, p): -1} for p in U), "C = x2_U = -y_U")
    q = [lin((1, g), (-1, h)) for g, h in zip(m.query(y2A, A), m.query(y1, A))]
    v = [lin((1, qi), (-1, ti), (1, ci)) for qi, ti, ci in zip(q, m.query(y1, T), m.query(C, U))]
    w = [lin((1, vi), (-1, si)) for vi, si in zip(v, m.query(x1, S))]
    M = [[R[i][p] for p in J] + [Q(i == r) for r in range(8)] for i in range(8)]
    for c in range(8):                    # exact Gauss-Jordan inverse of R_J
        piv = next(r for r in range(c, 8) if M[r][c])
        M[c], M[piv] = M[piv], M[c]
        M[c] = [val / M[c][c] for val in M[c]]
        for r in range(8):
            if r != c and M[r][c]:
                M[r] = [a_ - M[r][c] * b_ for a_, b_ in zip(M[r], M[c])]
    inv = [row[8:] for row in M]
    xJ = {p: lin(*((inv[jp][i], w[i]) for i in range(8))) for jp, p in enumerate(J)}
    x1U = {p: (xJ[p] if p in J else x1[p]) for p in U}
    f = m.query(x1, T)
    t = m.sect(m.query(x1, A), T)
    kf = m.sect(f, U)
    xU = {p: lin((1, x1U[p]), (1, kf[p])) for p in U}
    rest = [lin((1, fi), (-1, bi), (-1, ti)) for fi, bi, ti in zip(f, m.query(xU, U), m.query(t, T))]
    xA = m.sect(rest, A)
    rec = {}
    for p in U:
        rec[fid(0, 0, p)], rec[fid(0, 1, p)] = xU[p], lin((-1, C[p]))
    for p in T:
        rec[fid(0, 0, p)] = t[p]
    for p in A:
        rec[fid(0, 0, p)] = xA[p]
    for p in A + T:
        rec[fid(0, 1, p)] = lin((1, x1[p]), (1, y1[p]), (-1, rec[fid(0, 0, p)]))
    need(all(rec[i] == {i: 1} for i in range(224)), "PR2443 decoder recovers all 224 pair-0 inputs")


def leads(R, states):
    """Two symbolic identities (from CONSERVED-QQ16 (1)/(3)) checked exactly in this model.

    (L1) the selected pair sums of pair 0 are conserved by F0, B1 and F2 and untouched
         afterwards (identity selected terminal): X_V + Y_V = x_V + y_V = x1_V + y1_V;
    (L2) at d1, x1_U = X2_U + Y2_U - K_(1,U) ell_(1,T) x1_T (from x'_U = x_U - y_U and
         y'_U = y_U + K_(s,U) a with y1_U = y_U + x1_U).
    These are recomputation leads, not in-place availability of the observed arrays.
    """
    m = Model(R)
    x1 = {p: states[0][fid(0, 0, p)] for p in range(112)}
    for d in DECODE:
        need(all(lin((1, states[d][fid(0, 0, p)]), (1, states[d][fid(0, 1, p)])) ==
                 {fid(0, 0, p): 1, fid(0, 1, p): 1} for p in A + T), "conserved selected pair sums")
    ka = m.sect(m.query(x1, T), U)
    l2 = {p: lin((1, states[1][fid(0, 0, p)]), (1, states[1][fid(0, 1, p)]), (-1, ka[p])) for p in U}
    need(all(l2[p] == x1[p] for p in U),
         "x1_U from the live post-B1 pair and one 8-coordinate driver record")
    # L2 variant at d1: the driver ell_(1,T) x1_T is computed from the retained x1_T record, so the
    # decoder needs only the 32 retained F0 selected arrays (x1_A, x1_T, y1_A, y1_T) plus the live
    # post-B1 reads y2_A, C = X2_U and Y2_U (Y2_U lies outside PR2443's read set).  The x1_U forms
    # below are built only from states[1] fields and the retained x1_T forms.
    decoder_check(R, states, x1_U=l2)
    return {"L1_selected_pair_sums_live_at_d1_and_d18": 16, "L2_x1_U_from_live_pair_plus_driver_record": 96,
            "L2_variant_d1": {"retained_F0_cut_arrays": len(A) * 2 + len(T) * 2,
                              "extra_post_B1_reads_outside_PR2443_contract": {"Y2_U": len(U)},
                              "decoder_recovers_all_224_pair0_inputs": True}}


def det3(a, b, c):
    return (a[0] * (b[1] * c[2] - b[2] * c[1]) - a[1] * (b[0] * c[2] - b[2] * c[0])
            + a[2] * (b[0] * c[1] - b[1] * c[0]))


def in_span2(o, f, g):
    """Exact test: o lies in the rational span of forms f and g."""
    rows = [[f.get(k, Q(0)), g.get(k, Q(0)), o.get(k, Q(0))] for k in sorted(set(o) | set(f) | set(g))]
    r = 0
    for c in range(2):
        piv = next((i for i in range(r, len(rows)) if rows[i][c]), None)
        if piv is None:
            continue
        rows[r], rows[piv] = rows[piv], rows[r]
        rows[r] = [val / rows[r][c] for val in rows[r]]
        for i in range(len(rows)):
            if i != r and rows[i][c]:
                fac = rows[i][c]
                rows[i] = [a_ - fac * b_ for a_, b_ in zip(rows[i], rows[r])]
        r += 1
    return all(not row[2] for row in rows[r:])


def census(states, writes, obs, seed=20261015):
    """Survival of each observation at the decode points d1 and d18."""
    rng = random.Random(seed)
    pts = [[Q(rng.randint(-10**6, 10**6), rng.randint(1, 10**3)) for _ in range(NF)] for _ in range(3)]

    def ev(f):
        return [sum(v * pt[k] for k, v in f.items()) for pt in pts]

    index = {}
    for d in DECODE:
        exact, line = {}, {}
        for i, f in enumerate(states[d]):
            exact.setdefault(key(f), []).append(i)
            line.setdefault(normal_key(f), []).append(i)
        index[d] = (exact, line, [ev(f) for f in states[d]])
    rows = []
    for item, cut, field, form in obs:
        need(form, "observed array is a nonzero form")
        row = {"item": item, "cut_event": cut, "field": fname(field)}
        ov = ev(form)
        for d in DECODE:
            exact, line, vals = index[d]
            st = states[d]
            touched = any(field in writes[e] for e in range(cut + 1, d + 1))
            same = st[field] == form
            need(same or touched, "a field outside every write set changed")
            span = []
            for k in range(NP):
                for p in range(112):
                    fx, fy = fid(k, 0, p), fid(k, 1, p)
                    # A nonzero 3x3 evaluation determinant certifies o outside the span.
                    if det3(vals[fx], vals[fy], ov) == 0 and in_span2(form, st[fx], st[fy]):
                        span.append(fname(fx) + "|" + fname(fy))
            first = next((e for e in range(cut + 1, d + 1) if states[e][field] != form), None)
            entry = {"same_field_unchanged": same, "untouched_by_write_sets": not touched,
                     "first_overwrite_event": first,
                     "equal_live_fields": [fname(i) for i in exact.get(key(form), [])],
                     "scalar_multiple_live_fields": [fname(i) for i in line.get(normal_key(form), [])],
                     "same_port_two_field_span": span}
            if not touched:      # symbolic survival: no event in (cut, d] writes the field
                need(same and fname(field) in entry["equal_live_fields"], "symbolic survival")
            row["d%d" % d] = entry
        rows.append(row)
    return rows


def summarise(rows):
    keys = ("in_place_same_field", "equal_some_live_field", "scalar_multiple_of_live_field",
            "in_same_port_two_field_span", "copy_required")
    table = {}
    for it in ITEMS:
        sel = [r for r in rows if r["item"] == it]
        entry = {"arrays": len(sel)}
        for d in DECODE:
            es = [r["d%d" % d] for r in sel]
            entry["d%d" % d] = {
                "in_place_same_field": sum(e["same_field_unchanged"] for e in es),
                "equal_some_live_field": sum(bool(e["equal_live_fields"]) for e in es),
                "scalar_multiple_of_live_field": sum(bool(e["scalar_multiple_live_fields"]) for e in es),
                "in_same_port_two_field_span": sum(bool(e["same_port_two_field_span"]) for e in es),
                "copy_required": sum(not e["equal_live_fields"] for e in es),
                "first_overwrite_events": sorted({e["first_overwrite_event"] for e in es
                                                  if e["first_overwrite_event"] is not None}),
            }
        table[it] = entry
    totals = {"d%d" % d: {k: sum(table[it]["d%d" % d][k] for it in ITEMS) for k in keys} for d in DECODE}
    return table, totals


def digest(obj):
    return sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def full(R, recipe, **kw):
    model = kw.pop("model", Model)
    states, writes = run(R, recipe, model=model, **kw)
    rows = census(states, writes, observations(states))
    table, totals = summarise(rows)
    return states, writes, rows, table, totals


def negative_controls(R, recipe, states, totals):
    out = {}
    try:      # 1. claiming x1_A survives B1 (in place) must fail
        need(all(states[1][fid(0, 0, p)] == states[0][fid(0, 0, p)] for p in A), "x1_A survives B1")
        raise RuntimeError("control accepted: x1_A survives B1")
    except Fail:
        out["claim_x1_A_survives_B1"] = "rejected"
    for name, drop, d in (("drop_F2_event3", 3, "d18"), ("drop_B1_event1", 1, "d1")):
        tot = full(R, recipe, drop=drop)[4]          # 2./3. dropping an overwrite event
        need(tot[d] != totals[d], name + " changes the census")
        out[name] = {"changed": True, d + "_totals": tot[d]}
    try:      # 4. wrong C sign must fail
        need(all(states[1][fid(0, 0, p)] == {fid(0, 1, p): 1} for p in U), "C = +y_U")
        raise RuntimeError("control accepted: C = +y_U")
    except Fail:
        out["claim_C_equals_plus_y_U"] = "rejected"
    try:      # 5. corrupted centre coefficient must fail the source checks
        load_sources(R_mutation=True)
        raise RuntimeError("control accepted: corrupted R")
    except Fail:
        out["corrupted_centre_coefficient"] = "rejected"

    class Bad(Model):
        bad_backward = True
    try:      # 6. a wrong future-logger sign in E_t (u_A) must break PR2443's decoder
        decoder_check(R, run(R, recipe, model=Bad)[0], model=Bad)
        raise RuntimeError("control accepted: wrong backward map")
    except Fail:
        out["wrong_E_t_sign_breaks_decoder"] = "rejected"
    return out


def main():
    R, recipe, pins = load_sources()
    states, writes, rows, table, totals = full(R, recipe)
    decoder_check(R, states)
    lead = leads(R, states)
    variants = {}
    for name, kw in (("terminal_also_exchanges_selected", {"terminal_selected": "signed_exchange"}),
                     ("pairs_1_to_3_initially_zero", {"zero_other_pairs": True})):
        variants[name] = full(R, recipe, **kw)[4]
    for d in ("d1", "d18"):
        need(all(v[d]["copy_required"] == totals[d]["copy_required"] for v in variants.values()),
             "copy count stable under the variants")
    write_sets = [{"event": i, "kind": e["kind"], "pair_or_bridge": e.get("pair", [e.get("src"), e.get("dst")]),
                   "fields_written": len(w),
                   "writes_pair0": sorted({"XY"[(f % 224) // 112] + ("A" if f % 112 in A else "T" if f % 112 in T
                                                                     else "U") for f in w if f < 224})}
                  for i, (e, w) in enumerate(zip(recipe, writes))]
    result = {"status": "PASS_QQ16_CUT_RETENTION_CENSUS", "pins": pins,
              "model": "owner/payload-constant subspace (all D_s = I); exact rational linear forms in the "
                       "896 initial port arrays of four pairs; bridges and ordinary terminal per PR2346 section 1",
              "decode_points": {"d1": "after event 1 (B_1_2)", "d18": "after event 18 (terminal)"},
              "write_sets": write_sets, "per_item": table, "totals": totals, "variants": variants,
              "census_rows_sha256": digest(rows), "leads": lead}
    result["receipt_sha256"] = digest({k: result[k] for k in ("per_item", "totals", "variants",
                                                              "census_rows_sha256", "write_sets")})
    result["negative_controls"] = negative_controls(R, recipe, states, totals)
    return result, rows


if __name__ == "__main__":
    res, rows = main()
    here = Path(__file__).resolve().parent
    if "--write" in sys.argv:
        (here / "RESULT.json").write_text(json.dumps(res, indent=1, sort_keys=True) + "\n")
        (here / "CENSUS-ROWS.json").write_text(json.dumps(rows, indent=1, sort_keys=True) + "\n")
    else:
        committed = json.loads((here / "RESULT.json").read_text())
        need(committed == res, "recomputed result equals committed RESULT.json")
        need(json.loads((here / "CENSUS-ROWS.json").read_text()) == rows
             and digest(rows) == res["census_rows_sha256"], "committed CENSUS-ROWS.json equals recomputed rows")
    print(json.dumps({"totals": res["totals"], "negative_controls": sorted(res["negative_controls"])}, indent=1))
    print("PASS_NEGATIVE_CONTROLS", len(res["negative_controls"]))
    print(res["status"])
