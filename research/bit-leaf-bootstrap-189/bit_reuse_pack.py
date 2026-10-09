#!/usr/bin/env python3
"""Enlarge the bit word's donor-reuse pairing (the second W-lowering lever).

word.py::row() computes

    R = self.R - len(pairs);  W = 2*v + R;   deficit = W*m - mass  (asserted invariant)

so each extra donation pair lowers W by one at constant rank deficit and raises
the coarse saving a (kappa = a/(1+a)).  The bit side binds the current record,
so more pairs is a better record.

Eligibility, verbatim from word.py::__init__:
  b in gauge;  d not in gauge;  d not in rootroles;  d in last (a phase-2 operand);
  donor and recipient sets disjoint and one-to-one;
  last[d] < readtime[b];  C.sub(endframe[d], gauge[b].frame) and both endpoints
  nondegenerate;  no gate may use a role together with its donor.

This keeps the shipped pairing and greedily adds donors to unpaired gauges,
scarcest gauges first, then re-runs the frozen exact checks on the result.
"""
from pathlib import Path
from collections import Counter, defaultdict
from bisect import bisect_left
import argparse, importlib.util, json, sys, time

HERE = Path(__file__).resolve().parent


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--package", type=Path, required=True)
    ap.add_argument("--out", type=Path, default=HERE / "bit-reuse-pack.json")
    a = ap.parse_args()
    if hasattr(sys, "set_int_max_str_digits"):
        sys.set_int_max_str_digits(0)
    PKG = a.package.resolve()
    sys.path.insert(0, str(PKG / "bit"))
    sys.path.insert(0, str(PKG / "arithmetic"))
    bitword = module("reuse_bit_word", PKG / "bit" / "word.py")
    prove = module("reuse_bit_prove", PKG / "bit" / "prove.py")
    needle = bitword.need

    t0 = time.monotonic()
    word = bitword.Candidate()
    word.exact_frames()
    C = word.C
    baseline = word.row()
    shipped_pairs = [tuple(p) for p in word.pairs]
    print(f"[load {time.monotonic()-t0:.1f}s] R={word.R} v={word.v} h={word.h} "
          f"gauges={len(word.gauge)} pairs={len(word.pairs)} W={baseline['W_per_vertex']} "
          f"deficit={baseline['deficit_per_vertex']}", flush=True)

    used_together = defaultdict(set)
    for x, y, n in word.ops:
        used_together[x].add(y)
        used_together[y].add(x)

    pool = [s for s in range(word.R)
            if s not in word.gauge and s not in word.rootroles and s in word.last]
    donors_by_frame = defaultdict(list)
    for d in pool:
        donors_by_frame[word.endframe[d]].append(d)
    donor_last = {}
    for fd, ds in donors_by_frame.items():
        ds.sort(key=lambda d: word.last[d])
        donor_last[fd] = [word.last[d] for d in ds]
    gauges_by_frame = defaultdict(list)
    for b in word.gauge:
        gauges_by_frame[word.gauge[b]["frame"]].append(b)
    print(f"[pool {time.monotonic()-t0:.1f}s] donor pool={len(pool)} donor frames="
          f"{len(donors_by_frame)} gauge frames={len(gauges_by_frame)}", flush=True)

    contain = {}

    def frames_ok(fd, fb):
        if C.dimf[fd] > C.dimf[fb]:
            return False
        key = (fd, fb)
        v = contain.get(key)
        if v is None:
            v = contain[key] = bool(C.nondeg(fd) and C.nondeg(fb) and C.sub(fd, fb))
        return v

    contained = {}
    gauge_frame_list = sorted(gauges_by_frame, key=lambda fb: C.dimf[fb])
    for fb in gauge_frame_list:
        contained[fb] = [fd for fd in donors_by_frame if frames_ok(fd, fb)]
    print(f"[frames {time.monotonic()-t0:.1f}s] containment classes sized "
          f"(gauge frame -> #donor frames): "
          f"{sorted(Counter(len(v) for v in contained.values()).items())[:8]}", flush=True)

    def pick(b, used_donors, prefer_free_only=True):
        """First eligible donor for gauge b that is not already a donor."""
        rb = word.readtime[b]
        cands = []
        for fd in contained[word.gauge[b]["frame"]]:
            lasts = donor_last[fd]
            cut = bisect_left(lasts, rb)
            if cut == 0:
                continue
            cands.append((cut, fd))
        cands.sort()
        for cut, fd in cands:
            for d in donors_by_frame[fd][:cut]:
                if d in used_donors or b in used_together[d]:
                    continue
                return d
        return None

    # ---- keep the shipped pairing, then extend it ---------------------------
    pairs = list(shipped_pairs)
    recipients = {b for b, _ in pairs}
    used_donors = {d for _, d in pairs}
    unpaired = [b for b in word.gauge if b not in recipients]
    # scarcest gauges first: fewest contained donor frames, earliest readtime as tiebreak
    unpaired.sort(key=lambda b: (len(contained[word.gauge[b]["frame"]]), word.readtime[b]))
    added = 0
    for b in unpaired:
        if b in used_donors:
            continue
        d = pick(b, used_donors)
        if d is None:
            continue
        pairs.append((b, d))
        used_donors.add(d)
        added += 1
    print(f"[greedy {time.monotonic()-t0:.1f}s] pairs {len(shipped_pairs)} -> {len(pairs)} "
          f"(+{added}); unpaired gauges left: "
          f"{sum(1 for b in unpaired if b not in {x for x, _ in pairs})}", flush=True)

    if added == 0:
        print("[result] shipped pairing cannot be enlarged by this greedy pass")
        a.out.write_text(json.dumps(dict(shipped_pairs=len(shipped_pairs),
                                         maximum_found=len(pairs), added=0,
                                         seconds=time.monotonic() - t0), indent=1) + "\n")
        return

    # ---- rebuild the word and re-run the frozen exact checks ----------------
    needle(len({b for b, _ in pairs}) == len(pairs) == len({d for _, d in pairs}),
           "one-to-one aliases")
    needle(not ({b for b, _ in pairs} & {d for _, d in pairs}), "disjoint donor and recipient sets")
    for b, d in pairs:
        needle(d not in word.gauge and d not in word.rootroles and b in word.gauge,
               "ungauged non-root donor and gauged recipient")
        needle(word.last[d] < word.readtime[b], "donor dead before recipient read")
    word.pairs = [[b, d] for b, d in pairs]
    word.donor = dict(word.pairs)
    word.phys = {s: word.donor.get(s, s) for s in range(word.R)}
    needle(len(set(word.phys.values())) == word.R - len(word.pairs), "physical slot count")
    needle(all(word.phys[x] != word.phys[y] for x, y, _ in word.ops), "distinct physical gate ports")
    word.exact_frames()
    row = word.row()
    row_c = dict(row, child_histogram={int(k): n for k, n in row["child_histogram"].items()})
    base_c = dict(baseline, child_histogram={int(k): n for k, n in baseline["child_histogram"].items()})
    cert, base = prove.certify(row_c), prove.certify(base_c)
    print(f"[price] W={row['W_per_vertex']} (was {baseline['W_per_vertex']}) "
          f"mass={row['rank_per_vertex']} deficit={row['deficit_per_vertex']}", flush=True)
    print(f"[price] coarse {float(base['coarse_saving']):.15g} -> "
          f"{float(cert['coarse_saving']):.15g} "
          f"({float(cert['coarse_saving']/base['coarse_saving']-1)*100:+.4f}%)", flush=True)
    print(f"[price] ordinary {float(base['ordinary_saving']):.15g} -> "
          f"{float(cert['ordinary_saving']):.15g} "
          f"({float(cert['ordinary_saving']/base['ordinary_saving']-1)*100:+.4f}%)", flush=True)
    print(f"[price] kappa {float(base['ordinary_saving']/(1+base['ordinary_saving'])):.12g} -> "
          f"{float(cert['ordinary_saving']/(1+cert['ordinary_saving'])):.12g}", flush=True)
    a.out.write_text(json.dumps(dict(
        shipped_pairs=len(shipped_pairs), new_pairs=len(pairs), added=added,
        pairs=[[b, d] for b, d in pairs],
        W_before=baseline["W_per_vertex"], W_after=row["W_per_vertex"],
        deficit=row["deficit_per_vertex"],
        coarse_before=str(base["coarse_saving"]), coarse_after=str(cert["coarse_saving"]),
        ordinary_before=str(base["ordinary_saving"]), ordinary_after=str(cert["ordinary_saving"]),
        profile=dict(row, child_histogram={str(k): n for k, n in row["child_histogram"].items()}),
        seconds=time.monotonic() - t0), indent=1) + "\n")
    print(f"[write] {a.out}", flush=True)


if __name__ == "__main__":
    main()
