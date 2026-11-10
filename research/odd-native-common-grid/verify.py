"""Source-authenticated dual-method replay; no native or supplier admission.

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from __future__ import annotations

import ast
from hashlib import sha256
from pathlib import Path
import gzip
import json
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from audit_bounds import caller_bounds, ceil_log2, require, word_bounds
from audit_controls import controls, rejects
import independent_bounds as independent


def authenticate():
    manifest = json.loads((HERE / "SOURCE-BYTES.json").read_text())
    require(manifest["head"] == "4e13b7acdbea1c9f12aa88126435360eecea7401", "exact candidate head")
    for entry in manifest["files"]:
        raw = (HERE / entry["path"]).read_bytes()
        require(len(raw) == entry["bytes"] and sha256(raw).hexdigest() == entry["sha256"],
                "source bytes: " + entry["path"])
    raw = (HERE / "source/data/caller.json").read_bytes()
    wanted = sha256(raw).hexdigest()
    mutant = bytes([raw[0] ^ 1]) + raw[1:]
    require(sha256(mutant).hexdigest() != wanted, "single-byte source corruption detected")
    return manifest


def source_parameters(text):
    # Only inspect literal declarations. Never execute the source check.py.
    result = {}
    for node in ast.parse(text).body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if isinstance(target, ast.Tuple) and all(isinstance(x, ast.Name) for x in target.elts):
            names = [x.id for x in target.elts]
            if names == ["cutoff", "floor", "power", "offset"]:
                require(isinstance(node.value, ast.Tuple), "literal source parameter tuple")
                result.update(zip(names[:3], [ast.literal_eval(x) for x in node.value.elts[:3]]))
    require(result == {"cutoff": 11, "floor": 12, "power": 1920}, "retained separation parameters")
    return result


def main():
    source = authenticate()
    word = json.loads(gzip.decompress((HERE / "source/data/word.json.gz").read_bytes()))
    caller = json.loads((HERE / "source/data/caller.json").read_text())
    expected = json.loads((HERE / "EXPECTED-BOUNDS.json").read_text())
    bounds = {"word": word_bounds(word), "caller": caller_bounds(caller)}
    require(json.dumps(bounds, sort_keys=True) == json.dumps(expected, sort_keys=True),
            "complete exact source envelope receipt")

    # Independently authored fixed-grid integer and positive transfer-matrix
    # engines, not a second invocation of the rational row interpreter.
    iw, ic = independent.word_run(word), independent.caller_run(caller)
    for key in ("dyadic_height", "maximum_scaled_mass", "coefficient_visits"):
        require(iw[key] == bounds["word"][key], "independent word: " + key)
    require(iw["odd_scale_lcm"] == 1125 and iw["numerator_bits"] == 24, "independent scale and numerator")
    for key in ("maximum_mass", "denominator_height", "pre_joint_height"):
        require(ic[key] == bounds["caller"][key], "independent caller: " + key)
    from fractions import Fraction
    require(ceil_log2(Fraction(ic["pre_joint_mass"])) == bounds["caller"]["pre_joint_mass_bits"],
            "independent joint entrance mass")
    rejected_scales = {str(scale): rejects(lambda s=scale: independent.word_run(word, scale=s),
                        "integer grid rejection at event " + str(event))
                       for scale, event in ((225, 1101), (375, 36915))}

    threshold = independent.threshold_run()
    params = source_parameters((HERE / "source/check.py").read_text())
    require(caller["ambient_rank"] == 153 and 153 < 2**8
            and 8*params["power"] < threshold["H"], "compiler carrier below fixed N")
    A = max(bounds["caller"]["denominator_height"],
            bounds["caller"]["pre_joint_height"] + bounds["word"]["dyadic_height"])
    B = max(bounds["caller"]["mass_bits"],
            bounds["caller"]["pre_joint_mass_bits"] + bounds["word"]["scaled_mass_bits"])
    require((A, B) == (178, 161), "source-specific unfinished-context bounds")
    require(2 * max(A, B) + 1 == 357, "same exact threshold coefficient")
    c = controls(word, caller)
    receipt = {"source_head": source["head"], "source_files": len(source["files"]),
               "word_coefficient_visits": bounds["word"]["coefficient_visits"],
               "caller_events": bounds["caller"]["events"], "independent_minimum_scale": iw["odd_scale_lcm"],
               "A": A, "B": B, "threshold": threshold,
               "per_caller_scale_scans": 2*bounds["word"]["public_fields"]*bounds["caller"]["operations"]["J"],
               "rejected_scales": rejected_scales, "controls": c,
               "native_endpoints_reproved": False, "full_supplier_admitted": False, "new_kappa": False}
    require(receipt["per_caller_scale_scans"] == 52272, "complete per-call scale/unscale inventory")
    print("PASS_ODD_NATIVE_COMMON_GRID " + json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
