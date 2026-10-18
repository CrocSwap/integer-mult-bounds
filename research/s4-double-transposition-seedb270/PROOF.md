# Exact cost of a pair of S4 double transpositions

## Theorem

Let `R = F2[S4]`, let the number of scalar roles be `W=3`, and define a paid
call for `s in {(12),(23),(34)}` and a rank-one idempotent `N in M3(F2)` by

```text
D(s,N) = I + ([s]+[e])N.
```

Allow arbitrary free interleaved scalar `GL3(F2)` changes of basis. For
arbitrary dirty inputs, the complete endpoint

```text
diag([(13)(24)], [(13)(24)], [e])
```

has exact paid-call minimum eight.

## Upper bound

With right multiplication as the word convention, put
`s1=(12)`, `s2=(23)`, `s3=(34)`. Direct composition gives
`q=s2*s1*s3*s2=(13)(24)`. Four calls with `N=E11` place `[q]` in the first
diagonal role; four with `N=E22` place `[q]` in the second. Every other entry
is the identity, so this is a formal `R`-matrix identity on arbitrary input,
including the restored third dirty role. Thus the minimum is at most eight.

## Normalize free scalar maps

Write a free scalar map as `A tensor [e]`. Moving it to the right across a
paid factor uses

```text
(A tensor 1) D(s,N) = D(s, A N A^-1) (A tensor 1).
```

Conjugation preserves rank one and idempotence, so the 84 factors already
include every normalized choice. The augmentation homomorphism
`epsilon:R->F2`, `epsilon([g])=1`, sends every paid factor to `I`. The target
also augments to `I3`. Therefore the product of the moved free scalar maps
must be `I3`. No extra words are introduced by free mixing.

## Even-length obstruction

The sign character gives a ring homomorphism
`F2[S4] -> F2[C2]`; denote the nonidentity basis element of `C2` by `x`, so
`x^2=1`. Every adjacent transposition maps to `x`, whereas
`q=(13)(24)` maps to `1`. The target therefore maps to the identity matrix.

For any rank-one idempotent `N=u v^T`, `v^T u=1`, and the paid factor maps to
`I+(x+1)u v^T`. The coefficient ring is commutative, so the determinant
lemma yields

```text
det(I+(x+1)u v^T) = 1 + (x+1)v^T u = x.
```

Each free `GL3(F2)` map has determinant one, since the only nonzero element of
`F2` is one. Determinants multiply, so an endpoint word with `k` paid calls
has determinant `x^k`; the target determinant is one. Since `x` has order
two, `k` is even. Any strict improvement over the eight-call direct word
would therefore have length at most six.

## Complete six-call exclusion

Each `D(s,N)` is an involution. In `R`, `a=[s]+[e]` satisfies `a^2=0` in
characteristic two; using `N^2=N`,

```text
D(s,N)^2 = I + 2aN + a^2 N = I.
```

Consider the right-multiplication Cayley graph on all `3x3` matrices over
`R`, starting either at identity `I3` or at target `T`. The verifier
enumerates the full radius-three balls using all three labels and all 28
rank-one idempotents. A word of length at most six splits as `AB` with
`|A|,|B|<=3`. If `AB=T`, involutivity gives `A=T B^-1`, so the intermediate
state belongs to both balls. The independently enumerated exact balls have
layers `[1,84,4697,232692]` and empty intersection. Hence no word of length
at most six reaches the target.

The state stores every coefficient of every matrix entry in `F2[S4]` as a
24-bit mask; the implementation packs the nine masks into 27 bytes for the
visited-state keys. It performs no address specialization, probability
sampling, rank pruning or assumed group-ring faithfulness. Sorted state hashes
and counts are in `CERTIFICATE.json`; replay recomputes all states and hashes.

Together with the direct word and even-length obstruction, the exact minimum
is eight.

## Exactness boundary

The theorem is for this fixed finite group, paid-letter set, role count and
endpoint. The natural permutation representation only gives the four-call
rank floor and is not used to prove the stronger exclusion. This does not
establish that any supplier can provide these operations, that the model
occurs in a selected circuit, or that any recursive moment or conditional
multiplication bound changes.
