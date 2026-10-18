# A clean scratch cache cannot improve a two-output source channel

Let `F`, `H`, `G1`, and `G2` be subspaces of a finite-dimensional vector
space over any field. For `j in {1,2}`, write

```text
a  = dim(F + H)
bj = dim(H + Gj)
dj = dim(F + Gj).
```

For each `j`, set `A=F+H` and `B=H+Gj`. Since `A intersect B` contains `H`
and `A+B=F+H+Gj`, the dimension identity gives

```text
a + bj = dim(A+B) + dim(A intersect B)
        >= dim(F+H+Gj) + dim(H)
        >= dim(F+Gj) = dj.
```

For `0<s<1`, `t -> t^s` is increasing and subadditive on nonnegative reals.
Therefore

```text
dj^s <= (a+bj)^s <= a^s + bj^s.
```

Summing over two output ports proves

```text
direct = d1^s + d2^s <= 2*a^s + b1^s + b2^s = cache.
```

The right-hand side charges one source-to-scratch load and one exact scratch
restore at `a^s` each, plus the two scratch-to-output transfers. Thus this
clean-cache channel cannot reduce the paid transport bill for exactly two
outputs. Any source/helper supply, hosting, precision, or interface charges
would add to the cache route and cannot reverse the inequality.

## Relation to the selected block interface

At the pinned base, `research/complex-block-rank-optimum/PROOF.md` states that
each input column affects exactly two distinct output ports. The theorem
screens the corresponding channel route for one read-only source contribution
that is cached in a newly added clean scratch array. It does **not** establish
that the direct channel bill is itself a legal full-supplier program; direct is
an optimistic local comparator. It does not rule out multi-source coding,
combined caches, changed output support, changed frames, more than two outputs,
or a different nine-array program.

## Three-output control

The two-port restriction is real. In `Q^15`, take coordinate subspaces

```text
F  = span(e1,e2,e3,e4,e5,e6)
H  = span(e1)
G1 = span(e1,e7,e8,e9,e10,e11,e12,e13)
G2 = span(e1,e7,e8,e9,e10,e11,e12,e14)
G3 = span(e1,e7,e8,e9,e10,e11,e12,e15).
```

Then `a=6`, every `bj=8`, and every `dj=13`. At `s=9983/10000`, the exact
outward-interval verifier certifies

```text
three-port direct = 3*13^s       = 38.830314 (rounded to 6 decimals)
three-port cache  = 2*6^s+3*8^s = 35.878812 (rounded to 6 decimals).
```

Thus a shared cache can lower this channel bill for three ports. This is only a
dimensional control, not a construction admitted to the selected supplier.

## Exact finite checks

`verify.py` imports the base-pinned interval routines from
`research/complex-local-word-ceiling/ceiling.py`. It checks all 220,480 positive
integer triples `a,b,d <= 64` satisfying `d <= a+b` at `s=9983/10000` and
`s=999/1000`. It also checks the two-output example (`a=6`, `b1=b2=8`,
`d1=d2=13`) and verifies that omitting the restore would falsely make the
two-port cache look cheaper. These finite checks support arithmetic and model
controls; the all-dimension, all-exponent conclusion is the subspace proof
above.
