# Proof: shared length two cannot write the transposition

## Model

Let `G = S3` act on the labels `{0,1,2}`, and write

```text
s = (1 2) = (1,0,2),   t = (2 3) = (0,2,1).
```

Let `ell(g)` be the reduced word length of `g` with respect to the generating
set `{s,t}`.  The six values are

```text
ell(identity)=0, ell(s)=ell(t)=1, ell(st)=ell(ts)=2, ell((1 3))=3.
```

A **paid shared call** is a pair `(g, M)`, where `g` is an element of `G` and
`M` is a nonempty set of registers; the call writes `g` to every register in
`M`.  Its cost is `ell(g)`.  A **shared word** is a finite sequence of paid
shared calls, and its total cost is the sum of the call costs.  If register
`r` belongs to the masks of calls `i1 < i2 < ... < ik`, its induced element is
the ordered product `g_i1 g_i2 ... g_ik`.  Registers not written by any call
are left at the identity.

This is the natural shared-letter cost of the paid alphabet in #4351: one
letter of the alphabet is dispatched to a chosen set of registers, and the
letter is charged its reduced generator length.

## Proposition

For every shared word `W` of total cost `L`, every register `r` satisfies
`ell(W_r) <= L`.

**Proof.**  `W_r` is a product of a subsequence of the letters of `W`.  The
reduced word length is subadditive: `ell(ab) <= ell(a) + ell(b)` for all
`a,b` in `G`, because concatenating reduced words for `a` and `b` is a word
for `ab`.  By induction over the subsequence,

```text
ell(W_r) <= sum over the calls that write r of ell(g_i)
          <= sum over all calls of ell(g_i) = L.
```

The second inequality holds because every term is nonnegative.  Scratch
registers are ordinary registers in this argument; their number does not
enter.

## Corollary

No shared word of total cost at most two writes the transposition `(1 3)` on
any register, with any number of scratch registers.

**Proof.**  If `W_r = (1 3)`, the proposition gives
`3 = ell((1 3)) <= L`, so `L >= 3`.

The bound is sharp in the stated cost model: the coordinate word
`s, t, s` has cost `3` and writes `(1 3)`.  Sharing does not lower that cost,
but it does let one scratch register be restored for one extra call.  The
four-call word

```text
(s, {0,1}), (t, {0}), (s, {0}), (s, {1})
```

writes `s t s = (1 3)` on register `0` and `s s = identity` on register `1`,
at total cost `4`.  So a restored scratch costs at least one call beyond the
three-call target word, and no cost-two word can replace it.

## Finite corroboration

`verify.py` rebuilds the multiplication table, inverses and the reduced length
table, checks subadditivity on all `36` ordered pairs, and enumerates every
shared word of total cost at most two on two and on three registers.  The
enumeration covers every nonempty mask, every cost-one letter, every cost-two
letter, and both positions of a two-call word: `272` words and `768`
register evaluations in total.  Every evaluation is distinct in the count and
none equals `(1 3)`.  The cost-three, shared cost-four and mutation controls
are asserted separately.

The finite enumeration is corroboration, not the proof.  The all-size
statement is the subadditivity proposition above.
