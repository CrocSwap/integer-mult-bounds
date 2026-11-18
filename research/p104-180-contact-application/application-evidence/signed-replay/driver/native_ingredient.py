# SPDX-License-Identifier: Apache-2.0
"""Fresh transposed native verification and retained 18-call ingredient invoice."""

from fractions import Fraction
import gzip
from hashlib import sha256
import independent as engine
from interval_gate import moment, show
import json
from pathlib import Path


def main():
    folder = Path(__file__).resolve().parent
    config = json.loads((folder / "INGREDIENT-INPUT.json").read_bytes())
    raw = gzip.decompress((folder.parent / "WORD.json.gz").read_bytes())
    word = json.loads(raw)
    canon = json.dumps(word, sort_keys=True, separators=(",", ":")).encode()
    candidate = sha256(canon).hexdigest()
    assert candidate == config["candidate_canonical_sha256"]
    bound_caller = folder / "admission-source/data/caller.json"
    assert sha256(bound_caller.read_bytes()).hexdigest() == config["retained_18_caller_sha256"]
    caller = json.loads(bound_caller.read_bytes())
    assert caller["stages"] == 18 and [e[1] for e in caller["events"] if e[0] == "J"] == list(range(1, 19))
    native = engine.native(word)
    assert not native["bad_inputs"] and native["lifetimes"] == config["clear_lifetimes"]
    assert native["owned_peak"] == 50 and native["events"] == len(word["program"])
    # The last nontrivial scalar has no later scalar row repair.
    mutant = max(i for i, e in enumerate(word["program"])
                 if e[0] in ("ADD", "SCALE") and e[1] < word["public"])
    bad = engine.native(word, mutant)["bad_inputs"]
    assert bad, "Deliberate coefficient fault must change an arbitrary-input row"
    inv = engine.invoices(word, caller, native)
    assert inv["S"] > 0
    hist = {r: inv["T"].get(r, 0) - inv["P"].get(r, 0) for r in inv["T"].keys() | inv["P"].keys()}
    step = 10**16
    lower = int(Fraction(inv["raw_crossing"]) * step)
    lo, hi = Fraction(lower, step), Fraction(lower + 1, step)
    ml, mh = moment(hist, lo), moment(hist, hi)
    assert ml[0] > 0 and mh[1] < 0
    ordinary = engine.ordinary(word, caller, native)
    assert ordinary["margin_to_billion"] > 0
    result = {"status": "PASS_TRANSPOSED_NATIVE_18_INGREDIENT", "word_canonical_sha256": candidate,
              "native": native, "invoice": inv, "gate": {"BIT_pin": config["bit_pin"]},
              "ordinary": ordinary, "ingredient_18_caller_sha256": config["retained_18_caller_sha256"],
              "unmodified_dyadic_invoice_bracket": [str(lo), str(hi)],
              "sign_margins": [show(ml), show(mh)],
              "bad_scalar_control": {"event": mutant, "bad_inputs": bad},
              "physical_evidence_sha256": config["physical_evidence_sha256"],
              "clear_evidence_sha256": config["clear_evidence_sha256"],
              "scope": "Fresh all-input transposed native endpoint and separate literal 18-call arithmetic."}
    with (folder.parent / "RESULT.json").open("x") as out:
        json.dump(result, out, indent=2, sort_keys=True)
        out.write("\n")
    print(result["status"], candidate, flush=True)


if __name__ == "__main__":
    main()
