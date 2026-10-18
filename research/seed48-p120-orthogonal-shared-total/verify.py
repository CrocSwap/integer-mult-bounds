#!/usr/bin/env python3
"""Exact P120 census for one orthogonal root-pencil shared-total decoder family."""
from fractions import Fraction
from hashlib import sha1, sha256
import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = "research/seed48-p120-orthogonal-shared-total"
MANIFEST = ROOT / PACKAGE / "SOURCES.json"
CERT = ROOT / PACKAGE / "vendor/seed51/certificate.tsv"
SEED = 48
PORTS = tuple(range(120))


def require(ok, message):
    if not ok:
        raise SystemExit("FAIL " + message)


def blob_id(data):
    return sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def verify_source_pins(manifest):
    for row in manifest["files"]:
        proc = subprocess.run(["git", "show", manifest["base_commit"] + ":" + row["path"]],
                              cwd=ROOT, check=True, capture_output=True)
        data = proc.stdout
        require(sha256(data).hexdigest() == row["sha256"], "base SHA-256 mismatch: " + row["path"])
        require(blob_id(data) == row["git_blob"], "base Git blob mismatch: " + row["path"])
    source = manifest["external_sources"][0]["files"][0]
    data = CERT.read_bytes()
    require(sha256(data).hexdigest() == source["sha256"], "vendored certificate SHA-256 mismatch")
    require(blob_id(data) == source["git_blob"], "vendored certificate Git blob mismatch")


def read_certificate(path):
    lines = path.read_text().splitlines()
    require(lines[:3] == [
        "# schema=1",
        "#! seed=51 track=structural-decoder ports=P120 e_index=51 d0_index=1",
        "#! columns=index root8_csv label9_bits",
    ], "predecessor certificate header changed")
    roots, labels = [], []
    for expected, line in enumerate(lines[3:]):
        index, root, label = line.split("\t")
        require(int(index) == expected and len(label) == 9 and set(label) <= {"0", "1"},
                "malformed root or label certificate row")
        roots.append(tuple(int(x) for x in root.split(",")))
        labels.append(int(label, 2))
    require(len(roots) == len(labels) == 120 and all(len(row) == 8 for row in roots),
            "wrong root/label dimensions")
    return roots, labels


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def parity_dot(a, b):
    return (a & b).bit_count() & 1


def validate_certificate(roots, labels):
    gram = [[dot(a, b) // 2 for b in roots] for a in roots]
    require(len(set(roots)) == 120, "duplicate root representatives")
    require(all(dot(a, a) == 4 for a in roots), "root norm is not four")
    require(all(dot(a, b) % 2 == 0 for a in roots for b in roots), "half-Gram is nonintegral")
    require(all(gram[i][i] == 2 for i in PORTS), "wrong Gram diagonal")
    require(all(gram[i][j] in (-1, 0, 1) for i in PORTS for j in PORTS if i != j),
            "unexpected off-diagonal Gram value")
    require(all(parity_dot(labels[i], labels[j]) == ((1 + gram[i][j]) & 1)
                for i in PORTS for j in PORTS), "root labels fail a Gram parity")
    require(all(0 <= x < 512 for x in labels), "label outside F2^9")
    return gram


def supports_by_word(labels):
    out = [0] * 512
    for word in range(1, 512):
        mask = 0
        for source, label in enumerate(labels):
            if parity_dot(word, label):
                mask |= 1 << source
        out[word] = mask
    return out


def enumerate_rows(ports, roots, labels, support, e_index, d_index):
    e, d0 = roots[e_index], roots[d_index]
    pe = {s: dot(roots[s], e) for s in ports}
    pd = {s: dot(roots[s], d0) for s in ports}
    nodes = []
    counts = {"label_eligible": 0, "unique_calibrator": 0, "calibrated": 0,
              "nonzero_diagonal": 0}
    port_mask = sum(1 << s for s in ports)
    for target in ports:
        for word in range(1, 512):
            z = support[word] & port_mask
            if not (z >> target & 1) or word == labels[target]:
                continue
            counts["label_eligible"] += 1
            ratios = {
                Fraction(-pd[s], pe[s])
                for s in ports if s != target and (z >> s & 1) and pe[s] != 0
            }
            if len(ratios) > 1:
                continue
            counts["unique_calibrator"] += 1
            if not ratios:
                continue
            counts["calibrated"] += 1
            mu = next(iter(ratios))
            if pd[target] + mu * pe[target] == 0:
                continue
            counts["nonzero_diagonal"] += 1
            correction = 0
            for s in ports:
                if s != target and (z >> s & 1) and pe[s] == 0 and pd[s] != 0:
                    correction |= 1 << s
            nodes.append({"target": target, "word": word, "mu": mu, "Z": z, "E": correction})
    return nodes, counts, pe, pd


def row_exact(target, mu, total, z, ports, pe, pd):
    for s in ports:
        coefficient = Fraction(pd[s]) + mu * pe[s] - (pd[s] if total >> s & 1 else 0)
        if s == target:
            if not (z >> s & 1) or coefficient == 0:
                return False
        elif (z >> s & 1) and coefficient != 0:
            return False
    return True


def pair_census(nodes, ports, pe, pd):
    raw = available = cross_a = cross_b = both = exact_pairs = 0
    no_cross = 0
    for i, a in enumerate(nodes):
        for b in nodes[i + 1:]:
            if a["target"] == b["target"]:
                continue
            raw += 1
            if a["E"] & ~b["Z"] or b["E"] & ~a["Z"]:
                continue
            available += 1
            a_hit = bool(b["E"] >> a["target"] & 1)
            b_hit = bool(a["E"] >> b["target"] & 1)
            cross_a += a_hit
            cross_b += b_hit
            both += a_hit and b_hit
            no_cross += not a_hit and not b_hit
            if a_hit:
                require(pe[a["target"]] == 0 and pd[a["target"]] != 0,
                        "first target is not a forced total cancellation")
                require(Fraction(pd[a["target"]]) + a["mu"] * pe[a["target"]]
                        - pd[a["target"]] == 0, "first contaminated diagonal did not vanish")
            if b_hit:
                require(pe[b["target"]] == 0 and pd[b["target"]] != 0,
                        "second target is not a forced total cancellation")
                require(Fraction(pd[b["target"]]) + b["mu"] * pe[b["target"]]
                        - pd[b["target"]] == 0, "second contaminated diagonal did not vanish")
            total = a["E"] | b["E"]
            exact_a = row_exact(a["target"], a["mu"], total, a["Z"], ports, pe, pd)
            exact_b = row_exact(b["target"], b["mu"], total, b["Z"], ports, pe, pd)
            exact_pairs += exact_a and exact_b
    return {"distinct_target_pairs": raw, "available_pairs": available,
            "first_target_contaminated": cross_a, "second_target_contaminated": cross_b,
            "both_targets_contaminated": both, "no_target_contaminated": no_cross,
            "exact_pairs": exact_pairs}


def full_unit_exact(ports, roots, labels, gram, a, b, total, pe, pd):
    for target in ports:
        word = a["word"] if target == a["target"] else b["word"] if target == b["target"] else labels[target]
        for source in ports:
            if target == a["target"]:
                coefficient = Fraction(pd[source]) + a["mu"] * pe[source] \
                    - (pd[source] if total >> source & 1 else 0)
            elif target == b["target"]:
                coefficient = Fraction(pd[source]) + b["mu"] * pe[source] \
                    - (pd[source] if total >> source & 1 else 0)
            else:
                coefficient = Fraction(gram[target][source], 2)
            paired = parity_dot(word, labels[source])
            if target == source:
                if not paired or coefficient == 0:
                    return False
            elif paired and coefficient != 0:
                return False
    return True


def first_exact_pair(ports, roots, labels, support, e_index, d_index):
    nodes, _, pe, pd = enumerate_rows(ports, roots, labels, support, e_index, d_index)
    for i, a in enumerate(nodes):
        for b in nodes[i + 1:]:
            if a["target"] == b["target"] or a["E"] & ~b["Z"] or b["E"] & ~a["Z"]:
                continue
            total = a["E"] | b["E"]
            if row_exact(a["target"], a["mu"], total, a["Z"], ports, pe, pd) \
                    and row_exact(b["target"], b["mu"], total, b["Z"], ports, pe, pd):
                return a, b, total, pe, pd
    return None, None, None, pe, pd


def main():
    manifest = json.loads(MANIFEST.read_text())
    verify_source_pins(manifest)
    roots, labels = read_certificate(CERT)
    gram = validate_certificate(roots, labels)
    support = supports_by_word(labels)
    print("PASS_SOURCE_AND_E8_CERTIFICATE: roots=120 labels=F2^9 pairings=14400")

    e_index = SEED
    orthogonal = [j for j in PORTS if j != e_index and dot(roots[e_index], roots[j]) == 0]
    d_index = orthogonal[SEED % len(orthogonal)]
    require(len(orthogonal) == 63 and d_index == 91 and dot(roots[e_index], roots[d_index]) == 0,
            "seed-selected orthogonal pencil changed")
    nodes, row_counts, pe, pd = enumerate_rows(PORTS, roots, labels, support, e_index, d_index)
    require(row_counts == {"label_eligible": 30600, "unique_calibrator": 190,
                           "calibrated": 190, "nonzero_diagonal": 65} and len(nodes) == 65,
            "orthogonal P120 row census changed: " + repr(row_counts))
    census = pair_census(nodes, PORTS, pe, pd)
    require(census == {"distinct_target_pairs": 2048, "available_pairs": 1056,
                       "first_target_contaminated": 1049, "second_target_contaminated": 1031,
                       "both_targets_contaminated": 1024, "no_target_contaminated": 0,
                       "exact_pairs": 0},
            "orthogonal P120 pair census changed: " + repr(census))
    print("P120_ORTHOGONAL: e=L48 d0=L91 <e,d0>=0 rows=" + repr(row_counts))
    print("P120_ORTHOGONAL_PAIRS: " + repr(census))

    # Regression control: independently reproduce the fixed odd-pair case from PR #1366.
    odd_nodes, odd_counts, odd_pe, odd_pd = enumerate_rows(PORTS, roots, labels, support, 51, 1)
    odd_census = pair_census(odd_nodes, PORTS, odd_pe, odd_pd)
    require(odd_counts == {"label_eligible": 30600, "unique_calibrator": 63,
                           "calibrated": 63, "nonzero_diagonal": 27} and len(odd_nodes) == 27,
            "PR #1366 regression row census changed")
    require(odd_census["distinct_target_pairs"] == 351 and odd_census["available_pairs"] == 351
            and odd_census["both_targets_contaminated"] == 351
            and odd_census["exact_pairs"] == 0,
            "PR #1366 regression pair result changed")

    # Positive control: published P112 C.6 exact two-target unit.
    p112 = tuple(range(8, 120))
    a, b, total, pe112, pd112 = first_exact_pair(p112, roots, labels, support, 0, 76)
    require(a is not None and b is not None, "P112 C.6 positive control not found")
    require((a["target"], a["word"], b["target"], b["word"], total.bit_count())
            == (75, 329, 76, 438, 24), "P112 C.6 witness changed")
    require(full_unit_exact(p112, roots, labels, gram, a, b, total, pe112, pd112),
            "P112 C.6 full 112-by-112 positive control failed")
    altered_total = total & ~(total & -total)
    require(not full_unit_exact(p112, roots, labels, gram, a, b, altered_total, pe112, pd112),
            "removing one required shared-total source escaped the negative control")

    # Certificate mutation control.
    bad_labels = labels[:]
    bad_labels[0] ^= 1
    require(any(parity_dot(bad_labels[0], labels[j]) != ((1 + gram[0][j]) & 1)
                for j in PORTS), "label mutation control failed")

    print("PASS_PR1366_REGRESSION: odd-pair nodes=27 available=351 both-diagonal obstruction=351")
    print("PASS_P112_C6_CONTROL: targets=75,76 sinks=329,438 total_sources=24 full_unit=112x112")
    print("PASS_NEGATIVE_CONTROLS: required-total-source removal and label mutation detected")
    print("PASS_P120_ORTHOGONAL_SHARED_TOTAL: no exact pair in the complete calibrated one-total family; no new kappa")


if __name__ == "__main__":
    main()
