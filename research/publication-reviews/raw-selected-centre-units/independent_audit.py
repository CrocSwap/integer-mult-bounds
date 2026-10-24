"""Check source identity, unit geometry, complete prices, and suffix order.

This review uses no package or producer imports. OpenAI Codex assisted it.
"""

from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import json
import subprocess


def need(value, message):
    if not value:
        raise ValueError(message)


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == ".gz" else raw)


def blob(repo, commit, path):
    return subprocess.check_output(["git", "-C", str(repo), "show", commit + ":" + path])


def determinant(matrix):
    rows = [[F(v) for v in row] for row in matrix]
    result = F(1)
    for col in range(len(rows)):
        pivot = next((i for i in range(col, len(rows)) if rows[i][col]), None)
        if pivot is None:
            return F(0)
        if pivot != col:
            rows[col], rows[pivot] = rows[pivot], rows[col]
            result *= -1
        value = rows[col][col]
        result *= value
        rows[col] = [x / value for x in rows[col]]
        for i in range(col + 1, len(rows)):
            value = rows[i][col]
            rows[i] = [a - value * b for a, b in zip(rows[i], rows[col])]
    return result


def inverse(matrix):
    n = len(matrix)
    rows = [[F(x) for x in row] + [F(i == j) for j in range(n)]
            for i, row in enumerate(matrix)]
    for col in range(n):
        pivot = next(i for i in range(col, n) if rows[i][col])
        rows[col], rows[pivot] = rows[pivot], rows[col]
        value = rows[col][col]
        rows[col] = [x / value for x in rows[col]]
        for i in range(n):
            if i != col:
                value = rows[i][col]
                rows[i] = [a - value * b for a, b in zip(rows[i], rows[col])]
    need([row[:n] for row in rows] == [[F(i == j) for j in range(n)] for i in range(n)],
         "Independent selected inverse")
    return [row[n:] for row in rows]


def price(kind, coefficient=0):
    if kind in ("clear", "copy"):
        return 2
    q = F(coefficient)
    a, b = abs(q.numerator), q.denominator
    need(a and b & (b - 1) == 0, "Nonzero dyadic coefficient")
    if kind == "scale":
        need(a & (a - 1) == 0, "Unit dyadic scale")
        return 2 * (abs(a.bit_length() - b.bit_length()) + int(q < 0))
    need(kind == "add", "Known scalar kind")
    return 2 * (3 + a.bit_length() - 1 + a.bit_count() + b.bit_length() - 1)


def complete_cost(program):
    total, scans, children = 0, 0, Counter()
    for event in program["retained_core"]:
        if event[0] == "scalar":
            gate = event[1]
            coefficient = 0 if gate[0] in ("clear", "copy") else F(*gate[-2:])
            total += price(gate[0], coefficient)
        elif event[0] == "climb":
            children[event[-1]] += 1
    need(children == {1: 2433, 2: 724, 3: 228, 4: 102, 5: 20}, "Complete child census")
    for event in program["prefix"] + program["input_exchange"] + program["suffix"] + program.get("owned_cleanup", []):
        if event["kind"] == "divide_odd":
            need(event["divisor"] == 3, "Separate exact third scan")
            scans += 2
        else:
            total += price(event["kind"], event.get("coefficient", 0))
    return total, scans


def add(a, b, coefficient=1):
    return tuple(x + coefficient * y for x, y in zip(a, b))


def mv(matrix, vector):
    return [tuple(sum(c * vector[j][k] for j, c in enumerate(row)) for k in range(2))
            for row in matrix]


def qmap(value, port, sign):
    a, b = value
    scale = sign * (port % 3 + 1)
    return (a + scale * b, b) if port % 2 else (a, b + scale * a)


def suffix(events, state):
    state = list(state)
    for event in events:
        kind, target = event["kind"], event["target"]
        if kind == "clear":
            state[target] = (F(0), F(0))
        elif kind == "copy":
            state[target] = state[event["source"]]
        elif kind == "scale":
            state[target] = tuple(F(event["coefficient"]) * x for x in state[target])
        else:
            need(kind == "add", "Literal suffix kind")
            state[target] = add(state[target], state[event["source"]], F(event["coefficient"]))
    return state


def main(args):
    package, repo = args.package.resolve(), args.repo.resolve()
    manifest = read(package / "SOURCE-MANIFEST.json")
    workspace_sources, git_sources, unavailable_git_sources = 0, 0, []
    for name, item in manifest["files"].items():
        raw = (package / name).read_bytes()
        need(len(raw) == item["bytes"] and sha256(raw).hexdigest() == item["sha256"], "Manifest bytes: " + name)
        if "decompressed_sha256" in item:
            need(sha256(gzip.decompress(raw)).hexdigest() == item["decompressed_sha256"], "Payload bytes: " + name)
        if "source_commit" in item:
            exists = subprocess.run(["git", "-C", str(repo), "cat-file", "-e", item["source_commit"]],
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0
            if exists:
                need(raw == blob(repo, item["source_commit"], item["source_repository_path"]), "Git source: " + name)
                git_sources += 1
            else:
                unavailable_git_sources.append({"file": name, "commit": item["source_commit"],
                                                "source_repository_path": item["source_repository_path"]})
        else:
            need(raw == (repo / item["source_workspace_path"]).read_bytes(), "Frozen source: " + name)
            workspace_sources += 1
    lanes = package / "frozen/work/centre-encoding-campaign-20261014/lanes"
    transfer = lanes / "new-core-transfer-20261017"
    provider_checks = []
    for provider in ("base", "extra"):
        raw = (transfer / ("native-original-" + provider) / "FULL-WORD.json.gz").read_bytes()
        original = blob(repo, "f2927a4b8afcf0701a6b945e14f30de1d94f5176", "research/coupled-carrier-cap740/words/" + provider + ".json.gz")
        parent = blob(repo, "51eb9c4ee9e4722010d308aa3309e039d3940cc2", "research/rank7-coupled-586-588-carrier-fold/edits/FINAL-WORD-" + provider + ".json.gz")
        need(gzip.decompress(raw) == gzip.decompress(original) == gzip.decompress(parent), "Exact two-PR provider payload")
        provider_checks.append({"provider": provider, "payload_sha256": sha256(gzip.decompress(raw)).hexdigest()})
    rows = read(transfer / "INTERFACE.json")["R"]
    r = [[F(row.get(str(p), 0)) for p in range(112)] for row in rows]
    selected = read(transfer / "IRREGULAR-38-RESPONSE-UNIT.json")["selected_S"]
    need(len(selected) == len(set(selected)) == 38, "Actual selected witness")
    gram = [[sum(r[i][p] * r[j][p] for p in selected) for j in range(8)] for i in range(8)]
    v = [[int((i, j) in ((0, 2), (0, 3), (1, 4), (1, 5))) for j in range(8)] for i in range(8)]
    need(gram == [[20 * (i == j) - 8 * (v[i][j] + v[j][i]) - 2 * sum(v[i][k] * v[j][k] for k in range(8))
                  for j in range(8)] for i in range(8)], "Displayed actual Gram formula")
    det_t = determinant([[gram[i][j] / 4 - 13 * (i == j) for j in range(8)] for i in range(8)])
    det_w = determinant([[(i == j) - gram[i][j] / 4 for j in range(8)] for i in range(8)])
    need((det_t, det_w) == (2**24, 2**12), "Two exact unit determinants")
    is_power_two = lambda k: k != 0 and abs(k) & (abs(k) - 1) == 0
    first_units = [k for k in range(1, 15) if is_power_two(k - 13)]
    both_units = [k for k in first_units if is_power_two(1 - k)]
    need(first_units == [5, 9, 11, 12, 14] and both_units == [5, 9], "Complete-minor class only")

    serial = read(transfer / "SERIAL-BALANCED-PROGRAMS.json.gz")
    irregular = read(transfer / "IRREGULAR-38-PROGRAMS.json.gz")
    reduced = read(transfer / "bipartite-eight-transfer-20261018/run-normal/REDUCED-INTERFACES-PROGRAMS.json.gz")
    invoices = {}
    for family, data in list(serial["families"].items()) + [("irregular", irregular)] + list(reduced["families"].items()):
        for provider, item in data["providers"].items():
            for name, program in item["programs"].items():
                invoices[family + "/" + provider + "/" + name] = complete_cost(program)
    need(len(invoices) == 36, "All 12 serial, six irregular, and 18 reduced words")
    for provider in ("base", "extra"):
        need(invoices["eight/" + provider + "/short_normalized_backward"] == (89200, 0), "Signed S8 complete cost")
        need(invoices["twenty_four/" + provider + "/short_normalized_backward"] == (89592, 0), "S24 complete cost")
        need(invoices["irregular/" + provider + "/diagonal_backward"] == (171662, 0), "S38 complete cost")
        need(invoices["one_minor/" + provider + "/diagonal_backward"] == (171730, 16), "Raw S8 separate third scans")
    unit_costs = {name: sum(price(event["kind"], event.get("coefficient", 0)) for event in events)
                  for name, events in read(transfer / "IRREGULAR-38-RESPONSE-UNIT.json")["programs"].items()}
    need(unit_costs == {"A": 7452, "inverse_A": 7412}, "Both literal response-unit invoices")
    need(171662 + unit_costs["inverse_A"] == 179074, "Complete composed response-normalized invoice")

    suffix_cases, wrong_order = 0, 0
    response_sources = {
        "eight": read(lanes / "controller-followthrough-20261017/bipartite-eight-20261018/BIPARTITE-EIGHT-PROGRAM.json.gz"),
        "twenty_four": read(lanes / "controller-followthrough-20261017/structured-centres/STRUCTURED-CENTRES-PROGRAM.json.gz")}
    for family, data in reduced["families"].items():
        source = response_sources[family]
        response_sign = 1 if family == "eight" else -1
        j = [[response_sign * F(row.get(str(p), 0)) for p in range(112)] for row in source["response"]]
        s = data["selected_S"]
        u = [p for p in range(112) if p not in s]
        li = inverse([[j[p][q] for q in s] for p in s])
        for provider, item in data["providers"].items():
            words = item["local_words"]
            for fixture in range(3):
                x = [(F(p - 53), F(p % 7 - 3)) if fixture != 0 else (F(0), F(0)) for p in range(112)]
                y = [(F(17 - p), F(p % 11 - 5)) if fixture != 1 else (F(0), F(0)) for p in range(112)]
                z = [qmap(x[p], p, 1) if p in s else x[p] for p in range(112)]
                query = [z[p] if p in s else y[p] for p in range(112)]
                jq = mv(j, query)
                raw = [add(qmap(y[p], p, -1) if p in s else x[p], jq[p], -1) for p in range(112)]
                state = raw + [z[p] if p in s else y[p] for p in range(112)]
                state += [(F(p + 3), F(-p - 1)) for p in range(408)] + [(F(0), F(0))] * 8
                long_result = suffix(words["long_normalizer_X"], state)
                short_result = suffix(words["short_normalizer_X"], state)
                need(long_result == short_result, "Full literal suffix equality on independent two-component data")
                selected_result = mv(li, [tuple(-v for v in raw[p]) for p in s])
                expected = list(state)
                for p, value in zip(s, selected_result):
                    expected[p] = value
                for p in u:
                    expected[p] = add(raw[p], mv([[j[p][q] for q in s]], selected_result)[0])
                need(short_result == expected, "Direct selected inverse and changed lower query")
                if family == "eight":
                    bad = suffix(words["lower_X"] + words["selected_inverse_X"], state)
                    need(bad != short_result, "Old selected query is rejected")
                    wrong_order += 1
                suffix_cases += 1
    report = {"status": "PASS_INDEPENDENT_SELECTED_UNITS_PUBLICATION_AUDIT",
              "source_manifest_sha256": sha256((package / "SOURCE-MANIFEST.json").read_bytes()).hexdigest(),
              "workspace_source_files_compared": workspace_sources, "git_source_files_compared": git_sources,
              "source_Git_objects_unavailable": unavailable_git_sources,
              "provider_payloads_match_both_pinned_PRs": provider_checks,
              "S38_gram_formula_checked": True, "det_T": str(det_t), "det_W": str(det_w),
              "complete_minor_H_unit_k": first_units, "complete_minor_both_unit_k": both_units,
              "complete_word_invoices": invoices, "independent_two_component_suffix_cases": suffix_cases,
              "response_unit_invoices": unit_costs,
              "wrong_suffix_order_controls": wrong_order,
              "limits": "Independent bounded source, geometry, price, and suffix checks. Full native phases and all arbitrary columns are checked by the separate cold package replay. No minimum or global supplier claim."}
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(report["status"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    main(parser.parse_args())
