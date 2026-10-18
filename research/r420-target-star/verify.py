#!/usr/bin/env python3
"""Exact R420 target-star experiment. @ellipsi2 with OpenAI Codex; Apache-2.0.

Only the Python standard library is required. No producer or optimizer is used.
The inherited xcheck and record exporter are source-pinned and reused explicitly.
"""
import argparse
from collections import Counter
import copy
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = "research/e8-bit-r420/data/bitE8mut-r420.json.gz"
XCHECK = "research/e8-bit-r420/code/xcheck.py"
EXPORT = "research/e8-bit-carrier-skeleton/code/bit/export_records.py"
DONOR = 120  # assignment seed 0 fixes the first donor target to 0
DONOR_LIMIT = 16  # fixed before the bounded extension was run


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def check_pins():
    source = json.loads((HERE / "SOURCES.json").read_text())
    for path, pin in source["files"].items():
        data = (ROOT / path).read_bytes()
        need(hashlib.sha256(data).hexdigest() == pin["sha256"], "source pin: " + path)
        blob = hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()
        need(blob == pin["git_blob"], "source blob: " + path)
    return source


def synthesize(word):
    """Bounded donor-set nomination; exact best assignment for each donor set.

    Donors and receivers are disjoint, but one donor may serve many receivers.
    Starting with target 0, add the best strict-improvement donor up to 16 total.
    Smaller register IDs break all ties. No global donor-set optimum is claimed.
    """
    rows = {d: set(s) for f, d, s in word["D"]}
    zero = word["frames"].index([])
    need(len(rows) == 120 and set(rows) == set(range(120, 240)), "baseline D shape")
    need(all(f == zero and len(s) == len(set(s)) and all(240 <= a < 660 for a in s)
             for f, d, s in word["D"]), "baseline D is not helper-only")
    gains = {(i, d): len(rows[i])-len(rows[i] ^ rows[d])-2
             for i in rows for d in rows if i != d}

    def assignment(donors):
        census = []
        for target in sorted(rows.keys() - donors):
            donor = max(donors, key=lambda d: (gains[target, d], -d))
            census.append(dict(target=target, donor=donor, old_terms=len(rows[target]),
                               new_terms=len(rows[target] ^ rows[donor]), net_saved=gains[target, donor]))
        return sum(max(0, r["net_saved"]) for r in census), census

    donors, trace = {DONOR}, []
    while True:
        saving, census = assignment(donors)
        step = dict(donors=sorted(donors), saved_additions=saving,
                    receivers=sum(r["net_saved"] > 0 for r in census))
        trace.append(step)
        if len(donors) == DONOR_LIMIT:
            break
        candidates = [[d, assignment(donors | {d})[0]] for d in sorted(rows.keys()-donors)]
        step["candidate_scores"] = candidates
        donor, next_score = max(candidates, key=lambda p: (p[1], -p[0]))
        if next_score <= saving:
            break
        donors.add(donor)
    selected = [r["target"] for r in census if r["net_saved"] > 0]
    by = {r["target"]: r["donor"] for r in census if r["net_saved"] > 0}
    need(not (donors & set(selected)), "donor/receiver overlap")
    result = copy.deepcopy(word)
    setup = [[zero, target, [by[target]]] for target in selected]
    middle = [[zero, d, sorted(rows[d] ^ rows[by[d]] if d in selected else rows[d])]
              for _, d, _ in word["D"]]
    need(all(s for _, _, s in middle), "empty compensation row")
    result["D"] = setup + middle + list(reversed(setup))
    search = dict(donors=sorted(donors), donor_limit=DONOR_LIMIT, trace=trace,
                  oriented_pair_scores=len(gains), candidate_donor_sets=sum(
                      len(s.get("candidate_scores", [])) for s in trace),
                  stopping_rule="16 donors or no strictly profitable donor addition",
                  gains_sha256=digest([[i, d, gains[i, d]] for i, d in sorted(gains)]))
    return result, census, selected, search


def xor_replay(word, sections=("D", "A", "scatter", "B", "C"), zero_targets=False):
    """Own integer-bitset interpreter; every live input is an independent column."""
    n, v = 2 * word["v"] + word["R"], word["v"]
    values = [0 if zero_targets and v <= i < 2*v else 1 << i for i in range(n)]
    for section in sections:
        if section == "scatter":
            copied = [values[r] for r in word["ret"]]
            for t, row in enumerate(word["scatter"]):
                for k in row:
                    values[v+t] ^= copied[k]
        else:
            for _, d, sources in word[section]:
                for s in sources:
                    values[d] ^= values[s]
    return values


def endpoint(word, zero_targets=False):
    want = [1 << i for i in range(660)]
    for t in range(120):
        want[120+t] = (0 if zero_targets else 1 << (120+t)) ^ (1 << t)
    return xor_replay(word, zero_targets=zero_targets) == want


def export(word, directory):
    path = directory / "word.json.gz"
    path.write_bytes(gzip.compress(canonical(word), mtime=0))
    subprocess.run([sys.executable, "-I", "-B", str(ROOT / EXPORT), str(path), str(directory)],
                   check=True, capture_output=True, text=True)
    data = (directory / "249-records.bin").read_bytes()
    need(len(data) % 24 == 0, "record alignment")
    return list(struct.iter_unpack("<6i", data))


def audit_records(records, word, W):
    """Separate set-valued execution of the actual exported stream, both ways.

    Checks every geometry move, live COPY lifetime, arbitrary dirty input,
    scalar cost and exact positive row-sum bound. No word-level gate interpreter
    is called here. Reverse COPY/ERASE use the original immutable center.
    """
    n, v = 660, 120
    cur = list(word["start"]) + [W.ZERO]
    paths = [[] for _ in range(n)]
    H = Counter()
    counts = Counter()
    values = [{r} for r in range(n)] + [set()]
    center = None
    for op, a, b, c, f, phase in records:
        need(0 <= a <= n and (op == 0 or 0 <= b <= n), "record register")
        if op == 0:
            need(a < n and 0 <= b < len(W.fdim) and 0 <= c < len(W.fdim), "MOVE indices")
            need(cur[a] == b and W.nested(b, c), "illegal MOVE")
            need(f == W.fdim[c] - W.fdim[b] and f > 0, "mispriced MOVE")
            paths[a].append([b, c, f])
            H[f] += 1
            cur[a] = c
        elif op == 1:
            need(a != b and a < n and c == 1, "ADD operands")
            need(cur[a] == cur[b] == f, "ADD common frame")
            need(b != n or center is not None, "read inactive copy")
            need(a != center, "write copied center")
            values[a] ^= values[b]
        elif op == 2:
            need(center is None and b == n and cur[a] == c and f == W.ZERO,
                 "COPY lifecycle")
            need(phase == W.fdim[c], "COPY price")
            center = a
            values[n] = set(values[a])
            cur[n] = f
            H[phase] += 1
        elif op == 3:
            need(center == a and b == n and cur[a] == c and cur[n] == f,
                 "ERASE lifecycle")
            need(values[n] == values[a], "copied value mutated")
            values[n] = set()
            center = None
        else:
            raise ValueError("unknown opcode")
        counts[op] += 1
    want = [{r} for r in range(n)] + [set()]
    for t in range(v):
        want[v+t].add(t)
    need(values == want and center is None, "exported forward endpoint")
    need(cur[:n] == word["final"], "exported final frames")
    need(counts[2] == counts[3] == 9, "COPY count")

    values = [{r} for r in range(n)] + [set()]
    center = None
    for op, a, b, c, f, phase in reversed(records):
        if op == 1:
            need(a != center and (b != n or center is not None), "reverse copy access")
            values[a] ^= values[b]
        elif op == 3:
            need(center is None, "reverse COPY overlap")
            center = a
            values[n] = set(values[a])
        elif op == 2:
            need(center == a and values[n] == values[a], "reverse ERASE")
            values[n] = set()
            center = None
    need(values == want and center is None, "exported inverse endpoint")

    maxima = []
    for reverse in (False, True):
        norms, high = [1] * (n+1), 1
        opened = False
        for op, a, b, c, f, phase in (reversed(records) if reverse else records):
            if op == 1:
                norms[a] += abs(c) * norms[b]
                high = max(high, norms[a])
            elif op == (3 if reverse else 2):
                need(not opened, "norm COPY overlap")
                norms[n] = norms[a]
                opened = True
            elif op == (2 if reverse else 3):
                need(opened, "norm ERASE without COPY")
                norms[n] = 0
                opened = False
        need(not opened, "norm COPY closure")
        maxima.append(high)
    payload = 64 * maxima[0]**3 * maxima[1]**2
    need(payload < 2**104, "native payload exceeds inherited 104-bit cap")
    return dict(records=len(records), scalar_additions=counts[1], copies=counts[2],
                moves=counts[0], local_histogram=dict(sorted(H.items())),
                rank_mass=sum(k*v for k, v in H.items()),
                frame_paths_sha256=digest(paths), forward_positive_bound=maxima[0],
                inverse_positive_bound=maxima[1], payload_upper=payload,
                payload_bits=payload.bit_length())


def bridge_replay(records, pairs, omit=None):
    """Fresh literal replay on 2*pairs target/source banks and shared dirty helpers.

    Stage/bridge schedule is DaysSky's B_K schedule (PR381), explicitly credited.
    This is a Python replay, not a claim to have run its C++ implementation.
    Each omitted-bridge control replays the entire actual record stream.
    """
    v, n = 120, 660
    total = 2*pairs*v + 420
    values = [1 << r for r in range(total)] + [0]
    stages = 2*pairs+1
    after = [[] for _ in range(stages)]
    X, Y = lambda p: 2*(p-1), lambda p: 2*(p-1)+1
    for p in range(2, pairs+1):
        after[2*p-3] += [(X(p-1), X(p)), (Y(p), Y(p-1))]
        after[2*p-2] += [(Y(p), Y(p-1)), (X(p-1), X(p))]
    for p in range(pairs, 1, -1):
        after[-1] += [(Y(p-1), Y(p)), (X(p), X(p-1))]
    bridge_index = 0
    for stage in range(stages):
        p = 1 if stage < 3 else (stage+1)//2
        reverse = stage == 1 or (stage >= 3 and stage % 2 == 1)
        xb, yb = (Y(p), X(p)) if reverse else (X(p), Y(p))
        mapping = ([xb*v+i for i in range(v)] + [yb*v+i for i in range(v)]
                   + [2*pairs*v+i for i in range(420)] + [total])
        opened = False
        copies = 0
        for op, a, b, c, f, phase in (reversed(records) if reverse else records):
            if op == 1:
                values[mapping[a]] ^= values[mapping[b]]
            elif op == (3 if reverse else 2):
                need(not opened, "bridge COPY overlap")
                values[total] = values[mapping[a]]
                opened = True
                copies += 1
            elif op == (2 if reverse else 3):
                need(opened, "bridge ERASE")
                values[total] = 0
                opened = False
        need(not opened and copies == 9, "stage copy lifecycle")
        for d, s in after[stage]:
            if bridge_index != omit:
                for t in range(v):
                    values[d*v+t] ^= values[s*v+t]
            bridge_index += 1
    for bank in range(0, 2*pairs, 2):
        a, b = bank*v, (bank+1)*v
        values[a:a+v], values[b:b+v] = values[b:b+v], values[a:a+v]
    need(bridge_index == 6*(pairs-1), "bridge count")
    return values == [1 << r for r in range(total)] + [0]


def controls(base, candidate, selected, W, records):
    """Failure-mode controls, checked without comparing a recipe hash."""
    passed = []
    # Crucial dirty-target control: deleting setup is invisible if targets start zero.
    mutant = copy.deepcopy(candidate)
    del mutant["D"][0]
    need(endpoint(mutant, zero_targets=True), "zero-target control was not blind")
    need(not endpoint(mutant), "missing preparation accepted on arbitrary targets")
    passed.append("missing_setup_passes_zero_targets_but_fails_arbitrary_targets")
    mutant = copy.deepcopy(candidate)
    del mutant["D"][-1]
    need(not endpoint(mutant), "missing restoration accepted")
    passed.append("missing_target_restoration")
    mutant = copy.deepcopy(candidate)
    ix = len(selected) + next(i for i, g in enumerate(base["D"]) if g[1] == selected[0])
    mutant["D"][ix] = copy.deepcopy(next(g for g in base["D"] if g[1] == selected[0]))
    need(not endpoint(mutant), "untransformed compensation accepted")
    passed.append("untransformed_receiver_compensation")
    mutant = copy.deepcopy(candidate)
    mutant["D"] = [g for g in mutant["D"] if g[1] != DONOR]
    need(not endpoint(mutant), "missing donor compensation accepted")
    passed.append("missing_donor_compensation")
    mutant = copy.deepcopy(candidate)
    mutant["D"][ix][2].pop()
    need(not endpoint(mutant), "missing source-access term accepted")
    passed.append("missing_helper_read")
    # A donor already changed by an earlier setup creates an extra dependency.
    # Merely XORing its original K row then omits that dependency's correction.
    mutant = copy.deepcopy(candidate)
    earlier, later = selected[:2]
    mutant["D"][1][2] = [earlier]
    mutant["D"][-2][2] = [earlier]
    rows = {d: set(s) for _, d, s in base["D"]}
    position = len(selected) + next(i for i, g in enumerate(base["D"]) if g[1] == later)
    mutant["D"][position][2] = sorted(rows[later] ^ rows[earlier])
    need(not endpoint(mutant), "already-modified receiver admitted as a star donor")
    passed.append("donor_is_an_already_modified_receiver")
    # Geometry-only failure: scalar semantics still pass at the wrong common frame.
    mutant = copy.deepcopy(candidate)
    mutant["D"][0][0] = W.FULL
    need(endpoint(mutant), "frame-only mutant changed scalar endpoint")
    old = W.w
    W.w = mutant
    try:
        try:
            W.full()
        except Exception as error:
            need("climb not nested" in str(error) or "left frame 0" in str(error),
                 "unexpected frame control failure: " + str(error))
        else:
            raise ValueError("illegal frame accepted")
    finally:
        W.w = old
    passed.append("scalar_valid_illegal_frame")
    mutant = copy.deepcopy(candidate)
    pair = copy.deepcopy(candidate["D"][0])
    mutant["D"] = [pair, copy.deepcopy(pair)] + mutant["D"]
    need(endpoint(mutant), "neutral pair should preserve F2 semantics")
    with tempfile.TemporaryDirectory(prefix="r420-neutral-control-") as name:
        neutral_records = export(mutant, Path(name))
        paid = audit_records(neutral_records, mutant, W)
    need(paid["scalar_additions"] == sum(r[0] == 1 for r in records)+2,
         "exported neutral pair not paid")
    passed.append("scalar_valid_neutral_pair_pays_two_additions")
    # Drop one actual exported preparation ADD, independently of word parsing.
    damaged = list(records)
    del damaged[next(i for i, r in enumerate(damaged) if r[0] == 1)]
    need(not bridge_replay(damaged, 4), "missing exported ADD accepted")
    passed.append("missing_exported_preparation_add")
    return passed


def run():
    source = check_pins()
    base = json.loads(gzip.decompress((ROOT / WORD).read_bytes()))
    candidate, census, selected, search = synthesize(base)
    # Independent incidence-count identity for every receiver's cost, including
    # losers and ties. No symmetric-difference operation is used in this check.
    row_bits = {d: sum(1 << s for s in sources) for _, d, sources in base["D"]}
    weight = lambda bits: bin(bits).count("1")
    independent_gains = []
    for i in range(120, 240):
        for d in range(120, 240):
            if i != d:
                saving = 2*weight(row_bits[i] & row_bits[d])-weight(row_bits[d])-2
                independent_gains.append([i, d, saving])
    need(digest(independent_gains) == search["gains_sha256"], "independent incidence cost mismatch")
    need(all(candidate[k] == base[k] for k in base if k != "D"), "changed field outside D")
    need(xor_replay(base, ("D",)) == xor_replay(candidate, ("D",)), "D operator changed")
    need(endpoint(base) and endpoint(candidate), "word endpoint")
    spec = importlib.util.spec_from_file_location("pinned_r420_xcheck", ROOT / XCHECK)
    inherited = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(inherited)
    W0, labels, full0, H0, C0, _ = inherited.check(base)
    need(all(H0.values()) and all(C0.values()), "baseline interface")
    W = inherited.Word(candidate)
    full = W.full()
    H, C, _ = W.interface()
    need([k for k, v in H.items() if not v] == ["H2_D_frame0_targets_from_helpers"],
         "unexpected inherited hypothesis change")
    need([k for k, v in C.items() if not v] == ["K_equals_D"], "unexpected literal K result")
    need(all(f == W.ZERO and 120 <= d < 240 and all(120 <= s < 660 for s in srcs)
             for f, d, srcs in candidate["D"]), "replacement D frame/operand condition")
    with tempfile.TemporaryDirectory(prefix="r420-target-star-") as name:
        tmp = Path(name)
        (tmp / "baseline").mkdir()
        (tmp / "candidate").mkdir()
        original_records = export(base, tmp / "baseline")
        records = export(candidate, tmp / "candidate")
        original = audit_records(original_records, base, W0)
        changed = audit_records(records, candidate, W)
        need([r for r in records if r[0] != 1] == [r for r in original_records if r[0] != 1],
             "MOVE/COPY/ERASE stream changed")
        need([r for r in records if r[0] == 1 and r[5] != 1]
             == [r for r in original_records if r[0] == 1 and r[5] != 1], "non-D ADD stream changed")
        need(original["frame_paths_sha256"] == changed["frame_paths_sha256"], "paths changed")
        bridge_results = []
        for pairs in (2, 4, 5):
            need(bridge_replay(original_records, pairs), "baseline multistage failure")
            need(bridge_replay(records, pairs), "candidate multistage failure")
            for omitted in range(6*(pairs-1)):
                need(not bridge_replay(records, pairs, omitted), "omitted bridge accepted")
            bridge_results.append(dict(stages=2*pairs+1, columns=2*pairs*120+420,
                                       actual_stream_omission_controls=6*(pairs-1)))
        rejected = controls(base, candidate, selected, W, records)
    savings = sum(r["net_saved"] for r in census if r["net_saved"] > 0)
    need(original["scalar_additions"] - changed["scalar_additions"] == savings, "net cost mismatch")
    return candidate, dict(status="PASS_R420_TARGET_STAR", assignment_seed=0, initial_donor=DONOR,
        base_commit=source["base_commit"], candidate_content_sha256=digest(candidate),
        source_manifest_sha256=digest(source), selected_targets=selected, census=census,
        search=search, receivers=len(selected), saved_additions=savings,
        donor_degrees=dict(sorted(Counter(r["donor"] for r in census if r["net_saved"] > 0).items())),
        preparation_additions=len(selected), restoration_additions=len(selected),
        baseline_D_additions=sum(len(g[2]) for g in base["D"]),
        candidate_D_additions=sum(len(g[2]) for g in candidate["D"]),
        original=original, candidate=changed, inherited_labels=labels,
        symbolic_columns=full["columns"], inherited_hypotheses=H, inherited_conclusions=C,
        replacement_D_operator="exactly the baseline y <- y + K*s; x,s unchanged",
        multistage_python_replays=bridge_results, controls=rejected,
        scope="Finite bit-circuit construction; no new kappa, no full theorem or global optimum.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", type=Path, default=HERE / "CERTIFICATE.json")
    parser.add_argument("--write-certificate", type=Path)
    parser.add_argument("--write-word", type=Path)
    args = parser.parse_args()
    word, result = run()
    if args.write_certificate:
        need(not args.write_certificate.exists(), "refusing to overwrite certificate")
        write_json(args.write_certificate, result)
    else:
        need(json.loads(args.check.read_text()) == json.loads(json.dumps(result)), "certificate mismatch")
    if args.write_word:
        need(not args.write_word.exists(), "refusing to overwrite word")
        args.write_word.write_bytes(gzip.compress(canonical(word), mtime=0))
    print("PASS_R420_TARGET_STAR receivers=%d D=%d->%d native_ADDs=%d->%d saved=%d columns=660 rank_mass=%d"
          % (result["receivers"], result["baseline_D_additions"], result["candidate_D_additions"],
             result["original"]["scalar_additions"], result["candidate"]["scalar_additions"],
             result["saved_additions"], result["candidate"]["rank_mass"]))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print("REJECT_R420_TARGET_STAR:", error, file=sys.stderr)
        sys.exit(1)
