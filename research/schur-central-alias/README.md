# Central Schur classes first alias at pivot dimension four

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped algebraic proof with exact finite corroboration. In the
sharp nilpotent identity-pivot Schur family, over every characteristic-two
field, two ordered residual pairs with the same pivot size and four original
sector dimensions can have identical complete central similarity classes
without being simultaneously conjugate. The least pivot size is **four**;
the least residual and ambient dimensions are **fourteen** and **eighteen**.

The witness has original sector dimensions (4,4,4,6) and compressed products
J3(0)+J1(0) and J2(0)+J2(0). Both central operators have full Jordan form
J2(0)^4 + J1(0)^6. The ranks of (S+T)^3 are two and zero, which distinguish
the ordered states. Consequently a complete central-class key cannot safely
deduplicate these ordered states. This is a local algebraic obstruction,
with no new kappa, physical cost saving or supplier-admission claim.

[PROOF.md](PROOF.md) gives the argument and explicit original headers. The
central class retains precisely the odd positive power ranks of H; the sum
S+T retains every power rank. The minimality proof uses only the nilpotent
partitions through size four and the credited whole-pair rigidity theorem.

Credit Malik Safwan / ssafwann [#5267](https://github.com/CrocSwap/integer-mult-bounds/pull/5267)
for the nilpotent model, admissibility and rigidity; Ali Romman
[#5287](https://github.com/CrocSwap/integer-mult-bounds/pull/5287) for the
already complete characteristic-two central law; Mihir Srivastava
[#5360](https://github.com/CrocSwap/integer-mult-bounds/pull/5360) for the
general-H ordered gluing boundary; Nick Petalas #4746/#4597, MatShep #4762,
codyw912 #4735, and the retained Ryanson Jonathan, lee-phys, Cinna Davis,
source527, commdata2338 and Jose Manuel lineage. Those results are cited
premises, not replay deliverables. Classical nilpotent power-rank facts are
not claimed as new.

## Reproduction

From the repository root, using CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/schur-central-alias/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/schur-central-alias/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/schur-central-alias
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/schur-central-alias --check-source-history
```

Other machines may substitute their CPython 3.12 path. Expected direct marker:
`PASS_SCHUR_CENTRAL_ALIAS`. The verifier writes no files. Its computed receipt
binds all package source hashes and a digest of both literal witness pairs,
the explicit central intertwiner, the finite minimality census and controls.
A receipt is printed, not hand-written or accepted as a mathematical premise.

The exact checks construct two complete eighteen-dimensional original
headers and fourteen-dimensional residual pairs, verify the common identity
pivots, prescribed products, idempotence, original commutation and sharp
commutator rank eight, and compare eight power ranks of each sum and centre.
An invertible central intertwiner is checked by literal multiplication.
All eleven nilpotent partitions of sizes one through four and all fourteen
same-size unordered comparisons give exactly the displayed collision.
Eight controls cover invalid partitions, singular inversion, a non-square-zero
central input, a different central class and the ordered-state separator.
Normal and optimized checks enforce the same explicit exceptions.

The all-field proof relies on the written argument and cited normal form;
finite evidence is not independent human or formal proof-kernel review.
The selected source-binding orientation passed at #7000. No predecessor
scientific suite, selected cold replay, native replay, Lean or Docker ran.
Physical access, movement, precision, stock, coefficient preparation,
restoration, dispatch, a complete supplier invoice and all five selected
framework assumptions remain outside scope.

## Engineering and overlap

The autonomous local run stopped at this first obstruction. The formal-interface-
lemma card is changed to a written state-information side result; no formal
caller binding is claimed. The baseline card example was run before the
experiment. New code uses bounded finite domains, no recursion, functions
below sixty lines and warning-strict normal/optimized checks. CPython allocation
is a Power of Ten rule-three deviation: the hard-coded largest matrix is
18 by 36 during augmented elimination, with bounded live fixture collections.
No external static analyzer is claimed. The verifier imports no predecessor
code and has no mutable external resources.

Live open PR bodies, recent handoffs and main-tree README searches were
checked for Schur central collisions, ordered-pair classification and the
partitions (3,1)/(2,2). Merged #5287 closes the older characteristic-two
Jordan-law question; that law is expressly credited. Main #5267/#5360 do not
claim this minimal central alias. The overlap helper covered 502 open PRs
and 7,179 Discussion records with complete remote pagination; its sparse
local coverage was only 193 of 10,178 note paths. Separate Git-tree searches
covered relevant merged READMEs. Arbitrary diffs and unpublished work remain
outside that coverage. Source bytes and provenance are pinned in SOURCES.json.

## Open next questions

- Which extra invariant should an actual ordered-state registry retain? Start
  with the full power-rank profile of S+T in this nilpotent family; a specified
  consumer, representation and acquisition cost are still required.
- What is the first central alias outside the sharp nilpotent same-profile
  family? Start with one explicitly named nonsharp or mixed-primary contract.
  The present minima do not cover that domain, and no broader census is held.
