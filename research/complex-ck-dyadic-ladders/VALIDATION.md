# Validation and handoff

Environment: Linux x86_64, CPython **3.12.14**, standard library only.
Validation date: **2026-10-13 UTC**.
Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.

## Completed checks

1. `python -I -B research/complex-ck-dyadic-ladders/verify.py`
   passes exact source/SPEC bindings, all 743 blocks, the independent full
   block census and arithmetic price check, 716+9 arbitrary input columns in
   both complete scalar projections, original positive-envelope reproduction,
   candidate envelope domination, private clearing, child histograms and
   13 negative controls. The committed receipt matches every field.
2. The same command with `-O` passes. Assertions are not used as checks in
   this package. One measured optimized run took **2.754 seconds** and
   **56,204 KiB** maximum resident memory. This describes verifier execution,
   not multiplication performance.
3. `python -I -O -B research/complex-ck-dyadic-ladders/check_columns.py`
   passes the independently implemented flat-vector replay of **11,610**
   local input columns, and **743** per-block missing-final-clear controls.
4. A minimal copied checkout, containing only the package and the eight
   pinned source inputs, passed from `/tmp` in a path containing spaces.
   Both gzip inputs were recompressed at level 1 with a different timestamp;
   the full isolated optimized replay still passed.
5. The copied checkout rejected a changed selected-source byte, a corrupted
   reported saving, and an existing `--write-receipt` output. The existing
   output remained byte-identical. The original checkout was not mutated.
6. `make selected-record-check` passes. Source/receipt replays do not modify
   repository inputs. Final staged whitespace and source syntax checks pass.

The separate block checker shares the circuit constructor, but not the main
checker's normalized-coefficient proof logic, sparse row interpreter or prefix
engine. It is an independently implemented verification path by the same AI
agent, with no independent-person review claim.

## Concurrent scope check

The initial live metadata scan covered 544 open PRs through #725. The next
scan reached #751. #739 at `abb9825202dba6f9bc95c7df8d12d86088fdff1a`
published the same scale-reuse idea for JP8 forward cleanup during this work;
it is explicitly credited. This contribution adds CK in both directions and
the backward zero-frame preconditioning domain. #734, #750 and #751 were
also inspected and are distinguished in README.md. No pending source is
imported. The final pre-submission metadata refresh reached #767 and inspected
#755's README at `a1dd9f819102c40e0b5e4a75215cf69ee864f480`. Its JP8
equal-magnitude reuse also covers backward preconditioning; that phase
extension is explicitly credited. Our distinct coverage is CK varying
magnitudes with original Horner initialization and the stated exact checks.

No pinned sprint issue existed; the claim and result are recorded locally.
No maintainer branch, selected-frontier record or existing supplier is edited.

## Verification boundary

Full repository `make verify`, fresh selected-provider construction,
Clifford/native-frame/wrapper regeneration, global hosting/invoice/assembly,
Lean and remote CI were not run. The isolated patch adds one research package
and changes no existing source or selected certificate. It proves/checks a
finite scalar-block substitution under the stated common-frame interface;
it does not settle the inherited all-size multiplication obligations.
