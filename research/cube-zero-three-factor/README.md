# A radical target of exact right-vector cost three

This contribution was produced by Nick Petalas. It answers the first
higher-nilpotency question in
[#4745](https://github.com/CrocSwap/integer-mult-bounds/pull/4745), pinned at
`3edea13af13b755932852e9306a714b317630dda`, with a **scoped proof** and finite
corroboration. A third paid factor enlarges the reachable radical set in the
cube-zero algebra below. No new κ is claimed.

For any field K, let R = K[x,y]/(x,y)³, with radical J = (x,y). Use two
roles, paid factors I + u vᵀ with u ∈ R² and v ∈ K², and arbitrary free
GL₂(K) maps anywhere in a word, as in Wentao Li's #4099 and Nick Petalas's
#4243/#4276. Factors may be singular. Then

```text
M = [[x², xy], [xy, y²]] ∈ M₂(J²) has exact cost 3.
```

Every nonzero base-field row φ and column v satisfy φMv ≠ 0. Thus the
common-zero obstruction from the square-zero ambient-algebra theorem does
not extend to this cube-zero algebra, even for targets in its square-zero
ideal J². The distinction is in the allowed coefficients of the factors:
they can use J, whereas K ⊕ J² has no degree-one coefficients.

## Proof and attaining word

All displayed products use algebraic order; execution on column vectors is
from right to left. The three paid factors are

```text
C₁ = [[x,0],[y,1]] = I + (x−1,y)ᵀ e₁ᵀ,
C₂ = [[1,y],[0,0]] = I + (y,−1)ᵀ e₂ᵀ,
C₃ = [[x,0],[0,1]] = I + (x−1,0)ᵀ e₁ᵀ.

C₁ C₂ C₃ = [[x²,xy],[xy,y²]] = M.
```

There is no scratch or zero-input assumption. This matrix identity acts on
arbitrary elements of R². It supplies the upper bound three.

For the lower bound, use the exact two-factor criterion of Nick Petalas's
[#4276](../right-vector-two-factor-criterion/PROOF.md), Theorem B. It states
that cost(M) ≤ 2 holds exactly when some G,H ∈ GL₂(K) give N = GMH with
N₁₂ ∈ N₁₁R. This theorem already includes arbitrary free maps and words
with fewer paid factors. It is a cited dependency, not a result rechecked
by this contribution.

Every entry of N lies in J², and J²J = 0. Therefore N₁₁R = K N₁₁. If
N₁₂ ∈ N₁₁R, there is a scalar c ∈ K with N₁₂ = cN₁₁. Let φ be the first
row of G and let t,s be the first and second columns of H. Then

```text
0 = N₁₂ − cN₁₁ = φM(s−ct).
```

Both φ and s−ct are nonzero because G,H are invertible. However, for any
nonzero row (a,b) and nonzero column (c,d) over K,

```text
(a,b) M (c,d)ᵀ = (ax+by)(cx+dy) ≠ 0 in R.
```

The two linear polynomials are nonzero. Their product is nonzero in the
polynomial domain K[x,y], has degree two, and hence survives quotienting
by (x,y)³. This contradiction excludes cost at most two and proves exact
cost three over every field, including characteristic two.

The subalgebra S = K ⊕ J² is split square-zero. The same target has no
common zero there, so #4745's theorem makes it unreachable over S. That
last comparison cites #4745; neither its proof nor its binary census is
replayed here. The cost-three theorem above uses only the merged #4276
criterion, and remains independently reviewable without the pending result.

## Evidence and reproduction

Run from the repository root with CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B -W error research/cube-zero-three-factor/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -O -B -W error research/cube-zero-three-factor/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/cube-zero-three-factor
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/cube-zero-three-factor --check-source-history
```

Another CPython 3.12 interpreter may replace the absolute local path. The
verifier writes nothing. It emits a generated SHA-256 receipt binding all
five package files and both declared source inputs, followed by
`PASS_CUBE_ZERO_THREE_FACTOR`. The finite fields are F₂,F₃,F₄,F₅,F₇;
F₄ uses the polynomial t²+t+1. Direct ring multiplication checks the word.
An independent six-dimensional right-ideal rank test rejects every
projective two-factor chart. The checker also evaluates every nonzero
row/column pair, all 12 basis columns of the data action over each field,
and every binary R² input. Positive ideal-membership controls, three
dropped factors, reversed order, an odd-characteristic sign error, illegal
right coefficients, a nonfield parameter and the degree-one quotient are
checked. These checks corroborate the written proof, rather than proving
its all-field quantifier in a proof kernel.

The original card's positive control was run first and reported
`PASS_UNIVERSAL_CONNECTOR_BOUNDARY pairings=945 max_coverage=31 queries=74 leaves=182`.
It is orientation, with no new claim about that connector.

## Limits and implementation decisions

This is one target family in a formal alphabet, not a classification of
all singular targets over R. Native coefficient preparation, conversion,
routing, restoration, precision, stock and the complete supplier bill
are unknown. There is no supplier admission or complete multiplication
theorem. Independent human and formal proof-kernel review are unclaimed.
No Lean, Docker or selected-construction replay was run.

The checker fixes the five field orders, six monomials, two roles, at most
448 charts per field and 4,096 binary inputs. Every loop has a fixed finite
domain, no recursion or subprocess is used, and all functions are under
60 physical lines. Meaningful checks remain active under optimized Python.
Power-of-ten rule 3 has a bounded managed-runtime deviation: tuples,
lists and field integers allocate during this offline calculation. The
largest stored domain has 64 ring elements, each with six coefficients;
the chart and input products are streamed. There is no service steady
state or persistent resource. Source manifests and package files are
small trusted local inputs. Warning-strict ordinary and optimized replay
provide the available diagnostics; no separate static analyzer is part
of the standard-library environment.

## Open next questions

1. Is every reachable radical target over K[x,y]/(x,y)³ attainable with
   three factors? Start with a three-factor normal form. The present
   example gives an exact lower bound, but no classification or global
   upper bound.
2. Which bilinear product maps J/J² × J/J² → J² admit such a cost-three
   target in a general cube-zero local algebra? Start with two independent
   degree-one elements and determine whether every product of their
   nonzero scalar linear combinations survives. Relations may destroy
   the lower-bound witness.

These follow-ups are not investigated here. TASK.json records the questions,
first steps and blockers.

## Credit and source boundary

Produced by Nick Petalas. Nick Petalas's #4745 supplies the explicit
higher-nilpotency question and the square-zero comparison; #4276 supplies
the exact two-factor ideal criterion; #4243 supplies the common free-map
convention. ToikY's #4334 develops the shared-chart algebra interface.
Wentao Li's #4099 supplies the right-vector alphabet, following #2513.
The new contribution is this all-field cost-three radical target and its
degree-two lower bound. SOURCES.json pins the unchanged merged dependencies
at canonical main. Pending #4745 is an exact-head citation, with no runtime
or Git-history dependency. Apache-2.0.
