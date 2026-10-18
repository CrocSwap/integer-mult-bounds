#!/usr/bin/env python3
"""Exact selected1094 binary-chart binding; no supplier or Lean runtime imports.

Prepared for Adam Gall with substantial OpenAI Codex assistance. Apache-2.0.
The independent checker consumes witnesses; recover.py is not imported.
"""
from __future__ import annotations

import argparse
from collections import Counter
import copy
import gzip
import hashlib
import json
from pathlib import Path
import tarfile

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
ARCHIVE = "research/community-frontier1094-audit/selected-replay.tar.gz"
MEMBERS = {
    "sigmas": "candidate/strict/global/hosted/ACTUAL-SIGMAS.json.gz",
    "template": "candidate/strict/global/hosted/GLOBAL-TEMPLATE.json.gz",
    "hosted": "candidate/strict/global/hosted/HOSTED.json",
    "phases": "candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json",
}
N = 73


class Rejected(ValueError):
    """An exact source, shape, or mathematical obligation failed."""


def require(ok: bool, message: str) -> None:
    if not ok:
        raise Rejected(message)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def no_duplicates(items: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in items:
        require(key not in result, "duplicate JSON object key")
        result[key] = value
    return result


def decode(data: bytes) -> object:
    return json.loads(data, object_pairs_hook=no_duplicates,
                      parse_constant=lambda _: (_ for _ in ()).throw(Rejected("nonfinite JSON")))


def nat(value: object, bound: int, name: str) -> int:
    require(type(value) is int and 0 <= value < bound, f"invalid {name}")
    return value


def vector(value: object, n: int, bound: int, name: str) -> list[int]:
    require(type(value) is list and len(value) == n, f"invalid {name} length")
    return [nat(x, bound, name) for x in value]


def load_inputs() -> tuple[dict, dict]:
    sources = decode((PACKAGE / "SOURCES.json").read_bytes())
    for source in sources["files"]:
        if source["usage"] == "input":
            require(digest((ROOT / source["path"]).read_bytes()) == source["sha256"],
                    f"changed source: {source['path']}")
    values, hashes = {}, {}
    with tarfile.open(ROOT / ARCHIVE, "r:gz") as archive:
        names = Counter(member.name for member in archive.getmembers())
        for label, name in MEMBERS.items():
            require(names[name] == 1, "archive member missing or duplicated")
            member = archive.extractfile(name)
            require(member is not None, "archive member is not a file")
            raw = member.read()
            payload = gzip.decompress(raw) if name.endswith(".gz") else raw
            values[label] = decode(payload)
            hashes[label] = {"member": name, "bytes_sha256": digest(raw),
                             "payload_sha256": digest(payload), "payload_bytes": len(payload)}
    values["replay"] = decode((ROOT / "research/community-frontier1094-audit/REPLAY.json").read_bytes())
    require(hashes["template"]["payload_sha256"] == values["hosted"]["template_sha256"],
            "template/hosted binding")
    require(hashes["phases"]["bytes_sha256"] ==
            values["hosted"]["source_artifacts"]["work/complex-nine-native/DATA-PHASES.json"],
            "phase/hosted binding")
    require(hashes["phases"]["bytes_sha256"] == values["template"]["exact_data_phase_recipe_sha256"],
            "phase/template binding")
    return values, hashes


def apply_columns(columns: list[int], value: int) -> int:
    result = 0
    while value:
        bit = value & -value
        result ^= columns[bit.bit_length() - 1]
        value ^= bit
    return result


def elimination_inverse(columns: list[int]) -> list[int]:
    """Gauss-Jordan on augmented rows, independent of the chart factorization."""
    n = len(columns)
    rows = [sum(((column >> i) & 1) << j for j, column in enumerate(columns)) |
            (1 << (n + i)) for i in range(n)]
    for j in range(n):
        pivot = next((i for i in range(j, n) if (rows[i] >> j) & 1), None)
        require(pivot is not None, "singular column operator")
        rows[j], rows[pivot] = rows[pivot], rows[j]
        for i in range(n):
            if i != j and (rows[i] >> j) & 1:
                rows[i] ^= rows[j]
    require(all((row & ((1 << n) - 1)) == 1 << i for i, row in enumerate(rows)),
            "elimination did not reach identity")
    return [sum(((row >> (n + j)) & 1) << i for i, row in enumerate(rows)) for j in range(n)]


def check_certificate(columns: object, certificate: object, n: int) -> tuple[list[int], int, int]:
    """Check PR1879's exact five-array obligations, then independent inverses.

    Column j is e_(p[j]) + a[p[j]] u; the coefficient is NOT a[j].
    A = (I + u a^T) P. Thus A^-1 = P^-1 (I + u a^T).
    """
    cols = vector(columns, n, 1 << n, "dictionary columns")
    require(type(certificate) is list and len(certificate) == 5, "five-array certificate shape")
    p = vector(certificate[0], n, n, "forward indices")
    backward = vector(certificate[1], n, n, "inverse indices")
    witnessed = vector(certificate[2], n, 1 << n, "certificate columns")
    ubits = vector(certificate[3], n, 2, "update bits")
    abits = vector(certificate[4], n, 2, "coefficient bits")
    require(cols == witnessed, "dictionary/certificate columns mismatch")
    require(all(backward[p[j]] == j and p[backward[j]] == j for j in range(n)),
            "permutation round trip")
    u = sum(bit << i for i, bit in enumerate(ubits))
    a = sum(bit << i for i, bit in enumerate(abits))
    require((u & a).bit_count() % 2 == 0, "nonzero form on update")
    require(all(cols[j] == ((1 << p[j]) ^ (u if abits[p[j]] else 0)) for j in range(n)),
            "serialized coefficient mismatch")
    inverse = elimination_inverse(cols)
    p_inverse = [1 << i for i in backward]
    for j in range(n):
        expected = apply_columns(p_inverse, (1 << j) ^ (u if abits[j] else 0))
        require(inverse[j] == expected, "factor inverse differs from elimination")
        require(apply_columns(cols, inverse[j]) == 1 << j, "source after inverse")
        require(apply_columns(inverse, cols[j]) == 1 << j, "inverse after source")
    return inverse, u, a


def check_dictionary(sigmas: object, witnesses: object) -> dict:
    require(type(sigmas) is dict and type(witnesses) is dict, "dictionary shape")
    require(witnesses.get("format") == "pr1879-five-array-chart-witnesses-v1", "witness format")
    require(type(witnesses.get("dimension")) is int and witnesses["dimension"] == N, "witness dimension")
    entries = witnesses.get("entries")
    require(type(entries) is dict and set(entries) == set(sigmas), "witness key coverage")
    weights = Counter()
    symmetric = 0
    for key in sorted(sigmas):
        columns = vector(sigmas[key], N, 1 << N, "dictionary columns")
        require(key == digest(canonical(columns)), "dictionary content key mismatch")
        inverse, u, a = check_certificate(columns, entries[key], N)
        transpose = [sum(((column >> i) & 1) << j for j, column in enumerate(columns)) for i in range(N)]
        require(inverse == transpose, "selected chart is not orthogonal")
        weights[u.bit_count()] += 1
        symmetric += u == a
    return {"charts": len(sigmas), "dimension": N,
            "coefficient_entries": len(sigmas) * N * N,
            "two_sided_basis_compositions": 2 * len(sigmas) * N,
            "elimination_inverses": len(sigmas), "orthogonal_charts": len(sigmas),
            "symmetric_transvections": symmetric,
            "update_weight_histogram": {str(k): v for k, v in sorted(weights.items())}}


def port_basis(q: int) -> list[int]:
    """Apply the written rank-one port reflection to coordinate units.

    This is the source's idle chart convention, not a physical executor model.
    """
    nat(q, 512, "port label")
    require(q != 511 and q.bit_count() % 2 == 1, "port requires odd non-full label")
    z = next(i for i in range(9) if not ((q >> i) & 1))
    u = q ^ (1 << z)
    axes = [1 << i for i in range(N)]
    axes[0], axes[z] = axes[z], axes[0]
    return [x ^ (u if (x & u).bit_count() % 2 else 0) for x in axes]


def check_references(values: dict) -> dict:
    """Bind every helper occurrence to the complete actual dictionary.

    Data-owner routes and private/idle charts are NOT claimed to be dictionary
    entries. The emitter populates ACTUAL-SIGMAS only from the 480 helper roles.
    """
    sigmas, template, phases, hosted = (values[k] for k in ("sigmas", "template", "phases", "hosted"))
    require(template["m"] == N and template["live"] == 14336, "selected dimensions")
    calls = template["calls"]
    require(type(calls) is list and len(calls) == 144, "selected call count")
    require(len(phases["recipes"]) == 112, "phase recipe port coverage")
    providers = template["local_providers"]
    references, widths, role_keys, occurrences = Counter(), Counter(), set(), []
    stream = hashlib.sha256()
    for time, call in enumerate(calls):
        stage = nat(call["stage"], 9, "stage")
        replica = nat(call["replica"], 16, "replica")
        require(call["time"] == time, "call chronological index")
        require(call["provider_id"] in providers, "missing provider")
        provider = providers[call["provider_id"]]
        require((provider["v"], provider["h"], provider["R"]) == (112, 9, 480), "provider dimensions")
        require(len(call["owners"]) == 704 and len(provider["widths"]) == 480, "complete owner rows")
        for helper, owner in enumerate(call["owners"][224:]):
            require(type(owner) is list and len(owner) == 2, "owner pair shape")
            family = nat(owner[0], 14336, "family")
            route = owner[1]
            require(type(route) is list and len(route) in (3, 5), "helper route shape")
            typ = nat(route[0], 5, "route tag")
            require(typ in (3, 4), "nonhelper route in helper rows")
            require(len(route) == (3 if typ == 3 else 5), "route tag/shape mismatch")
            offset = nat(route[2], N, "offset")
            width = nat(provider["widths"][helper], 10, "helper width")
            require(width > 0 and (width == 9) == (typ == 3), "helper width/route tag")
            port = family % 112
            q = provider["ports"][port]
            recipe = phases["recipes"][port]
            require(recipe["port"] == port and recipe["q"] == q, "port/phase correspondence")
            child = nat(route[1], len(recipe["idle_children"]), "child")
            basis = port_basis(q)
            pending = recipe["idle_children"][child]["orthogonal_axes"]
            require(offset + width <= len(pending), "pending slice outside child")
            axes = pending[offset:offset + width]
            lookup = {axis: i for i, axis in enumerate(basis)}
            require(all(axis in lookup for axis in axes), "pending axis outside basis")
            active = [lookup[axis] for axis in axes]
            free = [j for j in range(N) if j not in active]
            spectators = free[:9 - width]
            if typ == 4:
                require(type(route[3]) is int and route[3] == width, "serialized helper width")
                supplied = vector(route[4], 9 - width, N, "spectators")
                require(supplied == spectators, "spectator order mismatch")
            order = active + spectators + free[9 - width:]
            require(sorted(order) == list(range(N)), "route is not a coordinate permutation")
            columns = [basis[j] for j in order]
            key = digest(canonical(columns))
            require(key in sigmas and sigmas[key] == columns, "referenced chart absent or different")
            role = (stage, replica, helper)
            require(role not in role_keys, "duplicate helper occurrence")
            role_keys.add(role)
            references[key] += 1
            widths[width] += 1
            record = [stage, replica, helper, family, key]
            stream.update(canonical(record) + b"\n")
            occurrences.append(record)
    require(role_keys == {(s, r, h) for s in range(9) for r in range(16) for h in range(480)},
            "incomplete selected role domain")
    require(set(references) == set(sigmas), "unreferenced dictionary entry")
    require(stream.hexdigest() == hosted["sigma_stream_sha256"], "ordered occurrence digest mismatch")
    require(len(sigmas) == hosted["unique_actual_73column_sigmas"] == values["replay"]["actual_73_axis_charts"],
            "selected chart count binding")
    require(len(occurrences) == hosted["hosted_residuals"] == values["replay"]["roles"], "selected role count binding")
    return {"calls": len(calls), "helper_roles": len(occurrences), "unique_references": len(references),
            "unreferenced_entries": 0, "missing_entries": 0,
            "ordered_sigma_stream_sha256": stream.hexdigest(),
            "width_histogram": {str(k): v for k, v in sorted(widths.items())},
            "reference_multiplicity_histogram": {str(k): v for k, v in sorted(Counter(references.values()).items())},
            "first_occurrence": occurrences[0], "last_occurrence": occurrences[-1]}


def controls(values: dict, witnesses: dict) -> dict:
    rejected = []

    def reject(name, action):
        try:
            action()
        except Rejected:
            rejected.append(name)
        else:
            raise Rejected(f"negative control accepted: {name}")

    identity = [list(range(3)), list(range(3)), [1, 2, 4], [0, 0, 0], [0, 0, 0]]
    check_certificate([1, 2, 4], identity, 3)
    # A three-cycle ensures reversal/direction controls are not involution-blind.
    example = [[1, 2, 0], [2, 0, 1], [1, 4, 2], [1, 1, 0], [1, 1, 0]]
    check_certificate(example[2], example, 3)
    key = next(k for k in sorted(values["sigmas"])
               if witnesses["entries"][k][0] != witnesses["entries"][k][1])
    original = witnesses["entries"][key]
    for name, field, index, replacement in [
        ("boolean-column", 2, 0, True), ("float-column", 2, 0, 1.0),
        ("negative-column", 2, 0, -1), ("out-of-range-column", 2, 0, 1 << N),
        ("forward-out-of-range", 0, 0, N), ("bad-update-bit", 3, 0, 2),
        ("bad-coefficient-bit", 4, 0, 2),
        ("dictionary-certificate-mismatch", 2, 0, original[2][0] ^ 1),
        ("inverse-table-mutation", 1, 0, (original[1][0] + 1) % N),
        ("coefficient-mutation", 4, 0, 1 - original[4][0]),
    ]:
        bad = copy.deepcopy(original)
        bad[field][index] = replacement
        reject(name, lambda bad=bad: check_certificate(values["sigmas"][key], bad, N))
    bad = copy.deepcopy(original)
    bad[0], bad[1] = bad[1], bad[0]
    reject("permutation-direction-reversal", lambda: check_certificate(values["sigmas"][key], bad, N))
    reject("extra-certificate-field", lambda: check_certificate(values["sigmas"][key], original + [[]], N))
    singular = [[0, 1, 2], [0, 1, 2], [0, 2, 4], [1, 0, 0], [1, 0, 0]]
    reject("nonorthogonal-transvection-form", lambda: check_certificate(singular[2], singular, 3))
    reject("singular-elimination", lambda: elimination_inverse([1, 1, 4]))
    reject("duplicate-json-key", lambda: decode(b'{"x":1,"x":2}'))
    # A simultaneous change of both source and witness cannot preserve the content key.
    fake = {key: list(values["sigmas"][key])}
    fake[key][0] ^= 1
    reject("wrong-content-key", lambda: check_dictionary(fake, {
        "format": witnesses["format"], "dimension": N, "entries": {key: original}}))
    reduced = dict(values)
    reduced["sigmas"] = dict(values["sigmas"])
    del reduced["sigmas"][values["first_reference_key"]]
    reject("missing-live-chart", lambda: check_references(reduced))
    extra = dict(values)
    extra["sigmas"] = dict(values["sigmas"])
    extra["sigmas"]["unreferenced"] = list(range(N))
    reject("orphan-dictionary-entry", lambda: check_references(extra))
    altered = dict(values)
    altered["template"] = copy.deepcopy(values["template"])
    route = next(row[1] for row in altered["template"]["calls"][0]["owners"][224:] if row[1][0] == 4)
    route[4][0] = (route[4][0] + 1) % N
    reject("changed-spectator-axis", lambda: check_references(altered))
    # Show that moving the permutation to the wrong side changes an actual map.
    direction_witness = None
    for candidate_key in sorted(values["sigmas"]):
        candidate = witnesses["entries"][candidate_key]
        u = sum(bit << i for i, bit in enumerate(candidate[3]))
        a = sum(bit << i for i, bit in enumerate(candidate[4]))
        inverse = elimination_inverse(candidate[2])
        for j in range(N):
            permuted = 1 << candidate[1][j]
            wrong = permuted ^ (u if (permuted & a).bit_count() % 2 else 0)
            if inverse[j] != wrong:
                direction_witness = {"key": candidate_key, "input_axis": j,
                                     "correct_inverse_column": inverse[j], "wrong_order_column": wrong}
                break
        if direction_witness:
            break
    require(direction_witness is not None, "no actual wrong-order separating witness")
    return {"positive_cases": ["identity-3", "noncommuting-permutation-transvection-3"],
            "rejected": rejected, "wrong_inverse_order_witness": direction_witness}


def run() -> dict:
    values, hashes = load_inputs()
    raw = gzip.decompress((PACKAGE / "WITNESSES.json.gz").read_bytes())
    witnesses = decode(raw)
    chart_report = check_dictionary(values["sigmas"], witnesses)
    references = check_references(values)
    values["first_reference_key"] = references["first_occurrence"][-1]
    return {"status": "PASS_SELECTED_SIGMA_CHART_BINDING", "archive_sha256": digest((ROOT / ARCHIVE).read_bytes()),
            "members": hashes, "witness_payload_sha256": digest(canonical(witnesses)),
            "charts": chart_report, "references": references, "controls": controls(values, witnesses),
            "scope": "Exact selected binary-column certificate and helper-reference audit; no Lean build, physical executor, paid-cost or kappa claim."}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-receipt", type=Path, help="Write a new receipt; refuses an existing file")
    args = parser.parse_args()
    result = run()
    if args.write_receipt:
        with args.write_receipt.open("x") as output:
            output.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        expected = decode((PACKAGE / "RESULT.json").read_bytes())
        require(canonical(result) == canonical(expected), "receipt differs from exact replay")
    print(f"PASS_SELECTED_SIGMA_CHART_BINDING charts={result['charts']['charts']} "
          f"dimension={N} helper_roles={result['references']['helper_roles']} "
          f"controls={len(result['controls']['rejected'])} no_new_lean_build no_new_kappa")


if __name__ == "__main__":
    main()
