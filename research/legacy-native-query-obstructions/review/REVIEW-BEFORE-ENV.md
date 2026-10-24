# Independent agent review: native query obstructions

Status: **PASS for the stated formal-model claims**, after the source and
attribution corrections listed below. Review date: 2026-10-22 local time.
This is an independent OpenAI Codex agent review. It is not human review or
a proof-assistant result. The reviewer did not write the historical proofs.

The checked package is `legacy-native-query-obstructions`. The exact 65
file hashes are in `CHECKED-FILES.json`. Its SHA-256 is
`f91f88f3cb5c81b360ab1b693cfceeaff0fc2ab23289b2ced8a7c75362b70e90`.
The source manifest contains 50 frozen input files. The review uses upstream
commit `cef4b52f2a59009865bf8eabde1be3f159063703` for comparison.

## Conclusions

The package supplies useful scoped lower bounds for exact words of native
queries. It does not supply a new supplier, a physical implementation, or
an improved complete kappa. The following conclusions are supported.

1. For rational monomial ADDRESS maps with rank-one difference from identity,
   an exact endpoint that applies `-I_m` to `p` productive roles needs at
   least `p*m` negative-determinant queries. Coordinate reflections attain
   this count. Additional dirty roles can be restored without weakening the
   bound. The separate independent proof also establishes its stated wider
   scalar-only free-event extension; the README keeps the narrower helper
   claim.
2. If rank-one rational ADDRESS maps generate a finite group in three
   coordinates, the same endpoint needs at least `3*p` queries. This result
   uses the classical finite-reflection chamber theorem. It does not infer
   the classification from the finite checker.
3. On three productive roles, the rational plane endpoint `-I_2` needs at
   least six rank-one queries, with any determinant signs. Six coordinate
   reflections attain the count. The helper audit correctly extends this
   claim to the full endpoint `I+(z-1)D`, where `D` is a binary rank-three
   idempotent, including every initially dirty helper input.
4. If exactly two query labels lie outside a subgroup `H` with a `C2`
   character that detects the endpoint, then `p <= k+1`, where `k` counts
   the character-active inside labels. The proof permits nonnormal `H` and
   distinct outside labels. The zero- and one-outside cases and the stated
   restricted shear consequences also follow.
5. If all ADDRESS maps lie in one common identity-modulo-two subgroup over
   rationals with odd denominators, reduction modulo four gives `q >= p*m`.
   A separate basis choice for each map does not meet this hypothesis.

All five claims require the declared exact formal group-algebra endpoint.
They do not reject all dense eight-query rational three-coordinate words.
Clean-zero, discarded, or partial helper endpoints must not be added to the
plane, subgroup, or congruence claims without a separate proof.

## Proof checks

For the monomial result, the sign substitution is a group homomorphism only
on monomial matrices. The cycle classification covers arbitrary nonzero
rational weights. Each represented query difference has one outer factor
over `F2[e]/(e^2)`. Telescoping therefore gives `e I_d = BC`. Comparison of
the two binary coefficients gives `B0 C0=0` and
`B0 C1+B1 C0=I_d`, so `d <= rank(B0)+rank(C0) <= k`. This uses field rank
only after coefficient extraction. It does not treat the dual numbers as a
field. Productive row and column selection handles the restored helpers.
The independent proof also checks the scalar replay for noninvertible free
events. The entrywise sign map fails on a genuine shear, as its control shows.

For finite rational groups, the averaged positive Gram matrix makes each
rank-one finite-order element a reflection. Essentiality follows from the
endpoint `-I_3`. The rational trace restricts wall orders to `2,3,4,6`.
The positive Gram matrix then gives the stated rank-three type list. `A3`
cannot contain the nonidentity central endpoint. The `G2 x A1`
representation obeys the dihedral relations, maps `-I_3` to `(1+e)I_3`,
and gives an outer factor for every reflection. The realization isomorphism
preserves the reflections and the central minus-identity endpoint.

For plane words, the image and covector coloop arguments are valid over the
noncommutative group algebra. The coset argument uses the correct left or
right multiplication orbits. Rank-one rational maps have a fixed line, so
their cyclic subgroups cannot contain `-I_2`. The determinant quotient is
used only in a commutative group algebra. The two positive normal forms are
complete under the target-subset extrema conditions. Their coefficient
rank contradictions are valid. In the two-negative case, the opposite
reflections have equal controls; the determinant-magnitude lemma forces
the other maps to be unipotent. The unique possible additional four-subset
cannot have both required distinct minima and maxima. This is a direct
proof. The finite DATA replay is a separate check, not its coverage argument.
The fewer-than-five cases and the full dirty-helper reduction are also valid.

For the two-outside result, projection onto the `H`-supported coefficients
gives `(I-N)X=K(I-M)`. This is a linear support projection, not an assumed
algebra homomorphism. Augmentation gives `N=M` without a normality premise.
Applying the character only to this equality over `F2[H]` gives
`D=DN+(I-N)A+B(I-N)`. Rank subadditivity gives the claimed bound without
commuting `D` and `N`. The attaining `p=1,k=0` control prevents an overclaim
that every pair of outsiders is impossible.

For the congruence result, division of `g-I` by two stays in the odd-
denominator ring. Reduction preserves vanishing two-by-two minors. The
map `g -> I+e((g-I)/2 mod 2)` is multiplicative, and the first-order
coefficient has binary rank at most one per query. The endpoint coefficient
has rank `p*m`. The common-basis and full helper endpoint restrictions are
necessary and are stated.

The all-size separation argument is valid for a fixed finite word: finitely
many distinct rational ADDRESS maps can be separated by one integer vector
and a sufficiently large permitted residue precision. This does not follow
from equality on only one tested ADDRESS grid. The pinned native lift is
injective and preserves composition. No full compiler replay was performed.

## Source and citation corrections

The initial package omitted `native-research/PROOF.md`, which supplies the
two- and three-determinant-magnitude lemma used by the plane proof. The
packager added the byte-exact file. Its relevant coefficient comparison was
checked. This is a written dependency; its historical search is not run by
the package driver and is not needed by the admitted plane theorem.

The pinned PR #521 proof and source pins supply the native model and its
ordered-stream and recursive-interchange premises. The vendored proof
matches the Git object at `a190fdb39f31647fc6f651625353710624627348` exactly:
SHA-256 `320ce5529c1543f9e6fceb9e7f8b563ed332f13923229e38d4e7edac98f30283`.
Those files do not name an individual primitive author. The publication
must not infer an author from the submitter account. The proof's exact
source references and the Apache-2.0 license remain present.

The README now credits Swapnil Jain's prior determinant-sign dual-number
and rank-one relation methods. I read the cited local algebraic section,
including its conditional finite-field rank-one relation setting. It does
not itself establish the matrix-valued rational monomial argument checked
here. No literature-priority claim follows from this targeted comparison.

The pinned PR #521 proof already mentions an older `rho4` construction.
`ATTRIBUTION-QUALIFICATION.md` now explicitly overrides the historical
congruence proof's originality sentence. It states the common-basis and
restored-helper result without an unsupported priority claim. The exact
older `rho4` note was not identified in this audit.

The cited [Casselman notes](https://personal.math.ubc.ca/~cass/coxeter/R.html)
support the Cartan, rank-three, roots, and classification deductions.
Their Cartan section starts with simplicial realizations, so this citation
alone is not a precise proof source for the converse chamber step. The new
qualification cites [Nathan Reading's text](https://nreadin.math.ncsu.edu/papers/regions.pdf),
Theorem 10-2.1, Proposition 10-2.2, and Theorem 10-2.5, on printed pages
493–495. These state simpliciality and chamber transitivity for essential
finite reflection arrangements. The primary search-indexed statements and
the displayed proof passages were checked. Direct PDF retrieval timed out.
This is a classical inherited theorem, not a theorem verified by the
24-element representation certificate or by a proof kernel here.

The package now has the required Open next questions section. The question
is an explicit remaining scope boundary, not a claim of a new construction.

## Fresh exact replay

I ran the final driver with Python 3 and no third-party package:

```sh
python3 -B work/project-final-cleanup-20261022/legacy-audit/packages/legacy-native-query-obstructions/verify.py --work /Users/aliromman/Projects/IntegerMultiplicationBounds/work/project-final-cleanup-20261022/reviews/native-obstructions/final-replay
```

It exited zero and printed:

```text
PASS_LEGACY_NATIVE_QUERY_OBSTRUCTIONS checks=5
```

All five child checks exited zero. The exact command, Python version,
per-check outcomes, and control results are in `REVIEW-RESULT.json`.
The fresh logs and regenerated receipts are under `final-replay/`.

- The monomial engines check the representation laws, arbitrary-weight
  finite controls, outer factors, inner-factor obstructions, and the sharp
  twelve-call endpoint. The second engine uses a different matrix layout.
- The finite-group checker checks all 576 products of its 24-element
  `G2 x A1` realization, seven rational rank-one reflections, and 840 native
  outer factorizations.
- The independent two-negative plane checker reproduces 492 permitted
  projector triples and all 120 ADDRESS orders. It checks 9,840 words,
  finds no endpoint, and matches terminal coefficient SHA-256
  `ca085c7a99ebf32aeaea402edb3e96431e817eea57e15cf6b638d8b6dc41ee0f`.
  Its six-call endpoint, every single-call omission, and noncommuting
  order controls pass.
- The independent positive-plane checker confirms every canonical subset,
  the noncommutative coefficient identities, rank-one couplings, the
  determinant identity, and the rational shear normalization.

The original positive-five backup search over 82,320 normalized choices per
form was not rerun. The direct proof and its independent algebraic checker
are the decisive evidence. The two-outsider and congruence claims were
checked as written proofs, not certified for all sizes by a finite test.

Three package controls also pass: optimized Python is rejected because
assertions are required; an existing output directory is rejected; and a
source-byte change in a separate copied package is rejected before any
output directory is created. The checked original package did not change.
No selected supplier cold replay, full kappa calculation, Lean check,
hosted CI, or physical tape execution was run by this reviewer.

## Current-source overlap boundary

I searched the current main Markdown sources for the theorem terms and
read the nearest packages on generated-lattice parity cuts, local
right-vector cost, orbit-closed caller bounds, the SL2Z commutative caller,
the fifth-frame determinant obstruction, native query boundaries, and
native controller congruence. They share rank or character methods but use
different carriers, paid alphabets, or endpoints. They do not give the
specific rational multiplicative ADDRESS results in this package.

I also read live [PR #4939](https://github.com/CrocSwap/integer-mult-bounds/pull/4939)
at `743ddd6275cfd560d9c3e7825c42545152d14e4c` and
[PR #4950](https://github.com/CrocSwap/integer-mult-bounds/pull/4950)
at `78dc9c12f46967df0d85594875a32a62b5639670`.
Their coordinate-CNOT alphabet and coordinate-SWAP endpoints lie in
`F2[GL_n(F2)]`. They do not subsume the rational central `-I_m` endpoint
here; reduction to characteristic two loses that endpoint distinction.
Their readbacks are saved with this review. This is a targeted semantic
comparison, not an exhaustive review of all historical PRs or the literature.

No material proof error remains in the admitted scope. Publication is
appropriate as a group of scoped obstructions with exact checks. The final
PR description, GitHub links and rendering still require the coordinator's
publication check.
