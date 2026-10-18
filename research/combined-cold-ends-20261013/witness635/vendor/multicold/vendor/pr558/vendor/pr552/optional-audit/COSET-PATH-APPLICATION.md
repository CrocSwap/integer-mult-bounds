# Independent path-transfer review of the twelve weighted-coset substitutions

This review supplies an independent exact scalar audit of the selected provider. It does not claim an additional numerical gain, a new physical-frame theorem, or a replay of the unchanged bit supplier. The source hashes are in COSET-SOURCE-BINDING.json; the numerical receipt is COSET-PATH-REVIEW.json.

## Sufficient transfer statement

Let a finite linear straight-line circuit have initial coordinates split into protected inputs P and cold helper dirt C. Expand each assignment into a new register version, retaining unchanged versions by unit-weight edges. The coefficient of an initial coordinate in any output is the sum of all directed path weights from that input to the output. Induction on assignment order proves this statement: a scale multiplies the old paths, and an addition joins the old destination paths with the scaled source paths. Thus exact propagation of coefficient rows computes the boundary transfer matrix over the dyadic rationals, including all long paths and cancellation.

Suppose a source rewrite at an addition preserves the destination and gate coefficient/frame, and its current prefix error has zero restriction to P. Subsequent linear maps cannot introduce a protected component into that error. Therefore the final difference is supported on C. If the retained compiler subtracts the actual cold response and then performs the inverse of the actual background program, the two compensated endpoints agree on every initial column and restore all background dirt. This conclusion requires checking the actual changed program, not merely the clean-input action or a source equality before earlier rewrites. When target decoding occurs after the background circuit it is included in the boundary map before deriving the cold response.

In this witness P includes all 112 source coordinates, all 112 initial target coordinates, and 212 warm helper coordinates. The actual raw section named `precondition` is a final target decoder; it is included after A, cut, B. It is not mistaken for the compiler's initial cold-dirt compensation. The latter must be regenerated and charged by the physical pipeline.

## Independent finite application

A fresh C++ implementation, using Boost cpp_int dyadic arithmetic and no imported nomination, gk, or suffix-derivative routines, computes both complete 728-column boundary matrices. All 48,832 entries on 112 target rows and 436 protected columns agree exactly. The cold target-response nonzero count falls from 9,756 to 9,132, a saving of 624 entries. This is a compensation-count result, not an independent kappa increment.

It separately reconstructs the current prefix at each of the twelve selected rewrites, incorporating every earlier rewrite, and checks all 728 coefficients of the stated source error. All 8,736 comparisons pass, and each error vanishes on P. The selected A indices are 205, 340, 1555, 1690, 207, 342, 475, 477, 610, 612, 745, and 747.

The portable exporter proves that these exact twelve operations reconstruct the entire candidate A, that all fields other than A and cleanup remain equal, and that the 2,847 cleanup operations are precisely the reverse inverses of the actual nontarget A+B operations, at the full frame. The source audit is bound to candidate raw SHA-256 fd8ea67a1f4e8d754ffe29cc18a12aaa15c1704e58b688895e7ba51eb832b719.

The path-algebra connection is actually used here as an independent exact boundary-transfer and version-error audit. Triangular elimination gives an alternative mathematical derivation of the same boundary matrix: eliminate internal time-expanded vertices, adding incoming times outgoing path weights. This is the relevant Schur/path relationship. The implementation does not separately run a second Schur-complement algorithm, and the earlier attempted register-elimination optimization had no admitted winner. There is one independent implementation, not two independent successful optimization techniques.

Actual physical frame incidence, normalized operator endpoints, coefficient bounds, whole-owner maps and the assembly are checked separately by the changed-provider pipeline. This scalar audit does not replace those checks. Likewise, the source analogy is not a new Lean kernel certificate or a claim of global mathematical originality.

## Optional reproduction

The main verifier need not build this independent optional checker. With Python, a C++17 compiler, and genuine Boost headers installed:

```
python export_coset_paths.py --baseline BASELINE.json.gz --candidate CANDIDATE.json.gz --selection SELECTION.json --out audit-out
c++ -O2 -std=c++17 -I BOOST_INCLUDE audit_coset_paths.cpp -o audit_coset_paths
./audit_coset_paths audit-out/coset-path-input.txt audit-out/COSET-PATH-REVIEW.json
```

Do not compile with NDEBUG: the exact comparisons use C++ assertions. The included coset-path-input.txt is also a complete fixed independent arithmetic input; its SHA-256 is recorded by the source-binding receipt. The exporter accepts paths as arguments and contains no machine-specific locations. No executable binary is required in the submission.
