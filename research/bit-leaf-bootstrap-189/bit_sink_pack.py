#!/usr/bin/env python3
"""Attack the binding side of the record: the PR189 bit word's terminal sinks.

The frozen bit word in research/paired-cube-twin-local-168 admits terminal root
substitutions (bit/terminal.py, `prove`).  A sink is admissible only if its
target group is disjoint from every other chosen sink's target group, so the
shipped 34-sink selection is one packing, not necessarily a maximum one.  Each
extra sink lowers W (and R) by one at constant rank deficit, which raises the
word's coarse saving a (kappa = a/(1+a)): the bit side is what binds the current
record, so this is the lever.

Flow:
  1. rebuild the shipped profile from the shipped selection (self-check against
     the frozen certificate's bit.profile),
  2. enumerate every admissible (root, pivot) sink root,
  3. extend the shipped family with further rank-23 candidates, validating each
     candidate family through the exact chronology/ledger checks of
     bit/terminal.py::prove,
  4. price the extended family with the shipped exact interval-moment certify(),
  5. price it again with PR184's own select() (the arithmetic the record's
     assembly uses) and write the new profile for the assembly step.

Nothing is claimed that the exact checks do not accept.
"""
from pathlib import Path
from collections import Counter, defaultdict
from fractions import Fraction as Q
import argparse, importlib.util, itertools, json, sys, time

HERE = Path(__file__).resolve().parent


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--package", type=Path, required=True,
                    help="checkout of research/paired-cube-twin-local-168")
    ap.add_argument("--pr184", type=Path,
                    help="research/source-assisted/global/assemble_profiles.py")
    ap.add_argument("--out", type=Path, default=HERE / "bit-profile-extended.json")
    a = ap.parse_args()
    if hasattr(sys, "set_int_max_str_digits"):
        sys.set_int_max_str_digits(0)
    PKG = a.package.resolve()
    sys.path.insert(0, str(PKG / "bit"))
    sys.path.insert(0, str(PKG / "arithmetic"))
    bitword = module("attack_bit_word", PKG / "bit" / "word.py")
    prove = module("attack_bit_prove", PKG / "bit" / "prove.py")
    need = bitword.need

    t0 = time.monotonic()
    word = bitword.Candidate()
    word.exact_frames()
    C, h, v, R = word.C, word.h, word.v, word.R
    ops = word.ops
    baseline = word.row()
    shipped_raw = json.loads((PKG / "selected/bit/sinks.json").read_text())
    shipped_raw = shipped_raw["selected"] if isinstance(shipped_raw, dict) else shipped_raw
    shipped_row = json.loads((PKG / "certificate.json").read_text())["bit"]["profile"]
    print(f"[load {time.monotonic()-t0:.1f}s] v={v} h={h} R={R} roots={len(word.g['roots'])} "
          f"shipped_sinks={len(shipped_raw)} W={baseline['W_per_vertex']} "
          f"deficit={baseline['deficit_per_vertex']}", flush=True)

    # ---- shared structure, copied verbatim from bit/terminal.py::prove --------
    phase = set(word.phase1)
    order = word.phase1 + word.rest
    position = {i: j for j, i in enumerate(word.rest)}
    sources = set(word.source.values())
    aliasroles = set(word.donor) | set(word.donor.values())
    writes, uses, rootids = defaultdict(list), defaultdict(list), defaultdict(list)
    for i, (x, y, n) in enumerate(ops):
        writes[x].append(i)
        uses[y].append(i)
    for j, s in enumerate(word.w["rootroles"]):
        rootids[s].append(j)
    first = [len(word.rest) + 1] * v
    for s in word.order:
        for target in word.gauge[s]["targets"]:
            first[target] = min(first[target], word.readtime[s])

    def admissible(j):
        """Exact predicate list of terminal.prove for one root, minus disjointness."""
        if not (0 <= j < len(word.g["roots"])):
            return None
        r = word.g["roots"][j]
        s = word.w["rootroles"][j]
        U = word.w["root_frame"][j]
        if r["kind"] != "side" or s in sources | aliasroles | set(word.gauge):
            return None
        if rootids[s] != [j] or uses[s] or not writes[s]:
            return None
        if any(i in phase for i in writes[s]):
            return None
        if not all(C.sub(word.opframe[i], U) for i in writes[s]):
            return None
        if not r["targets"]:
            return None
        pivots = [p for p in r["targets"]
                  if first[p] > max(position[i] for i in writes[s])]
        if not pivots:
            return None
        path = [word.opframe[i] for i in writes[s]] + [U, word.w["full_frame"]]
        prev, prefix = None, []
        for f in path:
            if prev is not None and not C.sub(prev, f):
                return None
            d = C.dimf[f] - (0 if prev is None else C.dimf[prev])
            if d:
                prefix.append(d)
            prev = f
        if sum(prefix) != h:
            return None
        return dict(root=j, role=s, targets=sorted(r["targets"]), pivot=pivots[0],
                    pivots=pivots, root_frame=U, writes=list(writes[s]),
                    deleted_path=prefix, root_rank=C.dimf[U])

    cands = [c for c in (admissible(j) for j in range(len(word.g["roots"]))) if c]
    byroot = {c["root"]: c for c in cands}
    assert not [e["root"] for e in shipped_raw if e["root"] not in byroot], \
        "shipped sink is not admissible"
    shipped = [byroot[e["root"]] for e in shipped_raw]
    print(f"[scan {time.monotonic()-t0:.1f}s] admissible sink roots: {len(cands)} "
          f"ranks={sorted(Counter(c['root_rank'] for c in cands).items())} "
          f"shipped_ranks={sorted(Counter(c['root_rank'] for c in shipped).items())} "
          f"target-size={sorted(Counter(len(c['targets']) for c in cands).items())}", flush=True)

    # ---- exact profile path (bit/terminal.py::prove, minus the heavy formal part)
    at = defaultdict(list)
    for s in word.order:
        at[word.readtime[s]].append(s)
    deliveries = defaultdict(list)
    for e in word.k["entries"]:
        deliveries[e["deliver_after_root"]].append(e)
    _, _, source_profile, _ = C.chains()
    cache = {}

    def profile_of(chosen):
        key = tuple(sorted(e["root"] for e in chosen))
        if key in cache:
            return cache[key]
        bywrite = {i: e for e in chosen for i in e["writes"]}
        after = {e["writes"][-1]: e for e in chosen}
        deletedroots = {e["root"] for e in chosen}
        Y, current = Counter(), [None] * v
        events = 0

        def move(t, f):
            nonlocal events
            prev = current[t]
            need(prev is None or C.sub(prev, f), f"target chain nesting t={t} {prev}->{f}")
            need(all(word.module.dot(C.cov[t], b) == 0 for b in C.B[f]),
                 "target movement stays inside cap")
            d = C.dimf[f] - (0 if prev is None else C.dimf[prev])
            need(d >= 0, "target rank monotonicity")
            if d:
                Y[d] += 1
            current[t] = f
            events += 1

        for j, i in enumerate(word.rest):
            for s in at[j]:
                for t in word.gauge[s]["targets"]:
                    move(t, word.gauge[s]["frame"])
            if i in bywrite:
                move(bywrite[i]["pivot"], word.opframe[i])
            if i in after:
                for t in after[i]["targets"]:
                    move(t, after[i]["root_frame"])
        for s in at[len(word.rest)]:
            for t in word.gauge[s]["targets"]:
                move(t, word.gauge[s]["frame"])
        for j, r in enumerate(word.g["roots"]):
            if r["kind"] == "side" and j not in deletedroots:
                for t in r["targets"]:
                    move(t, word.w["root_frame"][j])
            for e in deliveries[j]:
                for t in e["receivers"]:
                    move(t, e["deliver_frame"])
        for t, f in enumerate(current):
            need(f is not None and C.dimf[f] <= h - 1, "final target cap")
            gap = h - 1 - C.dimf[f]
            if gap:
                Y[gap] += 1
        need(sum(r * n for r, n in Y.items()) == v * (h - 1), "full target rank mass")
        local = Counter({int(r): n for r, n in baseline["physical_internal_histogram"].items()})
        for e in chosen:
            local.subtract(e["deleted_path"])
        need(all(n >= 0 for n in local.values()), "positive remaining local ledger")
        child = Counter()
        for part in (local, Y, source_profile):
            for r, n in part.items():
                if r and n:
                    child[r] += 3 * n
        for s, z in word.gauge.items():
            if s not in word.donor:
                child[3 * z["dim"]] += 1
        child[2] += 2 * v
        physical_R = baseline["R"] - len(chosen)
        W = 2 * v + physical_R
        rank = sum(r * n for r, n in child.items())
        need(W * 3 * h - rank == baseline["deficit_per_vertex"],
             "terminal rank deficit unchanged")
        delta = Counter(child)
        delta.subtract(Counter({int(r): n for r, n in baseline["child_histogram"].items()}))
        expected = Counter()
        for e in chosen:
            expected[e["root_rank"]] -= 3
            expected[h - e["root_rank"]] -= 3
        need({k: n for k, n in delta.items() if n} == {k: n for k, n in expected.items() if n},
             "independent complete ledger agrees with exact terminal cancellation")
        row = dict(m=3 * h, W_per_vertex=W, deficit_per_vertex=baseline["deficit_per_vertex"],
                   rank_per_vertex=rank, maxchild=max(child),
                   child_histogram={int(k): n for k, n in child.items()},
                   terminal_sinks=len(chosen), R=physical_R,
                   active_virtual_R=baseline["R"] - len(chosen), reused_registers=len(word.pairs))
        cache[key] = row
        return row

    def try_profile(chosen):
        try:
            return profile_of(chosen), None
        except ValueError as exc:
            return None, str(exc)

    shipped_row_c = dict(W_per_vertex=shipped_row["W_per_vertex"],
                         deficit_per_vertex=shipped_row["deficit_per_vertex"],
                         rank_per_vertex=shipped_row["rank_per_vertex"],
                         maxchild=shipped_row["maxchild"],
                         child_histogram={int(k): n for k, n in shipped_row["child_histogram"].items()})
    cert_shipped = prove.certify(dict(shipped_row_c, m=shipped_row["m"]))
    rebuilt, err = try_profile(shipped)
    assert rebuilt and all(rebuilt[k] == val for k, val in shipped_row_c.items()), \
        f"rebuilt shipped profile mismatch: {err}"
    print(f"[self-check] shipped {len(shipped)} sinks -> W={rebuilt['W_per_vertex']} "
          f"rank={rebuilt['rank_per_vertex']} coarse={cert_shipped['coarse_saving']} "
          f"({float(cert_shipped['coarse_saving']):.15g}) "
          f"ordinary={cert_shipped['ordinary_saving']} "
          f"({float(cert_shipped['ordinary_saving']):.15g})", flush=True)
    base_coarse, base_ordinary = cert_shipped["coarse_saving"], cert_shipped["ordinary_saving"]

    # ---- extend the shipped family, validating every insertion --------------
    r23 = [c for c in cands if c["root_rank"] == 23]
    taken_targets = {t for c in shipped for t in c["targets"]}
    conflicts = [c for c in r23 if taken_targets & set(c["targets"])]
    free = [c for c in r23 if not taken_targets & set(c["targets"])]
    print(f"[extend] rank-23 candidates: {len(r23)} free={len(free)} "
          f"conflicting-with-shipped={len(conflicts)}", flush=True)

    def disjoint(family):
        seen = set()
        for c in family:
            if seen & set(c["targets"]):
                return False
            seen.update(c["targets"])
        return True

    lo, hi = 0, len(free)          # lo validates, hi is the failing bound
    row_lo, err_lo = try_profile(shipped)
    assert row_lo, err_lo
    row_hi, err_hi = try_profile(shipped + free)
    if row_hi:
        lo, hi = len(free), len(free)
        print(f"[extend] all {len(free)} free rank-23 sinks validated at once", flush=True)
    else:
        print(f"[extend] full extension rejected: {err_hi}", flush=True)
        while hi - lo > 1:
            mid = (lo + hi) // 2
            row_mid, err_mid = try_profile(shipped + free[:mid])
            if row_mid:
                lo = mid
            else:
                hi = mid
        print(f"[extend {time.monotonic()-t0:.1f}s] largest validating prefix: {lo} "
              f"(next rejected: {err_hi if hi == len(free) else err_mid})", flush=True)
    family = shipped + free[:lo]
    assert disjoint(family), "extension is not target-disjoint"

    # sweep any remaining free candidates with feedback (chronology is non-local)
    changed = True
    while changed:
        changed = False
        for c in free[lo:]:
            if c in family or not disjoint(family + [c]):
                continue
            row_c, _ = try_profile(family + [c])
            if row_c:
                family.append(c)
                changed = True
    print(f"[extend {time.monotonic()-t0:.1f}s] family after feedback sweep: "
          f"{len(family)} sinks ({len(family)-len(shipped)} added)", flush=True)

    row, err = try_profile(family)
    assert row, f"final family invalid: {err}"
    cert = prove.certify(row)
    print(f"[price] {len(family)} sinks coarse={cert['coarse_saving']} "
          f"({float(cert['coarse_saving']):.15g}) ordinary={cert['ordinary_saving']} "
          f"({float(cert['ordinary_saving']):.15g})", flush=True)
    print(f"[price] gain coarse={float(cert['coarse_saving']/base_coarse-1)*100:+.4f}% "
          f"ordinary={float(cert['ordinary_saving']/base_ordinary-1)*100:+.4f}%  "
          f"kappa {float(base_ordinary/(1+base_ordinary)):.12g} -> "
          f"{float(cert['ordinary_saving']/(1+cert['ordinary_saving'])):.12g}", flush=True)

    selected = [dict(root=c["root"], pivot=c["pivot"], targets=c["targets"],
                     role=c["role"], root_rank=c["root_rank"], writes=c["writes"]) for c in family]
    profile_out = dict(row, status="validated by bit/terminal.py::prove chronology and ledger checks",
                       shipped_sinks=len(shipped), added_sinks=len(family) - len(shipped))
    (a.out).write_text(json.dumps(dict(profile=profile_out, selected=selected,
                                       shipped_sinks=len(shipped), total_sinks=len(family),
                                       shipped_coarse=str(base_coarse),
                                       candidate_coarse=str(cert["coarse_saving"]),
                                       shipped_ordinary=str(base_ordinary),
                                       candidate_ordinary=str(cert["ordinary_saving"]),
                                       kappa_before=float(base_ordinary/(1+base_ordinary)),
                                       kappa_after=float(cert["ordinary_saving"]/(1+cert["ordinary_saving"])),
                                       seconds=time.monotonic() - t0), indent=1) + "\n")
    print(f"[write] {a.out}", flush=True)

    if a.pr184:
        pr184 = module("attack_pr184", a.pr184.resolve())
        b = pr184.select(pr184.normalize(row), True)
        b0 = pr184.select(pr184.normalize(shipped_row), True)
        print(f"[pr184] bit effective {float(b0['effective_saving']):.15g} -> "
              f"{float(b['effective_saving']):.15g} "
              f"({float(b['effective_saving']/b0['effective_saving']-1)*100:+.4f}%)", flush=True)


if __name__ == "__main__":
    main()
