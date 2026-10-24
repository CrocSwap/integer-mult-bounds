"""Bind the corrected producer and check its finite affine witnesses."""

import argparse
from fractions import Fraction as F
from hashlib import sha256
import gzip
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
REVIEW = HERE.parent / "unitary-code-closure-review-20261020"
PRODUCER = HERE.parents[1] / "unitary-code-closure-20261020"
PINS = {
    REVIEW / "FREEZE.json": "b3fc9ddc6fdc4cc6c2226b3b9fa101abdb21d22e50ceb3d6c9cefa9280062deb",
    REVIEW / "check_review.py": "c86a3655dcc6104be95845422a97407e0c389f1cac83c504d25b10cac7c7de03",
    PRODUCER / "CLOSURE.md": "63c0deeb7e13b359ca410dfb085e1a89866aa87383d6bd1cec02cba688a4ce3e",
    PRODUCER / "check_closure.py": "45d1e215c4dc6f7735deaed0d9df57cf3efa83a0bc4e354c43375187cbe7f01e",
    PRODUCER / "bound-normal/CHECKS.json": "f1e418155b89f8add0f066c80da2ab3a1120e6d78f047753e7e0698daf506a3a",
    PRODUCER / "bound-normal/PATH-SIGNATURES.json.gz": "053b09b693cef52a33b7f15ccb0c5697466bd123f3b4e0bbb0318fe2e674ed46",
    PRODUCER / "bound-normal/WIDTH-THREE-WITNESSES.json.gz": "09f5ba960ecf9eb965e1ccb94848fcbc36e1d68319502b9378d94c27a7401eca",
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def digest(raw):
    return sha256(raw).hexdigest()


def write_json(path, value):
    raw = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()
    path.write_bytes(raw)
    return digest(raw)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    manifest = {}

    def read(path, pin=None):
        raw = path.read_bytes()
        if pin is not None:
            need(digest(raw) == pin, "Pinned file " + path.name)
        manifest[str(path)] = digest(raw)
        return raw

    for path, pin in PINS.items():
        read(path, pin)
    freeze = json.loads((REVIEW / "FREEZE.json").read_bytes())
    for relative, pin in freeze["files"].items():
        read(REVIEW / relative, pin)
    spec = importlib.util.spec_from_file_location("independent_representation_review", REVIEW / "check_review.py")
    lib = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lib)
    ours = json.loads((REVIEW / "CHECKS.json").read_bytes())
    our_witnesses = json.loads((REVIEW / "COMMUTATOR-WITNESSES.json").read_bytes())
    our_witnesses = {("/".join(w["variant"]), w["output_port"]): w for w in our_witnesses}
    our_signatures = json.loads((REVIEW / "TWO-TAG-SIGNATURES.json").read_bytes())
    source = {}
    for name, (path, pin) in lib.PINS.items():
        raw = read(path)
        decoded = gzip.decompress(raw) if path.suffix == ".gz" else raw
        need(digest(decoded) == pin, "Exact source payload")
        source[name] = json.loads(decoded)
    data = {}
    for name in ("CHECKS.json", "PATH-SIGNATURES.json.gz", "WIDTH-THREE-WITNESSES.json.gz"):
        raw = read(PRODUCER / "bound-normal" / name)
        need(raw == read(PRODUCER / "bound-optimized" / name), "Normal and optimized producer bytes")
        data[name] = json.loads(gzip.decompress(raw) if name.endswith(".gz") else raw)
    report = data["CHECKS.json"]
    need(report["checker_sha256"] == PINS[PRODUCER / "check_closure.py"] and
         report["status"] == "PASS_ACTUAL_FRESH_STAGE_PATH_SEPARATION", "Completed corrected producer")
    paths = data["PATH-SIGNATURES.json.gz"]
    need([row[:4] for row in paths] == our_signatures, "Every route signature agrees with the independent proof")
    records = {(row["stage"], row["port"]): row for row in source["views"]["entries"]}
    rho = {key: row["route_columns"] for key, row in records.items()}
    delta = {key: row["literal_stage_alignment"]["exit_X"] for key, row in records.items() if key[0]}

    def point(p, j, r, value, include_outer=True):
        stages = [(1, r), (1, j), (2, j)] + ([(2, p)] if include_outer else [])
        for key in stages:
            value = lib.act(rho[key], value) ^ delta[key]
        return value

    for j, r, image2, image1, inner_shift, outputs in paths:
        need(inner_shift == point(0, j, r, 0, False), "Inner affine translation")
        need(outputs == [point(0, j, r, x) for x in (0, lib.E2, lib.E1)],
             "Literal ordered affine path on the common input")
    need(len(paths) == 12544 and report["single_physical_input_affine_outputs"] == 12544,
         "All physical paths")
    families = {"C": lib.sparse(source["unitary"]["code"]),
                "Cstar": lib.sparse(source["unitary"]["inverse_and_adjoint"])}
    witnesses = data["WIDTH-THREE-WITNESSES.json.gz"]
    for witness in witnesses["basis_witnesses"]:
        p, k = witness["output_port"], witness["input_port"]
        c0, c1, c2 = [families[name] for name in witness["variant"].split("/")]
        need(witness["input_columns"] == [0, lib.E2, lib.E1], "Common physical basis input")
        need(len(witness["outputs"]) == 2, "Two selected nonzero outputs")
        for item in witness["outputs"]:
            j, r = item["path"]
            coefficient = lib.mul(c2[p][j], lib.mul(c1[j][r], c0[r][k]))
            need(tuple(map(F, item["coefficient"])) == coefficient != lib.ZERO, "Actual Gaussian path coefficient")
            need(item["output"] == [point(p, j, r, x) for x in witness["input_columns"]],
                 "Actual physical output coordinates")
        need(witness["outputs"][0]["output"] != witness["outputs"][1]["output"], "Distinct output coordinates")
    powers = (lib.ONE, (F(0), F(1)), (F(-1), F(0)), (F(0), F(-1)))
    for witness in witnesses["commutator_witnesses"]:
        own = our_witnesses[witness["variant"], witness["output_port"]]
        pairs = {"input_port": "input_port", "path": "intermediate_ports", "coefficient": "coefficient",
                 "input_characters": "input_characters", "output_characters": "output_characters",
                 "output_line_pulled": "pulled_output_line",
                 "output_exponent": "left_i_power", "input_exponent": "right_i_power"}
        need(all(witness[a] == own[b] for a, b in pairs.items()), "Independent commutator witness agrees")
        p = witness["output_port"]
        j, r = witness["path"]
        shift = point(p, j, r, 0)
        sign = (-1) ** sum(lib.dot(shift, x) for x in witness["output_characters"])
        difference = lib.add(powers[witness["output_exponent"]],
                             tuple(-x for x in powers[witness["input_exponent"]]))
        coefficient = lib.mul(tuple(map(F, witness["coefficient"])), lib.mul((F(sign), F(0)), difference))
        need(witness["affine_shift"] == shift and witness["affine_sign"] == sign and
             tuple(map(F, witness["physical_commutator_coefficient"])) == coefficient != lib.ZERO,
             "Literal affine commutator coefficient")
    need(len(witnesses["basis_witnesses"]) == len(witnesses["commutator_witnesses"]) == 896,
         "All eight variants and every output row")
    for variant, profile in report["routed_variant_profiles"].items():
        need(profile["operator_terms"] == ours["actual_profiles"][variant]["total_terms"] and
             profile["row_term_histogram"] == ours["actual_profiles"][variant]["row_term_histogram"],
             "Exact support profile agreement")
    need(report["logical_path_separation_minimum_width"] == 2 and
         report["physical_path_and_commutator_minimum_width"] == 3, "Exact width limits")
    need(all(digest(Path(path).read_bytes()) == pin for path, pin in manifest.items()), "All files unchanged")
    pin = write_json(args.out / "SOURCE-MANIFEST.json", manifest)
    receipt = {"status": "PASS_CORRECTED_PRODUCER_BINDING", "source_manifest_sha256": pin,
               "producer_proof_sha256": PINS[PRODUCER / "CLOSURE.md"],
               "producer_checker_sha256": PINS[PRODUCER / "check_closure.py"],
               "producer_receipt_sha256": manifest[str(PRODUCER / "bound-normal/CHECKS.json")],
               "literal_affine_paths_checked": len(paths),
               "basis_column_witnesses_checked": len(witnesses["basis_witnesses"]),
               "physical_commutator_witnesses_checked": len(witnesses["commutator_witnesses"]),
               "cover_lift_and_monomial_restriction": "Proved in BINDING.md.",
               "native_word_replayed": False, "general_decoder_lower_bound": False}
    write_json(args.out / "CHECKS.json", receipt)
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
