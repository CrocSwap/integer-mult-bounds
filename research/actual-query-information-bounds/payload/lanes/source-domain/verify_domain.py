"""Check the fixed-stock cost of a code that removes centre responses."""

from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import io
import json
import subprocess
import tarfile


BASE = "bce54fb3f895cbe5cd4c0eb477c3afeed100190f"
ARCHIVE = "research/community-frontier1042-audit/selected-replay.tar.gz"
PLAN = "research/complex-t16-rare-pattern-exchanges/data/PLAN.json"
WORD = "slots/local/CANONICAL-WORD.json.gz"
PROGRAMS = "slots/local/LOCAL-PROGRAMS.json.gz"
TEMPLATE = "t16/global/hosted/GLOBAL-TEMPLATE.json.gz"
PINS = {
    ARCHIVE: "22c3f4dce4b897a1d423d1388801933e288b6a6b1906cb15e1b16a5eb68db754",
    PLAN: "7bd786ba8e66408f02aa9ef446eaf20c1bfe981ea2e4dd1e5a929f0aa7767bc0",
    WORD: "16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219",
    PROGRAMS: "241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a",
    TEMPLATE: "73f47a1e60b1e4ea66dbca9a497c411c8e6adc7984e276a437a10a9a7a13b47a",
    "notes/three-stage-cover-complex.tex": "1c5b638aa9b75365b8addec9c8eeee6bc5e499722901079b94c65fce033fde8a",
    "notes/general-clifford-frames.tex": "c9bb9655b594583c6b4bab8cb485233f1d1e588f83858cf1e4c3530cee8fed54",
    "notes/batched-complex-rows.tex": "64c70926a8705874f1c9b42a2f703e42cad4e90f927f544458cfdf729540236c",
    "research/punctured112-global/proof/GLOBAL-RESTRICTION.md": "90f67d1b4385d604318a03878cbb57ab136f8709850f7b1493774e4953892612",
    "research/static44-selective/proof/PR510-MUTABLE-SOURCE-CARRYOVER.md": "b2b597491874d6e4ad3ead49bf9a15515745de578bc8c200ab60cf6ec9bac1f2",
}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def pin(name, data):
    require(sha256(data).hexdigest() == PINS[name], "Source pin: " + name)
    return data


def source(repo, name):
    return pin(name, subprocess.check_output(["git", "show", BASE + ":" + name], cwd=repo))


def clean_centre_map(word, events):
    v = word["v"]
    n = 2 * v + word["R"]
    rows = [{p: Q(1)} if p < v else {} for p in range(n + 8)]

    def reg(item):
        return item[1] + (n if item[0] == "C" else 0)

    for event in events:
        if event == ["phase", "centers"]:
            break
        if event[0] != "scalar":
            continue
        gate = event[1]
        target = reg(gate[1])
        if gate[0] == "clear":
            rows[target] = {}
        elif gate[0] == "copy":
            rows[target] = rows[reg(gate[2])].copy()
        elif gate[0] == "scale":
            rows[target] = {p: x * Q(gate[2], gate[3]) for p, x in rows[target].items()}
        else:
            require(gate[0] == "add", "Unexpected scalar gate")
            for p, x in list(rows[reg(gate[2])].items()):
                value = rows[target].get(p, Q(0)) + x * Q(gate[3], gate[4])
                if value:
                    rows[target][p] = value
                else:
                    rows[target].pop(p, None)
    else:
        raise ValueError("The centre boundary is absent")
    return [[rows[c].get(p, Q(0)) for p in range(v)] for c in word["centers"]]


def run(repo):
    for name in PINS:
        if name not in (ARCHIVE, WORD, PROGRAMS, TEMPLATE, PLAN):
            source(repo, name)
    plan = json.loads(source(repo, PLAN))
    with tarfile.open(fileobj=io.BytesIO(source(repo, ARCHIVE)), mode="r:gz") as stream:
        raw = {name: pin(name, stream.extractfile(name).read())
               for name in (WORD, PROGRAMS, TEMPLATE)}
    word, programs, template = [json.loads(gzip.decompress(raw[name]))
                                for name in (WORD, PROGRAMS, TEMPLATE)]
    matrix = clean_centre_map(word, programs["forward"])
    r, v = len(matrix), word["v"]
    gram = [[sum(matrix[i][p] * matrix[j][p] for p in range(v))
             for j in range(r)] for i in range(r)]
    require(gram == [[Q(56 * (i == j)) for j in range(8)] for i in range(8)],
            "The centre map does not have the required rank")
    norms = [sum(matrix[i][p] ** 2 for i in range(r)) for p in range(v)]
    require(norms == [Q(4)] * v, "Unequal column norms")

    # A coordinate permutation copies physical data in different logical coordinates.
    q0, q1 = word["ports"][:2]
    require((q0, q1) == (11, 19), "The entrance witness uses different ports")

    def swap_coordinates(x):
        return x ^ (24 if bool(x & 8) != bool(x & 16) else 0)

    require(swap_coordinates(q0) == q1, "The coordinate map does not send q0 to q1")
    logical_address = 8
    wanted_support = sorted([logical_address, logical_address ^ q1])
    routed_support = sorted(swap_coordinates(x) for x in
                            [logical_address, logical_address ^ q0])
    require(wanted_support == [8, 27] and routed_support == [3, 16],
            "The physical-copy control does not change the logical payload")

    # These vectors show that no single input port is forced to zero by R x = 0.
    for p in range(v):
        witness = [Q(1) if q == p else
                   -sum(matrix[i][q] * matrix[i][p] for i in range(r)) / 52
                   for q in range(v)]
        require(all(sum(row[q] * witness[q] for q in range(v)) == 0 for row in matrix),
                "A nullspace coordinate witness fails")
        require(witness[p] == 1, "A nullspace witness loses its chosen port")

    replicas, m, live = plan["T"], plan["M"], plan["live"]
    require((replicas, m, live, plan["K"], plan["L"]) == (16, 73, 14336, 4, 9),
            "The stock or controller changed")
    calls = {(c["replica"], c["stage"]): c for c in template["calls"]}
    for replica in range(replicas):
        events = [e for e in template["execution_schedule"] if e.get("replica") == replica]
        require([(e["kind"], e.get("stage")) for e in events[:2]] ==
                [("local_cover_sweep", 0), ("local_cover_sweep", 1)],
                "A bridge precedes the second call")
        for stage, orientation in ((0, "forward"), (1, "backward")):
            c = calls[replica, stage]
            require(c["pair"] == 0 and c["orientation"] == orientation,
                    "The first two calls do not use the same data pair")
            require([owner[0] for owner in c["owners"][:2 * v]] ==
                    list(range(replica * 8 * v, replica * 8 * v + 2 * v)),
                    "The first pair uses unexpected data owners")
    require(len(calls) == 9 * replicas, "Incomplete call stock")

    mass = sum(int(rank) * count for rank, count in plan["profile"].items())
    require(m * live - mass == plan["deficit"] == 5120, "The selected rank bill changed")
    stripped_mass = mass - len(calls) * 64
    require(stripped_mass == (m - 1) * live, "The all-centre removal bill changed")
    per_replica = Q(live, replicas)
    codimension = 2 * r
    useful = per_replica - codimension
    actual_moment = Q(stripped_mass, replicas) / (m * useful)
    apparent_moment = Q(stripped_mass, m * live)
    one_bank_moment = Q(stripped_mass, replicas) / (m * (per_replica - r))
    require(actual_moment == Q(4032, 4015) > 1, "The two-call code was not rejected")
    require(apparent_moment < 1 and one_bank_moment < 1,
            "The controls do not distinguish the lost independent data")
    additional_saving = m * codimension - per_replica
    require(additional_saving == 272, "Incorrect additional rank requirement")
    return {
        "status": "PASS_FIXED_STOCK_CENTRE_NULLSPACE_CODE_OBSTRUCTION",
        "base": BASE, "source_pins": PINS,
        "source_map_shape": [r, v], "gram_diagonal": 56,
        "column_norm_squared": 4, "nullspace_coordinate_witnesses": v,
        "physical_copy_control": {
            "input_port": q0, "image_port": q1, "orthogonal_map": "swap coordinates 3 and 4",
            "logical_input_address": logical_address, "required_support": wanted_support,
            "rank_zero_routed_copy_support": routed_support,
            "correct_adapter_rank_from_preimage_frame_formula": 2,
        },
        "first_two_calls": {"replicas": replicas, "stages": [0, 1], "pair": 0,
                            "orientations": ["forward", "backward"], "intervening_bridges": 0},
        "stock_per_replica": str(per_replica), "global_live_stock": live,
        "ambient_rank": m, "old_global_rank_mass": mass,
        "optimistic_global_rank_mass_without_centres": stripped_mass,
        "necessary_codimension_below_per_replica": str(per_replica / m),
        "nullspace_protocol_codimension_at_least_per_replica": codimension,
        "optimistic_moment_after_code_at_b_zero": str(actual_moment),
        "incorrect_full_stock_moment_control": str(apparent_moment),
        "insufficient_one_bank_constraint_control": str(one_bank_moment),
        "further_rank_saving_needed_strictly_more_than_per_replica": str(additional_saving),
        "scope": "Ordinary-shear nullspace codes with the same nine-stage children and stock; no bound on a redesigned coded recursion.",
        "not_checked": ["native code preparation", "new hosting", "new supplier", "complete cold replay", "new kappa"],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    result = run(args.repo)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"])
    print("replicas=16 rank=16 per_replica_stock=896 moment_at_b_zero=4032/4015")
