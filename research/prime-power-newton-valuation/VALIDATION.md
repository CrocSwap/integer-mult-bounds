# Verification and handoff

Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
Branch: `research/seed80-independent-verification`.
Platform: Windows x86-64. Actual interpreter runs: CPython 3.14.7 and 3.12.14.
Python 3.11 is the documented floor; it was not installed or executed here.

## Completed local checks

The commands below were run from the repository root. Here `uv run --no-project`
selects an already installed interpreter; the verifier itself has no uv dependency.

```sh
uv run --no-project python -B -I research/prime-power-newton-valuation/test_verify.py
uv run --no-project python -B -I -O research/prime-power-newton-valuation/verify.py --check research/prime-power-newton-valuation/EXPECTED.json
uv run --no-project --python 3.12 python -B -I -O research/prime-power-newton-valuation/verify.py --check research/prime-power-newton-valuation/EXPECTED.json
uv run --no-project python -B scripts/verify_selected_result.py
```

Results: nine focused tests pass; both optimized interpreter replays report
`PASS 214 primitive embeddings; 10268 exact coefficients; 8 negative controls`;
the selected record, complete original source inventory and proof supplements
retain exact kappa `51110230636731/31250000000000000`. The checker also ran
normally when generating the receipt; the normal and optimized outputs agree.

The tests were written first. The initial five tests failed because the integer
engine was absent, then passed after implementation. The receipt, Eisenstein and
source-pin tests subsequently failed before their features were implemented.
The integral-division test likewise failed before that second extraction method
was added. No failing test or rejected control was described as a theorem failure.

The unchanged PR621 primary verifier was separately run with `-B -I -O`, writing
to the approved external temporary directory. Its complete JSON result equals
`research/prime-power-cyclic-inverse/EXPECTED.json`, not just its PASS field.
Its three checked files retain the SHA-256 pins in `SOURCE.json`.

One scoped AI worker checked the written uniform argument and produced the
proof note. A separate read-only AI reviewer ran all focused tests and the
optimized replay, and additionally compared every coefficient tuple with an
in-memory descending cyclotomic long-division reference. It reported no
correctness finding; its one documentation finding was the then-absent validation
note, supplied here. The shared basis conversion between the two valuation
extractors is disclosed in README and PROOF. No human or proof-assistant review
is claimed.

## Concurrent result comparison

The final open-PR refresh at approximately 05:52 UTC found Hao Yan's #796,
created at 05:47:56 UTC, after this package's local claim. At pinned head
`22902155c7875139e43e4fdf15723142d6709bdd`, its `cyclotomic.py` uses weighted
uniformizer-basis minima and no repeated integral-division extraction.

The exact source receipt was read through `git show` after fetching that head.
Its SHA-256 is `d074f1c2f87324e81cf8aa94784077694230cf35d95f8b0c173755c89f876333`.
Every shared coefficient valuation, primitive power list, hull vertex, root
valuation and multiplicity agrees: twelve radices, 160 embeddings and 5,894
coefficient obligations. Radix 81 adds 54 embeddings and 4,374 coefficients.
The full #796 executable package was not run or certified by this comparison.

To reproduce the comparison, fetch the pinned object once:

```sh
git fetch --no-tags https://github.com/CrocSwap/integer-mult-bounds.git 22902155c7875139e43e4fdf15723142d6709bdd
```

Then run this Python snippet from the repository root (or save it to an external
temporary file and execute it). It consumes the two complete exact receipts:

```python
import hashlib, json, subprocess
from pathlib import Path

package = Path("research/prime-power-newton-valuation")
claim = json.loads((package / "CORROBORATION.json").read_text())
raw = subprocess.check_output([
    "git", "show", claim["source_head"] + ":" + claim["source_receipt"]
])
if hashlib.sha256(raw).hexdigest() != claim["source_receipt_sha256"]:
    raise ValueError("comparison source pin mismatch")
theirs = {c["r"]: c for c in json.loads(raw)["cases"]}
ours = json.loads((package / "EXPECTED.json").read_text())
shared, extra, embeddings, coefficients = [], [], 0, 0
for c in ours["cases"]:
    r = c["radix"]
    if r not in theirs:
        extra.append(r)
        continue
    t = theirs[r]
    roots = [{"multiplicity": s["multiplicity"], "valuation": s["valuation"]}
             for s in t["segments"]]
    if (c["coefficient_valuations"] != t["coefficient_valuations"]
        or c["primitive_powers"] != t["primitive_powers"]
        or c["lower_hull"] != t["vertices"] or c["root_valuations"] != roots):
        raise ValueError("exact shared-receipt mismatch")
    shared.append(r)
    embeddings += len(c["primitive_powers"])
    coefficients += r * len(c["primitive_powers"])
if (shared != claim["shared_radices"] or extra != claim["additional_radices"]
    or embeddings != claim["shared_primitive_embeddings"]
    or coefficients != claim["shared_coefficient_obligations"]):
    raise ValueError("comparison coverage mismatch")
print("PASS PR796: 160 shared embeddings; 5894 shared coefficients; radix 81 added")
```

## Verification boundary

Only this new research package is changed. No existing generator, selected
construction, global ledger or `upstream/` file is edited. The repository-wide
`make verify`, selected cold supplier replay, optional SymPy, Linux execution and
remote CI are **not** claimed. GNU make is not available on this session's PATH;
the scoped Python checks above and unchanged predecessor replay were run directly.

The uniform proof concerns one prime-power polynomial family. Finite replay is
not a proof of all prime powers, archimedean conditioning, a paid exact inverse,
rounded preparation/restoration, recursive hosting, fixed-tape execution or the
conditional integer-multiplication theorem. There is no new kappa or global
optimality claim. The useful handoff is the integral-divisibility evidence and
radix-81 coverage, with explicit credit for #796's concurrent shared result.
