#!/usr/bin/env python3
"""Independent exact frame-walk audit, not a restored circuit or decoder.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
Geometry: DreamingOfClouds #6030. Audited theorem: Matarener #6315.
No predecessor executable is imported or executed.
"""
import argparse
import gzip
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = "research/p104-helper470-twin-rung-removal/WORD.json.gz"
PREDECESSOR_SHA256 = "10fe4a63096ea0e0e5b71322061f2903ad02f117fef44fda0b17fbfa6e334faf"


class Rejected(ValueError):
    pass


def need(condition, message):
    if not condition:
        raise Rejected(message)


def dot(x, y):
    return (x & y).bit_count() % 2


def space(vectors):
    values = {0}
    for vector in vectors:
        values.update(x ^ vector for x in tuple(values))
    return frozenset(values)


def dim(s):
    size = len(s)
    need(size > 0 and size & (size - 1) == 0, "non-subspace cardinality")
    return size.bit_length() - 1


def join(*spaces):
    return space(itertools.chain.from_iterable(spaces))


def walk(nodes, root, claimed=None):
    need(bool(nodes) and nodes[0] == root, "wrong source root")
    paid = 0
    for a, b in zip(nodes, nodes[1:]):
        if b <= a:
            continue
        need(a <= b, "nonnested step")
        paid += dim(b) - dim(a)
    if claimed is not None:
        need(type(claimed) is int and paid == claimed, "wrong paid amount")
    union = join(*nodes)
    need(dim(union) <= dim(root) + paid, "walk union bound")
    return paid, union


def check_model(carriers, selected, hG=False, htop=False, base=7, grow=True, merge_vector=0):
    zero, full = frozenset({0}), frozenset(range(512))
    W = space([merge_vector])
    G = space(carriers[c]["g"] for c in selected)
    paths, costs = [], []
    for c in selected:
        item = carriers[c]
        root = space([item["g"]])
        nodes = [root, item["H"], W] if grow else [root, W]
        paid, Z = walk(nodes, root)
        need(all(any(p in node for node in nodes) for p in item["receivers"]), "receiver coverage")
        need(nodes[-1] == W, "common merge")
        paths.append(Z)
        costs.append(paid)
    T = W
    tail = 0
    need(all(W <= Z and W <= T for Z in paths), "merge inclusion")
    if hG:
        need(G <= W, "hG fails")
    if htop:
        need(all(join(Z, T) == full for Z in paths), "htop fails")
    eta = []
    for c, Z, paid in zip(selected, paths, costs):
        H = carriers[c]["H"]
        U = join(Z, T)
        need(H <= U, "H coverage")
        e = int(not U <= H)
        need(dim(U) == 8 + e, "eta dimension")
        need(paid + tail >= base + e, "repaired individual inequality")
        eta.append(e)
    k = len(selected)
    total = sum(costs) + tail
    need(total + (k - 1) * tail >= base * k + sum(eta), "repaired sum")
    return {"k": k, "total": total, "tail": tail, "eta": eta,
            "path_dimensions": [dim(Z) for Z in paths],
            "hG": G <= W, "htop": [join(Z, T) == full for Z in paths]}


def all_subspaces(n):
    """Closure enumeration, independent of the predecessor RREF generator."""
    found = {frozenset({0})}
    todo = list(found)
    while todo:
        s = todo.pop()
        for v in range(1, 1 << n):
            if v not in s:
                enlarged = s | frozenset(x ^ v for x in s)
                if enlarged not in found:
                    found.add(enlarged)
                    todo.append(enlarged)
    return sorted(found, key=lambda s: (len(s), sorted(s)))


def tiny_check():
    subs = all_subspaces(3)
    need(len(subs) == 16, "tiny lattice size")
    counts = [0, 0]
    for H in subs:
        if dim(H) != 2:
            continue
        for g in H - {0}:
            for Z in subs:
                if g not in Z:
                    continue
                for T in subs:
                    if not H <= Z | T:
                        continue
                    U = join(Z, T)
                    eta = int(not U <= H)
                    need(dim(U) == 2 + eta, "tiny eta")
                    for W in subs:
                        if W <= Z & T:
                            need(dim(Z) - 1 + dim(T) - dim(W) >= 1 + eta, "tiny repaired inequality")
                            counts[eta] += 1
    return {"ambient_dimension": 3, "subspaces": len(subs), "eta_counts": counts,
            "admissible_tuples": sum(counts)}


def authenticate():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    pins = {}
    retained_raw = (HERE / "PREDECESSOR.json").read_bytes()
    need(hashlib.sha256(retained_raw).hexdigest() == PREDECESSOR_SHA256,
         "predecessor manifest pin")
    retained = json.loads(retained_raw)
    rows = [row for row in manifest["files"] if row["usage"] == "input"]
    rows += [dict(row, path=row["retained_path"]) for row in retained["files"]]
    for row in rows:
        raw = (ROOT / row["path"]).read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        need(digest == row["sha256"], "source SHA256 " + row["path"])
        blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        need(blob == row["git_blob"], "source Git blob " + row["path"])
        pins[row["path"]] = digest
    return pins


def result():
    pins = authenticate()
    word = json.loads(gzip.decompress((ROOT / WORD).read_bytes()))
    previous = json.loads((HERE / "inputs/pr6315-RESULT.json").read_text())
    ports = word["ports"]
    need(len(ports) == len(set(ports)) == 104, "selected ports")
    need(all(dot(p, p) == 1 for p in ports), "odd selected ports")
    lines = previous["carriers"]["lines"]
    normals = previous["carriers"]["normals_g"]
    need(len(lines) == len(normals) == 8, "eight carriers")
    carriers = []
    for c, (line, g) in enumerate(zip(lines, normals)):
        need(line not in ports and 0 < line < 512 and 0 < g < 512, "carrier labels")
        H = frozenset(p for p in range(512) if dot(p, line) == 0)
        receivers = [p for p in ports if dot(p, line) == 0]
        need(len(receivers) == 52 and dim(H) == 8, "receiver geometry")
        need(join(space([g]), space(receivers)) == H, "H equals root plus receivers")
        need(all(dot(normals[a], line) == int(a != c) for a in range(8)), "cross normal")
        carriers.append({"g": g, "H": H, "receivers": receivers})
    need(dim(space(normals)) == 8, "independent normals")
    summaries = []
    subsets = 0
    for k in range(2, 9):
        count = 0
        for selected in itertools.combinations(range(8), k):
            row = check_model(carriers, selected)
            need(row["total"] == 7 * k and row["eta"] == [0] * k, "countermodel price")
            need(not row["hG"] and row["htop"] == [False] * k, "missing premise")
            count += 1
        subsets += count
        summaries.append({"k": k, "subsets": count, "paid": 7 * k,
                          "eta_sum": 0, "missing_htop": k})
    need(subsets == 247, "subset coverage")
    nonzero = []
    for selected in [(0, 1), (0, 1, 2)]:
        common = sorted(set.intersection(*(set(carriers[c]["receivers"]) for c in selected)))
        need(common and common[0] == 11, "nonzero common selected port")
        row = check_model(carriers, selected, merge_vector=11)
        need(not row["hG"] and not any(row["htop"]), "nonzero missing premises")
        j = ports.index(11)
        receiver = word["live"][j] + 112
        frame = word["final"][receiver]
        primal = space(word["frames"][frame])
        need(primal == frozenset(x for x in range(512) if dot(x, 11) == 0), "actual endpoint chart")
        need(dim(space(word["frames"][word["initial"][receiver]])) == 0, "actual receiver starts at zero")
        need(all(lines[c] in primal for c in selected), "line-to-endpoint ascent")
        nonzero.append({"carrier_subset": list(selected), "merge_dual_generator": 11,
                        "selected_receiver_register": receiver, "merge_primal_frame": frame,
                        "common_receiver_count": len(common), "total": row["total"],
                        "path_dimensions": row["path_dimensions"], "eta": row["eta"]})
    full = frozenset(range(512))
    positive = []
    for k in range(2, 9):
        W = space(normals[:k])
        prefix = sum(walk([space([g]), W], space([g]))[0] for g in normals[:k])
        tail, T = walk([W, full], W)
        need(join(W, T) == full, "source-preserving htop")
        total = prefix + tail
        need(total + (k - 1) * tail == 8 * k, "source-preserving equality")
        positive.append({"k": k, "prefix_paid": prefix, "tail_paid": tail,
                         "total": total, "eta_sum": k})
    zero, root0, root1 = frozenset({0}), space([normals[0]]), space([normals[1]])
    H0 = carriers[0]["H"]
    controls = [
        ("underpriced growth", lambda: walk([root0, H0, zero], root0, 6)),
        ("missing source root", lambda: walk([zero, H0, zero], root0)),
        ("nonnested step", lambda: walk([root0, root1], root0)),
        ("omitted growth", lambda: check_model(carriers, (0, 1), grow=False)),
        ("pair false hG", lambda: check_model(carriers, (0, 1), hG=True)),
        ("pair false htop", lambda: check_model(carriers, (0, 1), htop=True)),
        ("triple false hG", lambda: check_model(carriers, (0, 1, 2), hG=True)),
        ("triple false htop", lambda: check_model(carriers, (0, 1, 2), htop=True)),
        ("unjustified 8k", lambda: check_model(carriers, (0, 1), base=8)),
        ("invalid merge line", lambda: check_model(carriers, (0, 1), merge_vector=normals[1])),
        ("boolean paid value", lambda: walk([root0, H0, zero], root0, True)),
    ]
    for label, action in controls:
        try:
            action()
        except Rejected:
            continue
        raise Rejected("negative control accepted: " + label)
    return {"schema": "carrier-merge-relay-premise-v1", "source_sha256": pins,
            "geometry": {"ports": 104, "carrier_lines": lines, "source_normals": normals,
                         "receivers_each": 52, "H_dimensions": [8] * 8},
            "countermodels": summaries, "countermodel_subsets": subsets,
            "nonzero_merge_examples": nonzero,
            "source_preserving_controls": positive, "small_lattice": tiny_check(),
            "negative_controls": [x[0] for x in controls],
            "scope": "abstract dual-frame walks; no scalar decoder or dirty restoration verified",
            "new_kappa": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="write evidence to a new external file")
    args = parser.parse_args()
    actual = result()
    serialized = json.dumps(actual, indent=2, sort_keys=True) + "\n"
    if args.output:
        destination = args.output.resolve()
        need(destination != ROOT and ROOT not in destination.parents, "output must be outside checkout")
        with destination.open("x") as stream:
            stream.write(serialized)
    else:
        need((HERE / "RESULT.json").read_text() == serialized, "receipt disagreement")
    print("PASS_CARRIER_MERGE_RELAY_PREMISE subsets=247 controls=11")


if __name__ == "__main__":
    main()
