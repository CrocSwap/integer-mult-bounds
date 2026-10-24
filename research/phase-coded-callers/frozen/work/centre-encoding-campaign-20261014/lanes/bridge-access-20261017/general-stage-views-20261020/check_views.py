"""Emit dimension-independent stage views and check their exact phases."""

import argparse
from collections import Counter
from hashlib import sha256
import gzip
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
LANES = HERE.parent.parent
PINS = {
    "D25": (
        "bridge-access-20261017/matched-stage-access-20261018/DIMENSION25-VIEWS.json",
        "125e74660e99d824f8699eed72c1facb59287976bf2c47fda533d654b8344473",
    ),
    "D73": (
        "bridge-access-20261017/BRIDGE-PROGRAMS.json.gz",
        "57e2f089e0dd9f363603fc0278612b8ae8b98956a7422aa41fbd592922213abc",
    ),
    "complete_dual": (
        "bridge-access-20261017/involution-reader-dual-20261020/FREEZE.json",
        "09ad251a968be73fe95eefb05f57b842eb9f55e43822f029505256705120c811",
    ),
}


def need(test, message):
    if not test:
        raise ValueError(message)


def read(name):
    path, pin = PINS[name]
    raw = (LANES / path).read_bytes()
    if path.endswith(".gz"):
        raw = gzip.decompress(raw)
    need(sha256(raw).hexdigest() == pin, "Pinned source: " + name)
    return json.loads(raw)


def xor(values):
    result = 0
    for value in values:
        result ^= value
    return result


def act(columns, value):
    result = 0
    while value:
        bit = value & -value
        result ^= columns[bit.bit_length() - 1]
        value ^= bit
    return result


def add(a, b):
    return a[0] ^ b[0], a[1] ^ b[1] ^ (a[0] & b[0]), a[2] ^ b[2]


def line(vector, exponent=1):
    cross = 0
    value = vector
    while value:
        bit = value & -value
        j = bit.bit_length() - 1
        cross ^= (vector & (bit - 1)) << (j * (j - 1) // 2)
        value ^= bit
    return (vector if exponent & 1 else 0,
            vector if exponent & 2 else 0, cross if exponent & 1 else 0)


def phase(terms):
    result = (0, 0, 0)
    for vector, exponent in terms:
        result = add(result, line(vector, exponent % 4))
    return result


def root_record(q):
    need(q < 512 and q.bit_count() in (3, 7), "The actual intrinsic-line family")
    hole = next(j for j in range(9) if not (q >> j & 1))
    v = q ^ (1 << hole)
    order = list(range(9))
    order[0], order[hole] = order[hole], order[0]
    basis = [(1 << j) ^ (v if v >> j & 1 else 0) for j in order]
    need(basis[0] == q and all((a & b).bit_count() % 2 == (i == j)
         for i, a in enumerate(basis) for j, b in enumerate(basis)),
         "The literal root chart is orthonormal")
    beta = [((b.bit_count() - 1) // 2) % 2 for b in basis]
    need(beta[0] == 1, "The actual q correction is one")
    delta = xor(b for b, bit in zip(basis, beta) if bit)
    need(add(phase([(1 << j, 1) for j in range(9)]), line(delta, 2))
         == phase([(b, 1) for b in basis]), "The exact root quadratic refinement")
    return {"q": q, "root_basis": basis, "beta": beta,
            "root_translation": delta}


def make_view(q, stage, stages):
    need(1 <= stage <= stages, "A stage inside the chosen dimension")
    root = root_record(q)
    dimension = 9 + 8 * stages
    unit = [1 << j for j in range(dimension)]
    block = unit[9 + 8 * (stage - 1):9 + 8 * stage]
    swaps = [b ^ e for b, e in zip(root["root_basis"][1:], block)]
    rho = [e ^ xor(v for v in swaps if (v & e).bit_count() % 2) for e in unit]
    entry_before = root["root_translation"]
    entry_after = q ^ xor(e for e, bit in zip(block, root["beta"][1:]) if bit)
    exit_after = entry_before ^ entry_after
    need(act(rho, entry_before) == entry_after and act(rho, q) == q,
         "The entry translation and own line have the exact images")
    need([act(rho, x) for x in rho] == unit, "The route is an involution")
    need(all(act(rho, b) == e and act(rho, e) == b
             for b, e in zip(root["root_basis"][1:], block)),
         "The route exchanges exactly the eight stated axes")
    return {
        "dimension": dimension, "stage": stage, "q": q, "route_columns": rho,
        "entry_before_route": entry_before, "entry_after_route": entry_after,
        "exit_after_route": exit_after,
    }


def check_view(record, stages, all_levels=False):
    q, s, rho = record["q"], record["stage"], record["route_columns"]
    unit = [1 << j for j in range(record["dimension"])]
    delta_in, delta_out = record["entry_after_route"], record["exit_after_route"]
    counts = Counter()
    future_levels = range(s) if all_levels else (s - 1,)
    past_levels = range(s, stages + 1) if all_levels else (s,)
    for level in future_levels:
        full = [(v, 1) for v in unit[:9 + 8 * level]]
        exterior = [(v, 1) for v in unit[9:9 + 8 * level]]
        exterior += [(v, 1) for v in unit[9 + 8 * (s - 1):9 + 8 * s]]
        for hole in (False, True):
            source = full + ([(q, -1)] if hole else [])
            desired = exterior + ([] if hole else [(q, 1)])
            transported = phase([(act(rho, v), n) for v, n in source])
            need(add(transported, line(delta_in, 2)) == phase(desired),
                 "The complete future or adjacent entry phase")
            need(transported != phase(desired), "Omitting the entry translation fails")
            counts["future_entry_hole" if hole else "future_entry_full"] += 1
    for level in past_levels:
        full = [(v, 1) for v in unit[:9 + 8 * level]]
        for hole in (False, True):
            source = full + ([(q, -1)] if hole else [])
            transported = phase([(act(rho, v), n) for v, n in source])
            need(add(transported, line(delta_out, 2)) == phase(source),
                 "The complete current or past exit phase")
            need(transported != phase(source), "Omitting the exit translation fails")
            counts["past_exit_hole" if hole else "past_exit_full"] += 1
    return counts


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    sources = {name: read(name) for name in PINS}
    by25 = {(r["stage"], r["port"]): r for r in sources["D25"]["entries"]}
    ports = [by25[0, p]["q"] for p in range(112)]
    roots = [{"port": p, **root_record(q)} for p, q in enumerate(ports)]
    need(len(set(ports)) == 112, "All intrinsic lines are distinct")
    bound25 = 0
    for (stage, port), old in by25.items():
        if stage == 0:
            need(old["route_columns"] == [1 << j for j in range(25)],
                 "The stage-zero route is the identity")
            continue
        new = make_view(ports[port], stage, 2)
        align = old["literal_stage_alignment"]
        need(new["route_columns"] == old["route_columns"]
             and new["entry_before_route"] == align["entry_X"] == align["entry_Y"]
             and new["exit_after_route"] == align["exit_X"] == align["exit_Y"],
             "All literal D25 route and phase records agree")
        bound25 += 1
    bound73 = 0
    for old in sources["D73"]["views"]:
        new = make_view(ports[old["port"]], old["stage"], 8)
        need(new["route_columns"] == old["route_columns"], "The literal D73 route agrees")
        if old["side"] == "Y":
            need(new["entry_after_route"] == old["translation_after_route"]
                 and new["entry_before_route"] == old["translation_before_route"],
                 "The literal D73 future entry phase agrees")
        else:
            need(old["side"] == "X"
                 and new["exit_after_route"] == old["translation_after_route"]
                 == old["translation_before_route"], "The literal D73 past exit phase agrees")
        bound73 += 1
    reports = {}
    for stages in (1, 2, 3, 8, 16):
        counts = Counter()
        for q in ports:
            for stage in range(1, stages + 1):
                counts.update(check_view(make_view(q, stage, stages), stages,
                                         all_levels=stages <= 8))
        reports[str(9 + 8 * stages)] = dict(counts)
    payload = {
        "schema": "general-orthogonal-stage-view-v1", "source_pins": PINS,
        "root_records": roots, "dimension": "D=9+8T for any positive integer T",
        "route": "Swap root_basis[j+1] with e_(9+8*(s-1)+j), for j=0,...,7.",
        "entry_before_route": "root_translation",
        "entry_after_route": "q XOR sum(beta[j+1]*e_(9+8*(s-1)+j))",
        "exit_after_route": "entry_before_route XOR entry_after_route",
        "owner": "h=d*rho_(s,p); the route is an orthogonal involution.",
        "scope": "Exact ideal field and owner views. Native core, recursive host, "
                 "map cost, caller closure, and exponent are separate.",
    }
    raw = (json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode()
    receipt = {
        "status": "PASS_GENERAL_STAGE_VIEW_SOURCE_BINDING_AND_PHASE_REGRESSIONS",
        "producer_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "payload_sha256": sha256(raw).hexdigest(),
        "literal_D25_nonzero_stage_records": bound25,
        "literal_D73_side_records": bound73, "regressions": reports,
        "proof_scope": "The arbitrary-T result is proved by the quadratic-refinement "
                       "and spectator-axis argument, not inferred from these tests.",
    }
    args.output.mkdir(parents=True, exist_ok=False)
    (args.output / "VIEWS.json").write_bytes(raw)
    (args.output / "CHECKS.json").write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
