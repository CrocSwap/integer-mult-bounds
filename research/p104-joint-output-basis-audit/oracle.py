#!/usr/bin/env python3
"""Independent exact reverse-mode scalar oracle; no author modules are imported.

This audits rational public transfer rows and temporal role allocation only.
It does not interpret native operators, absolute phases, tariffs, or kappa.
"""
import gzip
import hashlib
import json
import argparse
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ANCHORS = (703, 393, 707, 484, 297, 485, 226, 361, 451)
SENTINELS = (0, 1, 103, 104, 111, 112, 215, 216, 288, 395, 449, 549, 704, 744, 745, 769)
PINNED = {
    "sources/INPUT-WORD.json.gz": ("1415a62059ed62d0b4657db91f7ec01b23c117f5f2744746d93c880bd777be92", "f21f7ac451c3f2e1ae8d5ca1dcad839a0b0d844f"),
    "sources/OUTPUT-WORD.json.gz": ("0c83c1f1dee8c9442558719510a61b89f38c2dbfc8fb565ba035660d2a68d928", "03ea7690285d4cda72815f962d5710ab96e08490"),
    "sources/BASIS.json": ("e7bd061436c5fdbd1b968f9252cc79efda04320cf3c027a6fdcdf14ff4c9d2d3", "b35a19d4ec44aa365501ef0299a4b11f9cba3e00"),
    "sources/PROOF.md": ("cd400ad5d82d316e469bd5df81e4fc26faf1ba0aaa385a5f9964ec4786a9de5d", "d27ef41f57d7d75293515e56dc5c21c3e6cff0d7"),
    "sources/NOTICE": ("6c5f4a452f7d65ef8ca0980992dce279938b0a1139f6c067f91de78bf8ecb7bd", "e6cae17f778e8e31b7c294ff2890c545978931c0"),
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path):
    return json.loads(path.read_bytes())


def authenticate():
    pins = read_json(HERE / "SOURCE-PINS.json")
    require(type(pins) is list and len(pins) == 5, "five frozen source pins")
    require({p["file"]: (p["sha256"], p["git_blob"]) for p in pins} == PINNED,
            "independently pinned source bytes")
    for pin in pins:
        raw = (HERE / pin["file"]).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == pin["sha256"], "source SHA256: " + pin["file"])
        blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        require(blob == pin["git_blob"], "source Git blob: " + pin["file"])


def load_word(name):
    return json.loads(gzip.decompress((HERE / "sources" / name).read_bytes()))


def scalar(value):
    require(type(value) is str, "rational coefficients are strings")
    return Fraction(value)


def compile_word(word):
    public, owned = word["public"], word["owned_fields"]
    require(type(public) is int and public == 770 and type(owned) is int and owned == 29,
            "fixed public and owned inventories")
    require(len(word["initial"]) == public and len(word["final"]) == public, "public boundary sizes")
    active = dict(enumerate(word["initial"]))
    instructions, initializations, clears = [], [], []
    for index, event in enumerate(word["program"]):
        op, target = event[:2]
        require(type(target) is int and 0 <= target < public + owned, "role at event " + str(index))
        if op == "INIT":
            require(len(event) == 3 and target >= public and target not in active, "INIT lifetime")
            active[target] = event[2]
            initializations.append((index, target))
            instructions.append((op, target))
        elif op == "CLEAR":
            require(len(event) == 3 and target >= public and active.get(target) == event[2], "CLEAR lifetime")
            del active[target]
            clears.append((index, target))
            instructions.append((op, target))
        elif op == "MOVE":
            require(len(event) == 5 and active.get(target) == event[2] and type(event[4]) is bool,
                    "MOVE origin and charge type")
            require(type(event[3]) is int and 0 <= event[3] < len(word["frames"]), "MOVE destination")
            active[target] = event[3]
            instructions.append((op, target))
        elif op in ("ADD", "COPY"):
            require(len(event) == 5 and target in active and event[2] in active and
                    active[target] == active[event[2]] == event[4], "scalar addition frame and lifetime")
            require(target != event[2], "distinct addition roles")
            instructions.append((op, target, event[2], scalar(event[3])))
        elif op == "SCALE":
            require(len(event) == 4 and active.get(target) == event[3], "scalar scale frame and lifetime")
            coefficient = scalar(event[2])
            require(coefficient != 0, "invertible scalar scale")
            instructions.append((op, target, coefficient))
        else:
            raise ValueError("unsupported literal opcode: " + str(op))
    require(active == dict(enumerate(word["final"])), "exact final temporal inventory and frames")
    require(len(initializations) == len(clears), "complete owned lifetimes")
    return instructions, initializations, clears


def bump(weights, role, coefficient):
    value = weights.get(role, 0) + coefficient
    if value:
        weights[role] = value
    else:
        weights.pop(role, None)


def backwards_row(instructions, output_role, prefix=None):
    """Pull one coordinate functional through a literal prefix, in reverse.

    ADD r,s,c pulls its r coefficient into s. COPY overwrites r, so its
    pullback also discards r. INIT replaces an inactive role by zero and kills
    its coefficient. A CLEAR has no outgoing owned coordinate; liveness
    validation plus the next INIT guarantee that its coefficient is absent.
    """
    weights = {output_role: Fraction(1)}
    end = len(instructions) if prefix is None else prefix
    for index in range(end - 1, -1, -1):
        event = instructions[index]
        op, target = event[:2]
        value = weights.get(target)
        if op == "CLEAR":
            require(value is None, "adjoint coefficient on inactive CLEAR role")
        elif op == "INIT":
            weights.pop(target, None)
        elif op in ("ADD", "COPY"):
            if value is not None:
                bump(weights, event[2], value * event[3])
                if op == "COPY":
                    weights.pop(target, None)
        elif op == "SCALE" and value is not None:
            value *= event[2]
            if value:
                weights[target] = value
            else:
                weights.pop(target, None)
    require(all(role < 770 for role in weights), "adjoint leaves only independent public inputs")
    return weights


def encoded_row(row):
    return [[role, str(value)] for role, value in sorted(row.items())]


def digest_rows(rows):
    raw = (json.dumps([[role, encoded_row(row)] for role, row in rows.items()],
                      separators=(",", ":")) + "\n").encode()
    return hashlib.sha256(raw).hexdigest()


def copy_preconditions(instructions):
    checked = 0
    for index, event in enumerate(instructions):
        if event[0] == "COPY":
            require(not backwards_row(instructions, event[1], index),
                    "COPY destination scalar functional must be zero")
            checked += 1
    return checked


def first_difference(instructions, expected, probes):
    for role in probes:
        actual = backwards_row(instructions, role)
        if actual != expected[role]:
            keys = sorted(actual.keys() | expected[role].keys())
            source = next(key for key in keys if actual.get(key, 0) != expected[role].get(key, 0))
            return {"output": role, "input": source, "expected": str(expected[role].get(source, 0)),
                    "actual": str(actual.get(source, 0))}
    return None


def run():
    authenticate()
    source = load_word("INPUT-WORD.json.gz")
    final = load_word("OUTPUT-WORD.json.gz")
    left, left_init, left_clear = compile_word(source)
    right, right_init, right_clear = compile_word(final)
    source_copies, final_copies = copy_preconditions(left), copy_preconditions(right)
    require(source["initial"] == final["initial"], "unchanged initial frames")
    changed = [role for role in range(770) if source["final"][role] != final["final"][role]]
    require(set(changed) == set(ANCHORS), "exactly the nine changed output frame roles")
    require(source["frames"] == final["frames"][:-1], "all original frame coordinate lists unchanged")
    require(final["frames"][-1] == [7, 9, 35, 66, 400], "exact added forward frame")
    # Every output functional is recomputed in an independent backwards direction.
    source_rows, final_rows = {}, {}
    for role in range(770):
        source_rows[role] = backwards_row(left, role)
        final_rows[role] = backwards_row(right, role)
        require(source_rows[role] == final_rows[role], "public endpoint row " + str(role))
    probes = tuple(dict.fromkeys(ANCHORS + SENTINELS + tuple(range(770))))
    basis = read_json(HERE / "sources" / "BASIS.json")
    controls = {}
    for label, index in sorted(basis["control_indices"].items()):
        require(type(index) is int and 0 <= index < len(right), "control event index")
        event = right[index]
        require(event[0] in ("ADD", "SCALE"), "scalar omission control")
        corrupted = right[:index] + right[index + 1:]
        witness = first_difference(corrupted, source_rows, probes)
        require(witness is not None, "mutation must change a public transfer coefficient: " + label)
        controls[label] = {"omitted_index": index, "omitted_event": final["program"][index],
                           "witness": witness}
    # Added lifetimes appear after all historical lifetimes; report their exact
    # source-dependent CLEAR rows without assuming erasure is a scalar zero proof.
    new_inits = right_init[len(left_init):]
    require(len(new_inits) == 9 and {role for _, role in new_inits} == set(range(770, 779)),
            "nine added temporal lifetimes")
    temporal = []
    for start, role in new_inits:
        end = next(index for index, other in right_clear if other == role and index > start)
        row = backwards_row(right, role, end)
        temporal.append({"role": role, "init_index": start, "clear_index": end,
                         "public_support": len(row), "row": encoded_row(row)})
    return {
        "schema_version": 1,
        "claim_type": "independent exact finite scalar transfer audit",
        "scope": "all 770 public output rows, each over all 770 independent public inputs",
        "source_events": len(left), "final_events": len(right),
        "source_owned_lifetimes": len(left_init), "final_owned_lifetimes": len(right_init),
        "source_zero_destination_COPY_checks": source_copies,
        "final_zero_destination_COPY_checks": final_copies,
        "output_rows": 770, "input_coordinates": 770, "coefficient_comparisons": 770 * 770,
        "nonzero_coefficients": sum(map(len, source_rows.values())),
        "source_transfer_sha256": digest_rows(source_rows),
        "final_transfer_sha256": digest_rows(final_rows),
        "changed_output_roles": changed,
        "changed_output_row_sha256": digest_rows({role: final_rows[role] for role in sorted(ANCHORS)}),
        "controls": controls, "added_forward_lifetimes": temporal,
        "limits": [
            "Scalar MOVE is identity; native maps, absolute phases and native all-column obligations are outside this oracle.",
            "Owned CLEAR is a temporal boundary; this audit does not infer physical erasure from scalar rows.",
            "No tariff, complete caller, kappa, uniform compiler, precision tape or analytic recovery result is claimed.",
        ],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="emit a fresh receipt without retained-receipt comparison")
    options = parser.parse_args()
    result = run()
    retained = HERE / "ORACLE.json"
    if not options.emit:
        require(retained.is_file(), "retained ORACLE.json receipt must exist")
        canonical = lambda value: json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
        require(canonical(read_json(retained)) == canonical(result), "exact typed retained ORACLE.json receipt")
    print(json.dumps(result, indent=2, sort_keys=True))
