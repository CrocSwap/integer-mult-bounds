#!/usr/bin/env python3
"""Offline proof-carrying replay of the two archived P111 fitting claims."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path

import encoding
import lrat
import controls
import compare_original

ROOT = Path(__file__).resolve().parent
BASE = "2921874911956718fcaaaf9396fe8267b3cfa9f0"


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode("ascii")


def pairs(items):
    result = {}
    for key,value in items:
        encoding.need(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def read_json(path):
    return json.loads(path.read_text(), object_pairs_hook=pairs,
                      parse_constant=lambda x:encoding.need(False,"nonfinite JSON value"))


def sources():
    manifest = read_json(ROOT/"SOURCES.json")
    encoding.need(manifest["base_commit"] == BASE, "base source pin")
    encoding.need(manifest["current_pr620_head"] == "8f0150e0d0a8a02370907be35cccd3ca69cdd941", "PR620 head pin")
    expected = {"vendor/pr620/"+name for name in
                ("README.md","REPORT.md","geo.py","e8units.py","minrank_sat.py","uniq.py")}
    expected |= {"vendor/drat-trim/"+name for name in ("LICENSE","drat-trim.c","lrat-check.c")}
    encoding.need(set(manifest["source_files"]) == expected, "source inventory")
    for path,record in manifest["source_files"].items():
        raw = (ROOT/path).read_bytes()
        encoding.need(hashlib.sha256(raw).hexdigest() == record["sha256"], "source SHA256 pin: "+path)
        blob = hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
        encoding.need(blob == record["git_blob"], "source Git blob pin: "+path)
        if path.startswith("vendor/pr620/"):
            commit = BASE if path.endswith("/README.md") else manifest["current_pr620_head"]
            encoding.need(record["source_commit"] == commit, "archival source commit")
        else:
            encoding.need(record["source_commit"] == "2e3b2dc0ecf938addbd779d42877b6ed69d9a985", "native checker source commit")
    implementation = {"encoding.py","lrat.py","controls.py","verify.py","produce.py","compare_original.py","test_package.py"}
    encoding.need(set(manifest["implementation_sha256"]) == implementation, "implementation inventory")
    for path,digest in manifest["implementation_sha256"].items():
        encoding.need(hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == digest, "implementation pin: "+path)
    encoding.need(set(manifest["proofs"]) == {"8","9"}, "proof inventory")
    return manifest


def compute():
    manifest = sources()
    rows, gram, live, baseline, pattern, clique, labels = encoding.geometry()
    matrix_rank = controls.rank2([sum(bit << j for j,bit in enumerate(row)) for row in baseline])
    encoding.need(matrix_rank == 9 and controls.rank2(labels) == 9, "positive fitting rank")
    context = {"root_lines":rows,"live":live,"punctures":list(encoding.PUNCTURES),
               "anchor_live":clique,"anchor_original":[live[i] for i in clique],
               "baseline_rank":matrix_rank,"baseline_sha256":hashlib.sha256(canonical(baseline)).hexdigest(),
               "positive_labels":labels,"ordered_zero_entries":len(pattern),
               "ordered_free_entries":111*110-len(pattern),
               "ordered_orthogonal_puncture_pairs":sum(i != j and gram[i][j] == 0 for i in encoding.PUNCTURES for j in encoding.PUNCTURES)}
    encoding.need(hashlib.sha256(canonical(context)).hexdigest() == manifest["geometry_sha256"], "geometry/order pin")
    evidence = {}
    control_result = None
    for c in (8,9):
        record = manifest["proofs"][str(c)]
        encoding.need(record["path"] == f"proofs/c{c}.lrat.gz", "proof path")
        raw = gzip.decompress((ROOT/record["path"]).read_bytes())
        encoding.need(len(raw) == record["proof_bytes"] and hashlib.sha256(raw).hexdigest() == record["proof_payload_sha256"], "decoded proof pin")
        proof = lrat.parse(raw.decode("ascii"))
        roots = lrat.root_references(proof,record["clauses"])
        selected = {}
        dimacs_hash = hashlib.sha256(f'p cnf {record["variables"]} {record["clauses"]}\n'.encode('ascii'))
        def sink(index,clause):
            dimacs_hash.update((" ".join(map(str,clause))+" 0\n").encode("ascii"))
            if index in roots:
                selected[index] = clause
        formula = encoding.archived(c,sink)
        encoding.need(formula.variables == record["variables"] and formula.clauses == record["clauses"], "formula dimensions")
        encoding.need(formula.payload_hash.hexdigest() == record["clause_payload_sha256"] and dimacs_hash.hexdigest() == record["cnf_sha256"], "regenerated formula pin")
        encoding.need(len(proof) == record["proof_additions"], "proof length")
        proof_result = lrat.check(proof,selected,formula.variables,formula.clauses)
        if c == 9:
            encoding.need(formula.unsatisfied == [formula.clauses], "rank-nine positive calibration")
        else:
            control_result = controls.proof_controls(proof,selected,formula.variables,formula.clauses)
        evidence[str(c)] = {"mode":record["mode"],"variables":formula.variables,"clauses":formula.clauses,
                           "clause_payload_sha256":formula.payload_hash.hexdigest(),
                           "cnf_sha256":dimacs_hash.hexdigest(),"proof_payload_sha256":record["proof_payload_sha256"],
                           "proof":proof_result,"positive_calibration_violated_clauses":formula.unsatisfied if c == 9 else None}
        evidence[str(c)]["original_encoding_comparison"] = compare_original.compare(c,formula.payload_hash.hexdigest())
    wrong_order = dict(context)
    wrong_order["root_lines"] = list(rows)
    wrong_order["root_lines"][0],wrong_order["root_lines"][95] = rows[95],rows[0]
    controls.rejection(lambda:encoding.need(hashlib.sha256(canonical(wrong_order)).hexdigest() == manifest["geometry_sha256"], "geometry/order pin"),"wrong root ordering")
    control_result["rejected"].append("wrong root ordering")
    return {"schema":1,"seed":95,"base_commit":BASE,
            "source_manifest_sha256":hashlib.sha256((ROOT/"SOURCES.json").read_bytes()).hexdigest(),
            "geometry":context,"certificates":evidence,
            "finite_semantics":controls.small_semantics(),"controls":control_result,
            "conclusion":{"archival_minrank_F2":9,"rank_nine_fitting_matrix_unique":True,
                          "supplier_punctures_checked":False,"copy_cost_floor_checked":False,"new_kappa":False}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write",action="store_true",help="author: regenerate EXPECTED.json")
    parser.add_argument("--receipt",type=Path)
    args = parser.parse_args()
    result = compute()
    if args.write:
        (ROOT/"EXPECTED.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    else:
        encoding.need(canonical(result) == canonical(read_json(ROOT/"EXPECTED.json")), "certificate differs from replay")
    if args.receipt:
        args.receipt.write_bytes(canonical(result)+b"\n")
    print(json.dumps({"status":"PASS","minrank":9,"unique_rank_nine_fitting_matrix":True,
                      "proof_additions":sum(v["proof"]["additions"] for v in result["certificates"].values()),
                      "hints_checked":sum(v["proof"]["hints_checked"] for v in result["certificates"].values()),
                      "receipt_sha256":hashlib.sha256(canonical(result)).hexdigest(),"new_kappa":False},sort_keys=True))


if __name__ == '__main__':
    main()
