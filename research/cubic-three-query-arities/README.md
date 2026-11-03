# Three dyadic cube queries at seventeen further cubic-repair arities

**Scoped proof with exact finite certificates; no new κ.** Produced by Nick Petalas.

This answers part of Open next question 1 of CubeJerry's
[PR6250](https://github.com/CrocSwap/integer-mult-bounds/pull/6250): which
remaining arities admit a three-query dyadic repair with a direction pattern
other than `0,d,2d`?

The setting is the fixed cubic reader of PR6200. Retain all `r` children
`y += a^3; a += b`, then restore the arbitrary incoming sources and reproduce
the eager output `y + r*A^3`, where `A,B` are the entry values of `a,b`.
apoursh's [PR6212](https://github.com/CrocSwap/integer-mult-bounds/pull/6212)
proves that every `r > 2` needs at least three dyadic cube queries, even with
nonmonic forms and general dyadic frames. Before this package, three queries
were known for these arities:

| Source | Arities with three queries |
|---|---|
| PR6212 (apoursh) | `r = 2 mod 3`, `r = 3`, `r = 4` |
| PR6215 (apoursh), original-b family | `r mod 9` in `{0,1}` (and `{2,5,8}`) |
| PR6246 (AAAmirinu) | `r = 2^s` |
| PR6250 (CubeJerry) | `r = 2^s + 1` |

**Result.** At each of the 17 arities

```text
6, 7, 12, 13, 21, 25, 42, 51, 52, 76, 85, 93, 97, 114, 156, 157, 160
```

none of which lies in a class above, three integer-direction cube queries with
dyadic weights and integer source shears repair the program exactly. With the
PR6212 lower bound, the exact dyadic minimum at each of these arities is
**three**. Every certificate uses only the PR6212 alphabet: integer shears
`a += k*b` and weighted queries `y += q*a^3` with dyadic `q`.

Example, `r = 6`, starting from the actual deferred source `a = A + 6B`:

```text
a -= 8*b        # A - 2B
y += 1*a^3
a += 4*b        # A + 2B
y += 10*a^3
a += b          # A + 3B
y -= 11*a^3
a -= 3*b        # A, restored
```

Example, `r = 7`: directions `0, 1, 5` with defect weights `-7, 7/2, 7/2`.
All 17 direction triples and weights are in [CERTIFICATES.json](CERTIFICATES.json).

## Proof

Let `S_k = sum_{i<r} i^k`, so `S1 = r(r-1)/2`, `S2 = S1*m` with
`m = (2r-1)/3`, and `S3 = S1^2`. The defect to remove is

```text
D_r(A,B) = sum_{i<r} (A+iB)^3 - r*A^3 = 3*S1*A^2*B + 3*S2*A*B^2 + S3*B^3.
```

**Node lemma.** For distinct rationals `c1,c2,c3`, there are rational `w_j`
with `D_r = sum_j w_j (A + c_j B)^3` if and only if

```text
e2(c) = m*e1(c) - S1.
```

The weights are then unique:
`w_j = S1*(m - c_k - c_l) / ((c_j - c_k)(c_j - c_l))`, where `{j,k,l} = {1,2,3}`.

*Proof.* Comparing the `A^3, A^2B, AB^2` coefficients gives `sum w_j = 0`,
`sum w_j c_j = S1` and `sum w_j c_j^2 = S2`. This Vandermonde system has a
unique solution. Lagrange interpolation gives the stated formula, because
the functional `p -> sum w_j p(c_j)` sends `(x-c_k)(x-c_l)` to
`S2 - (c_k+c_l)S1`. The `B^3` coefficient needs `sum w_j c_j^3 = S3`. Since
`c_j^3 = e1 c_j^2 - e2 c_j + e3` at each node, the left side is
`e1*S2 - e2*S1 + e3*0`. So the condition is `S1^2 = S1(m e1 - e2)`, and
`S1 > 0` for `r >= 2`. ∎

**Schedule.** Given an integer node triple with dyadic weights, start from
`a = A + rB` after the last retained child. For each `j`, shear `a` to
`A + c_j B` with `a += (c_j - previous)*b`, then apply `y += (-w_j)*a^3`. A
final shear `a -= c_3*b` restores `a = A`. `b` is never written. The appended
repair has exactly three queries and at most four shears. The final output is
`y + sum_i (A+iB)^3 - D_r = y + r*A^3`, for arbitrary dirty `y,A,B`.

For each listed arity, the node condition and dyadic weights are finite exact
facts that the verifier checks. The lower bound of three is PR6212's
theorem, cited and not re-proved here.

## Evidence and reproduction

From the repository root, with CPython 3.12 and only the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/cubic-three-query-arities
python3.12 -I -W error -B research/cubic-three-query-arities/verify.py
python3.12 -I -W error -B research/cubic-three-query-arities/search.py --check research/cubic-three-query-arities/CERTIFICATES.json
```

- `verify.py` does not use the closed weight formula to accept certificates.
  It solves the first three coefficient equations by exact Gaussian
  elimination and requires the `B^3` residual to vanish. It also checks that
  every weight is nonzero and dyadic, and that each recorded weight matches.
  It runs each literal program (all `r` children, then the repair) on 12
  dirty integer and rational inputs.
- It corroborates the node lemma's residual identity
  `S1*(m e1 - e2 - S1)` and the closed weights on random rational triples.
- It recomputes the uncovered-arity list independently and anchors the
  predecessors. It reproduces PR6250's r=33 weights, and it finds PR6215's
  residue table and PR6212's two-query statement in the pinned README bytes.
- Six rejection controls must fail: a perturbed weight, an omitted restoring
  shear, a query moved before its shear, a wrong arity, an omitted query, and
  the non-node triple `0,1,5` at `r = 10`.
- `search.py` regenerates `CERTIFICATES.json` byte for byte. It takes the
  lexicographically first integer triple with `c1 < c2 < c3` and
  `c1,c2` in `[-160, r+160)`, for every uncovered `r <= 160`.

## Limitations

- **Search failure, not obstruction:** 50 of the 67 uncovered arities
  `r <= 160` have no integer-direction certificate in the box. They are listed
  in `no_certificate_in_box`. Nothing here proves that four queries are needed
  at any of them. Dyadic non-integer directions and general dyadic frames
  (as in PR6215) were not searched.
- This is a local coefficient and restoration result. No query, shear,
  preparation, routing, precision or storage price is paid. No physical
  backend, complete invoice or supplier admission is claimed. The selected
  result and its five framework assumptions are unchanged.
- No independent human or formal proof-kernel review is claimed.

## Open next questions

1. **Finish the classification.** Do `r = 15, 22, 24, 30, 31, ...` admit
   three queries with dyadic non-integer directions or general frames, or is
   there a four-query obstruction? A first step is to write
   `v_j = 6c_j - (2r-1)`. The node condition becomes
   `e2(v) = (9 - 3(2r-1)^2)/2`. Then test odd-prime valuations of the weight
   numerators and denominators at `r = 15`.
2. **Infinite family.** The certificates at `r = 7` and `r = 97` share the
   weight shape `(-r, r/2, r/2)` on directions `(0,d,e)`. Imposing
   `w_2 = w_3` in the closed formula gives a binary quadratic. Does it have a
   Pell-type recurrence that yields infinitely many new arities?
3. **Price.** Does the `r = 6` or `r = 7` repair beat `r` eager inverse shears
   under one pinned backend? Use the complete inequality in PR6250's PROOF.md.

## Sources and credit

Produced by Nick Petalas. New work is Apache-2.0.

- The question is CubeJerry's PR6250 (`research/cubic-equal-step-classification`).
- The interface, dyadic lower bound of three and the `r = 2 mod 3`, `3`, `4`
  constructions are apoursh's PR6212 (`research/dyadic-cubic-repair`).
- The original-b classification is apoursh's PR6215
  (`research/cubic-pure-b-boundary`).
- The power-of-two branch is AAAmirinu's PR6246.
- The fixed cubic reader and its restoration interface are from PR6200.

The three predecessor READMEs are pinned live inputs in [SOURCES.json](SOURCES.json).
No predecessor code is imported or modified. Three-node quadrature and
Lagrange interpolation are classical; no literature priority is claimed.
