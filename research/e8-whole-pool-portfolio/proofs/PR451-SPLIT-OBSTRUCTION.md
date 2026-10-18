# A trace obstruction to splitting one residual across two families

PR448 at [`9b966d8`](https://github.com/CrocSwap/integer-mult-bounds/blob/9b966d8188e1cadd00aa834078ee6a8742a9d9b4/research/cross-copy-hosting/PROOF.md)
proposes routing one residual onto pending coordinate sets in two different
families by an elementary coordinate permutation. Its proof uses the valid
same-family factorization `D_(P1+P2) = D_P1 D_P2`, then assigns the two factors
to different families. That assignment needs a new operator theorem: it is
not a consequence of the factorization or a coordinate conjugation.

The obstruction is invariant under **every invertible linear change of
storage**, not only coordinate permutations. Consider one residual on family
A and identity on an otherwise unused family B. Replacing it with one factor
on A and the other on B gives different traces.

## Bit permutation

Let each family have addresses `(x,y)` in `F_q^m × F_q^m`. A rank-r coordinate
operator `D_r` exchanges r selected coordinates between x and y. It fixes
`q^(2m-r)` addresses, so this is the trace of its permutation matrix. If the
residual has positive ranks a and b, with a+b≤m, then

```
trace(D_(a+b) ⊕ I) = q^(2m-a-b) + q^(2m)
trace(D_a ⊕ D_b)   = q^(2m-a) + q^(2m-b)
```

Their difference is

```
q^(2m-a-b) (q^a−1) (q^b−1) > 0.
```

Thus the two operators are not similar. Disjoint coordinate factors on the
**same** family do multiply correctly; putting them on separate families
changes the operator. Independent routing conjugations inside each family
do not change this trace conclusion.

The smallest enumerated odd-field control uses q=3, m=2 and a=b=1. On the
162 physical scalar coordinates of two families, the whole residual plus
identity has trace90; the split action has trace54. The script explicitly
constructs both permutations, checks bijectivity and involutivity, verifies
the valid same-family product, and emits a differing input column. Additional
controls cover m=3 and the exact rank-eight formulas at the proposed m=64.

## Complex factor

For the inherited complex factor, the exact Fourier multiplier on r selected
binary coordinates is `i^(sum y_j)`. Therefore

```
trace(C_r) = 2^(m-r) (1+i)^r.
```

The difference between `trace(C_(a+b) ⊕ I)` and `trace(C_a ⊕ C_b)` is

```
2^(m-a-b) [2^a−(1+i)^a] [2^b−(1+i)^b],
```

which is nonzero for positive a,b because each bracket is nonzero.
For m=2, a=b=1 the traces are exactly `4+2i` and `4+4i`. The script enumerates
the exact Fourier exponents and sums them as Gaussian integers, with no
floating-point arithmetic. It also verifies the same-family factorization
and the exact rank-nine formulas at the proposed m=73.

## Scope and reproduction

```sh
python -B research/cross-family-residual-obstruction/verify.py
```

This refutes the stated coordinate-permutation derivation for a **single
residual split between two families**. It does not rule out a different
compiler that changes the local program, introduces and charges additional
operations or storage, or proves a global regrouping theorem. Those changes
are not supplied by the two inherited hosting facts alone. A scalar count or
slot-packing audit cannot establish the missing operator identity.

The adjacent `r740-hosted-rank149` certificate retains whole-residual hosting
and does not use the cross-family extension.

Prepared by chafreaky with OpenAI Codex assistance, Apache-2.0. The reviewed
proposal is by Sreekanth Nair / higherbeing with substantial Anthropic Claude
assistance; its exact commit and proof are linked above. This review does not
claim their endorsement.
