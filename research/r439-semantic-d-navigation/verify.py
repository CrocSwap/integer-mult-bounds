#!/usr/bin/env python3
"""Cross-bind retained R439 evidence; do not replay the hosted supplier.

Prepared for commdata2338 with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import copy
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FILES = {
    "selected": "certificates/selected-result.json",
    "assembly": "research/community-frontier1094-audit/ASSEMBLY.json",
    "stars": "research/r439-bsection-stars-seed01/CERTIFICATE.json",
    "contract": "research/r439-semantic-d-contract-seed10/RESULT.json",
    "bridge": "research/r439-abc-semantic-bridge/RESULT.json",
    "hosted": "research/r439-abc-hosted-invoice/RESULT.json",
    "word": "research/r439-abc-star-composition/candidate.json.gz",
    "bridge_word": "research/r439-abc-semantic-bridge/inputs/candidate.json.gz",
    "review1099": "research/community-batch1099-audit/DISPOSITIONS.json",
    "review300": "research/community-efficient300-audit/DISPOSITIONS.json",
    "review400": "research/community-efficient400-audit/DISPOSITIONS.json",
    "review800": "research/community-efficient800-audit/DISPOSITIONS.json",
    "proof": "research/r439-semantic-d-contract-seed10/PROOF.md",
    "hosted_note": "research/r439-abc-hosted-invoice/README.md",
}
# Exact retained heads, not claims about the live state of GitHub.
CHAIN = [
    (1062, "review1099", "cd016e5dcd5ba28dafa3f3b4eeef003a38e6a11b", "r439-bsection-stars-seed01", "thakrarsagar"),
    (1122, "review300", "a2551e70fce0cc34348f50f1a94e7cc4c80bbcbf", "r439-abc-star-composition", "bitplane"),
    (1194, "review300", "2e39c98238f543d988f9efc1b076590a4b780dca", "r439-semantic-d-contract-seed10", "woklerx"),
    (1311, "review400", "a2875c1834b9c9ef42a84eda4890d5462cc98fa5", "r439-abc-semantic-bridge", "Arham-Tahir64"),
    (1806, "review800", "48153115a150af98a9c94adb34cab180dcd226e5", "r439-abc-hosted-invoice", "mtpsl"),
]
OLD_H2 = "H2_D_frame0_targets_from_helpers"
HYPOTHESES = {"H1_no_target_feeds_z", OLD_H2, "H3_A_z_only_scatter_targets_B_split",
              "H4_C_literal_reverse_at_full", "H5_V_identity"}
CONCLUSIONS = {"U_block_form", "J_identity", "K_equals_D", "C_is_U_inverse"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def load_inputs():
    manifest = json.loads((HERE / "SOURCES.json").read_bytes())
    pins = {p["path"]: p for p in manifest["files"] if p["usage"] == "input"}
    require(set(pins) == set(FILES.values()), "complete input inventory")
    raw = {}
    for name, path in FILES.items():
        raw[name] = (ROOT / path).read_bytes()
        require(sha(raw[name]) == pins[path]["sha256"], "source pin: " + path)
    data = {k: json.loads(v) for k, v in raw.items() if FILES[k].endswith(".json")}
    return data, raw


def check_flags(owner, syntactic_failure):
    h, c = owner["hypotheses"], owner["conclusions"]
    require(set(h) == HYPOTHESES and set(c) == CONCLUSIONS, "interface flag inventory")
    require(all(v is (not syntactic_failure if k == OLD_H2 else True) for k, v in h.items()), "H2 syntax distinguished")
    require(all(v is (not syntactic_failure if k == "K_equals_D" else True) for k, v in c.items()), "inherited conclusion flags")


def check_evidence(d, raw):
    chain = []
    for pr, review, head, package, author in CHAIN:
        rows = [r for r in d[review]["pull_requests"] if r["number"] == pr]
        require(len(rows) == 1, "unique retained disposition")
        row = rows[0]
        require(row["reviewed_head"] == row["current_head"] == head, "retained head")
        require(row["disposition"] == "incorporated", "retained disposition")
        require(row["integration_location"] == ["research/" + package], "retained location")
        require(row["metadata"]["author"]["login"] == author, "predecessor attribution")
        chain.append({"pr": pr, "head": head, "author": author, "package": "research/" + package})

    s, c, b, h = (d[k] for k in ("stars", "contract", "bridge", "hosted"))
    check_flags(s["owner_reference"], True)
    check_flags({"hypotheses": c["candidate_under_unmodified_checker_hypotheses"],
                 "conclusions": c["candidate_under_unmodified_checker_conclusions"]}, True)
    check_flags(c["proof_only_original_D_bridge"], False)
    check_flags(b["owner"]["candidate"], True)
    check_flags(b["owner"]["virtual_bridge"], False)
    require(c["semantic_H2"] is True and c["semantic_K_equals_D"] is True, "semantic contract")
    require(c["columns"] == c["independent_D_columns"] == b["owner"]["candidate"]["columns"] == 661, "dirty-column scope")
    n = [int(x, 16) for x in c["semantic_N_hex"]]
    require(len(n) == 111 and n == [int(x, 16) for x in b["compensation_rows_hex"]], "same semantic compensation")

    # Bind the hosted receipt to the actual PR1122 word and exact PR1311 receipt.
    require(raw["word"] == raw["bridge_word"], "same candidate bytes")
    word_sha = sha(raw["word"])
    require(word_sha == b["candidate_sha256"] == h["word_sha256"] == h["parent"]["word_sha256"], "word binding")
    require(sha(raw["bridge"]) == h["semantic_bridge_receipt_sha256"], "bridge receipt binding")
    word = json.loads(gzip.decompress(raw["word"]))
    adds = sum(len(g[2]) for sec in "DABC" for g in word[sec]) + sum(map(len, word["scatter"]))
    old, new = c["candidate_bill"], b["bills"]["candidate"]
    require(s["words"]["candidate"]["literal"]["native_ADDs"] == old["ADDS"] == 11500, "PR1062 count")
    require(adds == new["ADDs"] == h["native"]["common_frame_ADDs"] == 10652, "PR1122 count")
    require(old["profile"] == new["profile"] == c["baseline"]["profile"], "unchanged local profile")
    require(old["frame_paths_sha256"] == new["frame_paths_sha256"] == c["baseline"]["frame_paths_sha256"], "unchanged frame paths")
    require(sum(int(r) * count for r, count in new["profile"].items()) == old["rank_mass"] == new["rank_mass"] == 5129, "local rank mass")

    invoice, hosted = h["invoice"], h["hosted"]
    require(invoice["profile"] == hosted["profile"], "hosted invoice profile")
    require(sum(invoice["profile"].values()) == invoice["paid_calls"] == 904896, "paid children")
    require(sum(int(r) * count for r, count in invoice["profile"].items()) == invoice["rank_mass"] == hosted["rank_mass"] == 1808352, "hosted rank mass")
    require(hosted["hosted_residuals"] == 126432 and hosted["bank_assignments"] == 0, "hosting scope")
    require(hosted["emitted_events"] == 3911328, "instruction count")
    require(invoice["charged_prefix_bits"] == 192 and invoice["charged_two_level_bits"] == 512, "charged precision")
    require(invoice["prefix_bits"] == 176 and invoice["two_level_bits"] == 390, "unrounded precision")
    require([s["formal_columns_checked"] for s in h["stages"]] == [883, 1327], "five/nine-stage evidence")

    selected, assembly = d["selected"], d["assembly"]
    require(selected["certificate"] == FILES["assembly"] and selected["certificate_sha256"] == sha(raw["assembly"]), "selected certificate binding")
    require(assembly["bit_supplier"]["pr"] == 589 and assembly["bit_supplier"]["commit"] == "a5afc8c6169ea61ba7c51dfd3cade02cc7b13b46", "selected supplier remains PR589")
    require(assembly["bit_lower"] == invoice["bit_lower"] and assembly["binding"] == "complex", "unchanged bit saving")
    require(b["hosted_admission"] is False and h["no_selected_change"] is True, "receipt scopes distinguished")
    require(all(x["new_kappa"] is False for x in (c, b, h, invoice)), "no new exponent claim")
    return {
        "kind": "source-bound navigation evidence, not a new supplier replay",
        "retained_chain": chain,
        "candidate_sha256": word_sha,
        "semantic_compensation_rows": len(n),
        "syntactic_failures": [OLD_H2, "K_equals_D"],
        "virtual_bridge_all_flags": True,
        "local_ADDs": {"PR1062": old["ADDS"], "PR1122": adds},
        "unchanged_local_rank_mass": new["rank_mass"],
        "hosted_helpers": hosted["hosted_residuals"],
        "hosted_banks": hosted["bank_assignments"],
        "hosted_instructions": hosted["emitted_events"],
        "hosted_paid_children": invoice["paid_calls"],
        "precision_used_and_charged": [[176, 192], [390, 512]],
        "selected_bit_pr": assembly["bit_supplier"]["pr"],
        "bit_saving": invoice["bit_lower"],
        "new_kappa": False,
    }


def controls(data, raw):
    # Mutate after source admission to exercise relationships, not only hashes.
    mutations = [
        ("wrong hosted word", ("hosted", "word_sha256"), "0" * 64, "word binding"),
        ("wrong bridge receipt", ("hosted", "semantic_bridge_receipt_sha256"), "0" * 64, "bridge receipt binding"),
        ("literal H2 confused with semantic H2", ("bridge", "owner", "candidate", "hypotheses", OLD_H2), True, "H2 syntax distinguished"),
        ("incomplete virtual bridge", ("bridge", "owner", "virtual_bridge", "conclusions", "J_identity"), False, "inherited conclusion flags"),
        ("changed local profile", ("bridge", "bills", "candidate", "profile", "1"), 1324, "unchanged local profile"),
        ("understated invoice profile", ("hosted", "invoice", "profile", "1"), 381023, "hosted invoice profile"),
        ("lowered precision charge", ("hosted", "invoice", "charged_prefix_bits"), 176, "charged precision"),
        ("unadopted word called selected", ("assembly", "bit_supplier", "pr"), 1122, "selected supplier remains PR589"),
    ]
    for name, path, value, expected in mutations:
        changed = copy.deepcopy(data)
        node = changed
        for key in path[:-1]:
            node = node[key]
        node[path[-1]] = value
        try:
            check_evidence(changed, raw)
        except ValueError as error:
            require(str(error) == expected, "control rejected for unrelated reason: " + name)
        else:
            raise ValueError("control accepted: " + name)
    return [m[0] for m in mutations]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="regenerate only this package's RESULT.json")
    args = parser.parse_args()
    data, raw = load_inputs()
    result = check_evidence(data, raw)
    result["controls_rejected"] = controls(data, raw)
    path = HERE / "RESULT.json"
    if args.write:
        path.write_text(json.dumps(result, indent=2) + "\n")
    else:
        require(canonical(result) == canonical(json.loads(path.read_bytes())), "navigation receipt mismatch")
    print("PASS_R439_SEMANTIC_D_NAVIGATION chain=5 controls=8 selected_bit=589 no_new_kappa")


if __name__ == "__main__":
    main()
