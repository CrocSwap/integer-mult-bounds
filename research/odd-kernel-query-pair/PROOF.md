# Excluded-prime pattern for general odd-kernel native DATA shears

This is a local recursive-interface construction and a scoped admission lemma.
Ordinary ADDRESS interchange and ordered affine tape streams remain premises.
There is no new supplier, kappa, or formal multiplication proof.

It answers open question 2 of the pending
`research/triadic-query-pair/` package (fork tip `77041f2d`), which completes
PR840's non-dyadic note for kernel **3** and asks for the excluded-prime pattern
of a general odd kernel `q`.

## Object

Use the same six ADDRESS fields and unipotent push `h` as PR521/PR840:

```text
s=(1,0,1,-1,0,-1)^T, r=(1,0,-1,-1,0,1)^T,
M(k)=I6+(k/4)s r^T,   h = array permutation of M(1).
```

For each positive odd integer `q` and each `j ≥ 0`, `σ ∈ {±1}`, set
`a = σ·q·2^j`. The completed DATA endpoint is

```text
F_a(x,y,z)=(x+(h^a+h^-a)y, y, z).
```

## Lowering and exclusion pattern

The seven-event word of PR840/triadic applies verbatim for any nonzero integer
`k`, with diagonal units `1`, `c=k/4`, and `-1/c`. For `k = ±q·2^j`, the
odd parts of these diagonal units' numerators and denominators divide `q`.
The control-coefficient denominators have no other odd prime factors; their
numerators need not be invertible. Therefore the lowering
specializes to **every odd modulus coprime to `q`**. Equivalently: an odd
modulus is admitted iff it shares no odd prime factor with `q`; every even
modulus is excluded. When `q=1` this recovers PR840's all-odd-radix claim.
When `q=3` this recovers the pending triadic exclusions.

## Completed pair fusion and typed costs

The fused program is identical in form to PR840:

```text
x <- h^-a x
x ^= y
x <- h^(2a) x
x ^= y
x <- h^-a x.
```

Relative to two separate completed shears, the fused word uses **three ordinary
children, eighteen affine events and two XOR scans**. These counts are
independent of `q`. No odd kernel improves the typed interface invoice over the
dyadic case; larger radical(`q`) only shrinks the admitted modulus set.

## Three-query necessity

The PR840 determinant argument applies for any nonzero integer unit power `a`
on an odd full-order orbit admitted by the lowering. This package treats that
written argument as inherited; finite Laurent/two-query corroboration for
kernel 3 remains in the triadic predecessor.

## Evidence boundary

The checker verifies, for kernels `{1,3,5,7,9,15}`, that the closed-form
admission predicate matches denominator invertibility on a fixed probe modulus
set, that rational and modular columns match `M(k)`, that
`M(-a)M(2a)M(-a)=I`, and that fused/baseline invoices are `3/18/2` versus
`4/24/4`. An independent module rebuilds the matrix identity without importing
`verify.py`.
