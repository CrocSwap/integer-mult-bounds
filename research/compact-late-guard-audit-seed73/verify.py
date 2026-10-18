#!/usr/bin/env python3
"""Exact two-pass compact-control audit; no supplier or kappa claim.

Hanson Sun / bbMisk, with substantial OpenAI Codex assistance. Apache-2.0.
The quotient interpreter below is separately written from the pinned physical
swap/rotation interpreter. This is not independent human review.
"""
import argparse
from fractions import Fraction as Q
import hashlib
import importlib
import json
from pathlib import Path
import random
import struct
import sys

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
LIVE_INPUTS = {
    "notes/compact-control-movement.tex",
    "scripts/audit_compact_controls.py", "scripts/certify.py",
    "scripts/prepare_layers.py", "scripts/search_network.py",
    "tests/test_compact_controls.py",
}
DOMAINS = ((1, 2, 1), (1, 3, 2), (2, 2, 1),
           (2, 3, 2), (2, 4, 2), (3, 2, 1))


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def source_check():
    pins = json.loads((PACKAGE / "SOURCES.json").read_text())
    live = [p for p in pins["files"] if p["usage"] == "input"]
    need(len(live) == len(LIVE_INPUTS) and
         {p["path"] for p in live} == LIVE_INPUTS, "source inventory differs")
    docs = pins["source_documents"]
    need({p["path"] for p in docs} == {
        "sources/pr763-PROOF.md", "sources/pr763-README.md",
        "sources/pr1219-PROOF.md", "sources/pr1219-README.md",
    } and len(docs) == 4, "predecessor inventory differs")
    hashes = {}
    for home, items in ((ROOT, live), (PACKAGE, docs)):
        for pin in items:
            data = (home / pin["path"]).read_bytes()
            digest = hashlib.sha256(data).hexdigest()
            blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
            need(digest == pin["sha256"] and blob == pin["git_blob"],
                 "source drift: " + pin["path"])
            hashes[pin["path"]] = digest
    return hashes


class Geometry:
    """Project away the unchanged low rho bits; keep the entire upper field.

    Tables are just exact integer offsets. No source program, guard, producer,
    previous audit implementation or receipt is imported here.
    """
    def __init__(self, n, K, G, rho=None):
        self.n, self.K, self.G = n, K, G
        self.rho = K - 1 if rho is None else rho
        need(n >= 1 and G >= 1 and K >= G + 1 and 0 <= self.rho < K,
             "outside proved parameter domain")
        self.B, self.A, self.R = 1 << G, 1 << (K - 1), 1 << K
        self.U = 1 << (n * G)
        self.Y = 1 << ((n + 1) * K - self.rho)
        self.Z = 1 << n
        self.digits = [tuple((t >> (G * i)) & (self.B - 1) for i in range(n))
                       for t in range(self.U)]
        self.parity = [sum((d & 1) << i for i, d in enumerate(ds)) for ds in self.digits]
        self.compact = [sum(((z >> i) & 1) << (G * i) for i in range(n))
                        for z in range(self.Z)]
        self.wide = [sum(((z >> i) & 1) << (K * i) for i in range(n))
                     for z in range(self.Z)]
        self.nonsaturated = [all(d < self.B - 1 for d in ds) for ds in self.digits]
        self.first = [[sum(2 * ((z >> i) & 1) * d * (self.R ** i)
                           for i, d in enumerate(ds)) for ds in self.digits]
                      for z in range(self.Z)]
        self.second = [[sum(((z >> i) & 1) * (1 - 2 * d) * (self.R ** i)
                            for i, d in enumerate(ds)) for ds in self.digits]
                       for z in range(self.Z)]
        self.selected = ([self.bits(y) for y in range(self.Y)] if self.Y <= 4096 else None)

    def bits(self, y):
        return sum(((y >> (i * self.K)) & 1) << i for i in range(self.n))

    def read(self, y):
        return self.bits(y) if self.selected is None else self.selected[y]

    def earlier(self, y, t, z, inverse=False):
        if inverse:
            t = (t + self.compact[self.read(y) ^ z]) % self.U
            y = (y - self.second[z][t]) % self.Y
            t = (t - self.compact[self.read(y)]) % self.U
            y = (y - self.first[z][t]) % self.Y
        else:
            y = (y + self.first[z][t]) % self.Y
            t = (t + self.compact[self.read(y)]) % self.U
            y = (y + self.second[z][t]) % self.Y
            t = (t - self.compact[self.read(y) ^ z]) % self.U
        return y, t

    def later(self, c, y, t, u, inverse=False):
        if inverse:
            loaded = (u + self.compact[c]) % self.U
            y, t = self.earlier(y, t, self.parity[loaded], True)
            restored = (loaded - self.compact[c]) % self.U
            y, t = self.earlier(y, t, self.parity[restored], True)
        else:
            y, t = self.earlier(y, t, self.parity[u])
            loaded = (u + self.compact[c]) % self.U
            y, t = self.earlier(y, t, self.parity[loaded])
            restored = (loaded - self.compact[c]) % self.U
        need(restored == u, "source compact field not restored")
        return y, t

    def source_ok(self, c, u):
        return all(not (((c >> i) & 1) and self.digits[u][i] == self.B - 1)
                   for i in range(self.n - 1))

    def good(self, c, y, t, u):
        if not self.nonsaturated[t] or not self.source_ok(c, u):
            return False
        active = self.parity[u] | c
        return all(((y >> (i * self.K + 1)) & (self.A - 1))
                   + ((active >> i) & 1) * self.digits[t][i] < self.A
                   for i in range(self.n - 1))

    def one_pass_good(self, y, t, z):
        return self.nonsaturated[t] and all(
            ((y >> (i * self.K + 1)) & (self.A - 1))
            + ((z >> i) & 1) * self.digits[t][i] < self.A
            for i in range(self.n - 1))


def fraction(n, K, G):
    B, A = 1 << G, 1 << (K - 1)
    factor = 1 - Q(1, 2 * B) - Q((3 * B - 2) * (B - 2), 8 * A * B)
    return Q(B - 1, B) ** n * factor ** (n - 1)


def census(g):
    counts = dict(states=0, admitted=0, agrees_outside_guard=0,
                  target_correct_dirty_wrong=0, first_guard_false_acceptances=0)
    digest = hashlib.sha256()
    for c in range(g.Z):
        for u in range(g.U):
            p, q = g.parity[u], g.parity[(u + g.compact[c]) % g.U]
            need(g.source_ok(c, u) == (p ^ q == c), "source carry equivalence")
            for t in range(g.U):
                for y in range(g.Y):
                    mid_y, mid_t = g.earlier(y, t, p)
                    out_y, out_t = g.earlier(mid_y, mid_t, q)
                    wanted = y ^ g.wide[c]
                    admitted = g.good(c, y, t, u)
                    first_correct = (mid_y, mid_t) == (y ^ g.wide[p], t)
                    second_correct = (out_y, out_t) == (mid_y ^ g.wide[q], mid_t)
                    safe_calls = (g.nonsaturated[t] and p ^ q == c and
                                  first_correct and second_correct)
                    need(admitted == safe_calls, "two-pass contract equivalence")
                    need(not admitted or (out_y, out_t) == (wanted, t),
                         "guard admitted a wrong full map")
                    need(g.good(c, wanted, t, u) == admitted, "ideal guard invariance")
                    need(g.good(c, out_y, out_t, u) == admitted, "actual guard invariance")
                    need(g.later(c, out_y, out_t, u, True) == (y, t), "literal inverse")
                    counts["states"] += 1
                    counts["admitted"] += admitted
                    counts["agrees_outside_guard"] += (not admitted and (out_y, out_t) == (wanted, t))
                    counts["target_correct_dirty_wrong"] += (out_y == wanted and out_t != t)
                    counts["first_guard_false_acceptances"] += (
                        g.source_ok(c, u) and g.one_pass_good(y, t, p) and
                        (out_y, out_t) != (wanted, t))
                    digest.update(struct.pack("<7I", c, u, t, y, out_y, out_t, admitted))
    need(Q(counts["admitted"], counts["states"]) == fraction(g.n, g.K, g.G),
         "complete-rectangle density")
    return dict(n=g.n, K=g.K, G=g.G, rho=g.rho, **counts,
                good_fraction=str(fraction(g.n, g.K, g.G)),
                complete_map_sha256=digest.hexdigest())


def density_checks():
    rows = []
    for G in (1, 2, 3, 4):
        B = 1 << G
        for K in (G + 1, G + 2, G + 3):
            A = 1 << (K - 1)
            # Directly count both original parity controls and the source load.
            count = sum(1 for c in (0, 1) for u in range(B) for t in range(B - 1)
                        for guard in range(A) if u + c < B
                        and guard + (u % 2) * t < A
                        and guard + ((u + c) % 2) * t < A)
            expected = (B - 1) * ((2 * B - 1) * A - Q((3 * B - 2) * (B - 2), 4))
            need(count == expected, "local correlated guard count")
            for n in (1, 2, 3, 7):
                enumerated = Q(B - 1, B) * Q(count, 2 * B * B * A) ** (n - 1)
                exact = fraction(n, K, G)
                union = Q(n, B) + (n - 1) * (Q(1, 2 * B) +
                        Q((3 * B - 2) * (B - 2), 8 * A * B))
                need(enumerated == exact and 1 - exact <= min(1, union), "density/union bound")
            rows.append(dict(G=G, K=K, interior_admitted=count))
    n, K, G = 2, 6, 2
    B, A = 1 << G, 1 << (K - 1)
    old = (Q(B - 1, B) ** 2 * Q(max(A - 4 * B, 0), A)) ** n
    source_aware_old = Q(B - 1, B) ** n * Q(max(A - 4 * B, 0), A) ** n * Q(2 * B - 1, 2 * B) ** (n - 1)
    need(old == Q(81, 1024) and source_aware_old == Q(63, 512)
         and fraction(n, K, G) == Q(1971, 4096), "seed fixture densities")
    return dict(local_counts=rows, all_n_instances=48,
                seed_fixture=dict(n=n, K=K, G=G, retained=str(old),
                                  pr763_source_aware_old_target=str(source_aware_old),
                                  two_pass=str(fraction(n, K, G))))


def mathematical_controls():
    g = Geometry(2, 6, 2, 1)
    controls = {}
    # Projected y=62 means physical y=124 at rho=1.
    for name, u, use_second in (("first_guard_only", 0, False), ("second_guard_only", 1, True)):
        c, y, t = 1, 62, 1
        z = g.parity[(u + g.compact[c]) % g.U] if use_second else g.parity[u]
        actual = g.later(c, y, t, u)
        need(g.source_ok(c, u) and g.one_pass_good(y, t, z), name + " premise")
        need(actual == (63, 5) and not g.good(c, y, t, u), name + " counterexample")
        controls[name] = dict(c=c, y=y, t=t, u=u, actual=list(actual), ideal=[63, 1])
    need(g.later(1, 0, 0, 3) == (65, 0) and not g.source_ok(1, 3), "interior u carry control")
    controls["drop_interior_u_guard"] = dict(actual=[65, 0], ideal=[1, 0])
    need(31 + 1 == g.A and g.later(1, 62, 1, 0) != (63, 1), "strict boundary control")
    controls["replace_strict_with_nonstrict"] = "equality admits first_guard_only witness"
    need(g.later(1, 62, 1, 0)[0] == 63 and g.later(1, 62, 1, 0)[1] != 1,
         "target-only check must miss dirt")
    controls["target_only_check"] = "right target, wrong temporary"
    h = Geometry(1, 3, 2)
    need(h.later(1, 1, 3, 0) == (8, 3), "saturated t control")
    controls["drop_nonsaturation"] = dict(actual=[8, 3], ideal=[0, 3])
    need(h.good(1, 6, 1, 3) and h.later(1, 6, 1, 3) == (7, 1), "outgoing carries positive control")
    controls["forbid_final_carries"] = "rejects valid n=1 u=3 c=1 g=3 t=1"
    naive = Q(3, 4) ** 2 * Q(7, 8) * (1 - Q(3, 4) * Q(1, 32))
    need(naive != fraction(2, 6, 2), "source guard/control parity correlation control")
    controls["assume_independent_control_parity"] = dict(wrong=str(naive), correct=str(fraction(2, 6, 2)))
    return controls


def source_comparisons():
    sys.path.insert(0, str(ROOT / "scripts"))
    physical = importlib.import_module("audit_compact_controls")
    rng = random.Random(73)
    count = good = top_changes = 0
    for n, K, G in (*DOMAINS, (2, 6, 2), (3, 8, 2), (4, 7, 2), (5, 10, 1)):
        for rho in sorted({0, K - 1, 73 % K}):
            g = Geometry(n, K, G, rho)
            order, ops = physical.program(n, K, rho, G, True)
            need(sum(op[0] == "swap" for op in ops) == 12 and
                 sum(op[0] == "rotate" for op in ops) == 10, "complete primitive invoice")
            need(all(op[0] == "swap" or all(order.index(c) < order.index(op[1]) for c in op[2])
                     for op in ops), "physical source-control order")
            for _ in range(64):
                width = (n + 1) * K
                state = {k: rng.randrange(1 << (width if k in ("x", "y") else n * G)) for k in order}
                c = g.bits(state["x"] >> rho)
                projected = state["y"] >> rho
                model_y, model_t = g.later(c, projected, state["t"], state["u"])
                expected = dict(state, y=(model_y << rho) | (state["y"] & ((1 << rho) - 1)), t=model_t)
                actual = physical.execute(state, n, K, rho, G, late=True)
                need(actual == expected, "physical source/model discrepancy")
                need(physical.execute(actual, n, K, rho, G, late=True, inverse=True) == state,
                     "physical literal inverse")
                top = ((state["x"] >> (rho + n * K)) & 1) << (rho + n * K)
                completed = dict(actual, y=actual["y"] ^ top)
                wanted = dict(state, y=state["y"] ^ (g.wide[c] << rho) ^ top)
                if g.good(c, projected, state["t"], state["u"]):
                    need(completed == wanted, "completed highest-bit endpoint")
                    good += 1
                    top_changes += bool(top)
                count += 1
    need(good > 0 and top_changes > 0, "nonempty physical/highest-bit coverage")
    # Exact physical first-pass-only counterexample; arbitrary nonzero back field.
    state = dict(x=2, y=124, t=1, u=0, b=7)
    actual = physical.execute(state, 2, 6, 1, 2, late=True)
    need(actual == dict(state, y=126, t=5), "physical counterexample changed")
    return dict(seed=73, samples=count, admitted_samples=good,
                admitted_highest_bit_changes=top_changes, swaps=12, rotations=10,
                counterexample=dict(input=state, actual=actual, ideal=dict(state, y=126)))


def repair_checks():
    g = Geometry(2, 3, 2)
    checked = wrong_payloads = holes_total = 0
    for c in (1, 2, 3):
        for u in (0, 1, 3, 15):
            # x,u,b are restored for every raw address. t is NOT frozen.
            observed, ideal = {}, {}
            for y in range(g.Y):
                for t in range(g.U):
                    out = g.later(c, y, t, u)
                    need(out not in observed, "raw quotient not bijective")
                    observed[out] = (y, t)
                    ideal[y ^ g.wide[c], t] = (y, t)
            holes = {q for q in observed if not g.good(c, q[0], q[1], u)}
            records, wrong = [], {}
            for q in holes:
                old_y, old_t = g.later(c, *q, u, inverse=True)
                key = (old_y ^ g.wide[c], old_t)
                records.append((key, observed[q]))
                wrong[q[0] ^ g.wide[c], q[1]] = observed[q]
            need(len({key for key, _ in records}) == len(holes) and
                 {key for key, _ in records} == holes, "repair keys do not fill holes")
            repaired = dict(observed)
            for key, payload in sorted(records):
                repaired[key] = payload
            need(repaired == ideal, "sorted repair misplaced a payload")
            need(set(wrong) == holes, "wrong-key control should still fill holes")
            wrong_payloads += sum(payload != ideal[key] for key, payload in wrong.items())
            checked += len(observed)
            holes_total += len(holes)
    need(wrong_payloads > 0, "wrong-key control did not detect payload corruption")
    return dict(blocks=12, records=checked, holes=holes_total,
                wrong_key_payload_mismatches=wrong_payloads)


def verify():
    hashes = source_check()
    controls = mathematical_controls()
    densities = density_checks()
    rows = [census(Geometry(n, K, G)) for n, K, G in DOMAINS]
    return dict(status="PASS_COMPACT_LATE_TWO_PASS_GUARD", source_sha256=hashes,
                domains=rows, states=sum(r["states"] for r in rows),
                admitted=sum(r["admitted"] for r in rows),
                mathematical_controls=controls, density=densities,
                physical=source_comparisons(), repair=repair_checks(),
                scope="Two-pass sufficient invariant envelope; not the global exact agreement set. No new kappa.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="write a fresh receipt; never overwrite")
    parser.add_argument("--check-inputs", action="store_true")
    args = parser.parse_args()
    if args.check_inputs:
        source_check()
        print("PASS_COMPACT_LATE_INPUT_PINS")
        return
    if args.write:
        need(not args.write.exists(), "receipt destination already exists")
    else:
        need((PACKAGE / "EXPECTED.json").is_file(), "expected receipt missing")
    result = verify()
    payload = canonical(result)
    if args.write:
        with args.write.open("x") as out:
            out.write(payload)
    else:
        need(payload == (PACKAGE / "EXPECTED.json").read_text(), "expected receipt mismatch")
    print(result["status"], "states=" + str(result["states"]),
          "admitted=" + str(result["admitted"]),
          "physical=" + str(result["physical"]["samples"]), "no_new_kappa")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print("FAIL_COMPACT_LATE_GUARD:", exc, file=sys.stderr)
        raise SystemExit(1)
