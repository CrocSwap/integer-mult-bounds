# Five-product Toom-3 with only Gaussian-dyadic interpolation

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped algebraic proof and explicit restoring construction,
with exact finite corroboration. No new kappa or selected-frontier change.

The Gaussian square `0, 1, i, 1+i`, together with infinity, replaces the
odd-denominator interpolation in Gonzalo Mier's
[PR3974](https://github.com/CrocSwap/integer-mult-bounds/pull/3974)
Toom-3 screen. Five products still recover all five coefficients of the
product of two degree-two polynomials. The evaluation matrix has
determinant 2, and every inverse entry belongs to `(1+i)^(-1) Z[i]`.
No odd division is required. Height one in `1+i` is optimal among
integral point-evaluation schemes with Gaussian-dyadic linear decoding.

The literal word preserves six input fields, adds the convolution to
five arbitrary dirty outputs, and restores two initially clean fields.
It pays exactly five additive PRODUCT calls, sixty coefficient ADDs
and four SCALEs. A coefficient ADD is a charged macro with its explicit
Gaussian-integer coefficient. This is not a scalar-operation speedup
comparison with PR3974. Two SCALEs multiply by associates of `1+i`;
two divide by them exactly. All intermediate data remain Gaussian
integers on the declared boundary. Encoding the dirty outputs before
the five calls avoids product-scratch uncomputation.

[PROOF.md](PROOF.md) gives the complete contract, twelve-ADD decoder,
restoration proof, denominator obstruction and standard bilinear-rank
proof that five products are necessary. [circuit.py](circuit.py) emits
the complete 69-instruction word; [verify.py](verify.py) checks it against
separate schoolbook and rational-matrix oracles.

## Reproduce

From the repository root, with the CPython 3.12 standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/gaussian-dyadic-toom3/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/gaussian-dyadic-toom3/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/gaussian-dyadic-toom3
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/gaussian-dyadic-toom3 --check-source-history
```

Another CPython 3.12 executable may replace the local path. The last
command requires committed package bytes and full Git history. The
scientific checker is read-only and Git-free. It prints a generated
SHA256-bound receipt with `PASS_GAUSSIAN_DYADIC_TOOM3`.

Both normal and optimized checks cover all 25 inverse entries, five
encoder and five decoder columns, 36 real/imaginary tensor coefficient
cases, ten dirty-output columns, 988 complete endpoint fixtures and
all 69 single-instruction omission controls. Complete inverse checks
cover the 729 real cube and 257 complex fixtures as described in the
proof. Five invalid entrances and one inexact division reject.
Warning-strict execution and an AST function-size check remain active
under optimization. The written proofs provide the universal quantifiers.

## Limits and predecessor credit

The result removes an arithmetic denominator, not the missing physical
interface. Chris R / Clear1nsight's
[PR3992](https://github.com/CrocSwap/integer-mult-bounds/pull/3992)
already excludes the specified same-width Toom-only replacement for
the first historical nine-climb group. The new interpolation supplies
no extra information channel and does not bypass that obstruction.
No selected-provider convolution sub-tensor or new native supplier is
claimed. The two clean fields are an explicit resource premise.
Their admission, coefficient access, compatible frames, PRODUCT
implementation, physical routing, precision, stock and complete
recursive/outer invoice remain unpriced. All five selected framework
assumptions retain their status. Independent human and formal
proof-kernel review are unclaimed.

The executable accepts scalar Gaussian-integer entrances through 4096
bits per component. Its output can exceed that cap, so a later API call
must check its own entrance bound. The mathematical proof has no bit
cap. Arbitrary dirty evaluation scratch is unsupported. The denominator
obstruction assumes integral point evaluations; it does not exclude
non-evaluation algorithms or nonintegral input encoders. The five-product
lower bound is the standard bilinear model, not an arbitrary-circuit
lower bound. No native or selected cold replay, Lean or Docker ran.

Credit Gonzalo Mier for the source screen and missing embedding question;
Chris R / Clear1nsight for the typed-boundary obstruction; Josie Elliston,
Arham Tahir and the retained PR1094, Clifford and Toom-screen lineage.
Classical Toom-Cook evaluation, Lagrange interpolation and tensor
flattening retain their credit. No global literature priority for
complex Toom formulas is claimed. Predecessor code, numerical counts
and scientific verifiers are not replayed or audited by this package.

Canonical base is `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority
revision 8, selected PR6030. [SOURCES.json](SOURCES.json) pins provenance
only; no predecessor executable or pending Git object is a runtime
dependency. [TASK.json](TASK.json) records the changed side-result scope
and the [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19372301).
Main/general-form searches, live open PRs, handoffs, active Discussions,
recent account work and local reservations were checked. Arbitrary
historical diffs and unpublished work remain coverage limits.

## Open next questions

1. Can a genuine bilinear convolution consumer use this interface with a
   favorable complete paid invoice? First specify its exact coefficient
   triples, five outputs, bypasses and native product semantics. The
   missing physical caller and signed invoice block an algorithmic gain.
2. Can the five-call advantage survive arbitrary dirty evaluation scratch
   or fully charged clean-field admission? First state that workspace
   contract and charge every extra product and field pass. This package
   provides neither a dirty-scratch construction nor a clean-field tariff.

The structured questions and blockers are in [TASK.json](TASK.json).
