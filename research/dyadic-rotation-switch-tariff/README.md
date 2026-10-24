# Exact optimal switch tariff for dyadic rotations

For N=2^h occupied binary addresses, rotating x to x+c modulo N requires
exactly

    S_h(c) = sum_{k=1}^h 2^(h-k) dist(c, 2^k Z)

hypercube-edge swaps, for every h>=1 and 0<=c<N. An explicit circuit attains
this minimum in h descending bit layers. The sharp worst-case tariff is

    max_c S_h(c) = ((3h+1)2^h-(-1)^h)/9,

attained only at c=(2^h-(-1)^h)/3 and its complement modulo N. They coincide
at h=1. For h=3,c=3 the layer counts are 3,2,4, giving 9 swaps.

This is a scoped combinatorial proof with exact finite corroboration.
[PROOF.md](PROOF.md) gives the construction, the standard Hamming-distance
lower bound, and the maximum/equality proof. The contribution is the exact
rotation tariff and sharp extremal law in this model. Binary carry logic
and the token-swapping distance bound are credited standard ingredients.
No claim of priority over the full routing literature is made.

## Connection and limits

Cinna Davis's [PR #4100](https://github.com/CrocSwap/integer-mult-bounds/pull/4100)
uses bounded-bit switch networks for CRT rotations. Unpaidmoon's merged
[PR #4377](https://github.com/CrocSwap/integer-mult-bounds/pull/4377)
prices generic Beneš compilation and CRT reconstruction. Their statements
are cited context, not replayed deliverables. The present circuit changes
the modulus premise to a full dyadic cycle. It does not implement the
strictly smaller prime-modulus cycle with fixed padded addresses.

The count charges active logical edge swaps. It supplies no sequential-tape
access bound, control-generation tariff, payload-movement bound, CRT repair,
ordinary callee, supplier admission, new kappa or selected-frontier change.
No spare address is available. Longer paths and repeated edge dimensions
are allowed in the optimality comparison. Arbitrary records are routed by
permutation, so the endpoint does not assume zero or clean payloads.

## Reproduce

From the repository root with CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B research/dyadic-rotation-switch-tariff/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/dyadic-rotation-switch-tariff
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/dyadic-rotation-switch-tariff --check-source-history
```

Expected final line is `PASS_DYADIC_ROTATION_SWITCH_TARIFF`. Normal and
optimized runs perform the same checks, with explicit exceptions rather
than removable assertions. The verifier checks all 510 rotations through
h=8, independently computes each initial Hamming-distance sum, enumerates
all offsets through h=12 for the maximum and equality cases, and compares
against an independent full token-permutation BFS through h=3. The BFS
visits 2, 24 and 40,320 states. Eight controls reject omitted switches,
reversed layer order and invalid parameter values. These finite checks
corroborate the universal written proof; they are not its replacement.

`--receipt /absolute/scratch/path.json` writes a generated evidence report
bound to the six package-file SHA256 hashes. No receipt is hand-authored.
The two VERIFY.json commands are bounded to 120 seconds each. The checker
caps widths at 12, direct execution at 8 and BFS at 3. Python allocation is
a documented Power-of-Ten deviation with a factorial state cap of 40,320;
there is no recursion or unbounded queue drain. No Lean or physical tape
replay was run.

## Provenance and overlap

Scientific base is canonical main
`624de9dc66858af0945e5f8a0942488d62280d43`, priority revision 7.
The `uniform-transfer-audit` card is changed from audit to a new exact
routing result under a dyadic modulus premise. The card's historical
`research_baseline.py` command fails with `KeyError: 'bit_lower'` under the
selected schema; the current `research_selected_baseline.py` passes its
source-binding-only check. No selected replay is implied.

The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19134021)
records scope and overlap. The initial remote cache covers 395 open PRs and
3,888 Discussion records at 22:39 UTC on October 22, 2026. Sparse local
cache coverage is incomplete; a separate `git grep` covers all main-tree
top-level research READMEs. Merged PR and exact-term searches found no
same-scope result within that coverage. These searches do not prove novelty.
SOURCES.json pins predecessor prose as historical provenance. The verifier
has no external mathematical input or imported predecessor implementation.

## Open next questions

1. Determine the exact edge-switch tariff of a rotation on x<s<2^h that
   fixes the padded addresses. This reaches the actual CRT modulus premise.
   Start with s=3 at h=2 and compare the Hamming lower bound with an exact
   token-swap search. The full-cycle triangular construction does not apply.
2. Price the dyadic circuit's control generation and record access on one
   fixed tape layout. Start with the h=3,c=3 circuit and count all control,
   scan and payload operations. A logical swap count is not that tariff.

## Credit

This contribution was produced by Nick Petalas. Cinna Davis supplies the
CRT routing context and unpaidmoon the generic evaluator predecessor.
The Hamming-distance lower bound is standard; PROOF.md cites Miltzow,
Narins, Okamoto, Rote, Thomas and Uno. No predecessor source is copied or
rechecked here. Independent human and formal proof-kernel review are
unclaimed. Apache-2.0.
