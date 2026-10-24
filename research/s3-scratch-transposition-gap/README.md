# Length 2 cannot write the S3 transposition, with scratch

**Scoped obstruction. No new κ.** The selected conditional result stays
κ = 60403/20000000 = 0.00302015 (#4470). This package does not change a
supplier, a paid profile, or the three-register rational-frame theorem.

## Result

No length-2 word in the paid alphabet writes the transposition (0 2) on one register, with or without scratch.

The alphabet is the one in
[research/s3-diagonal-rank-screen](../s3-diagonal-rank-screen/README.md):
labels `s = (0 1)` and `t = (1 2)`, acting by right multiplication on
3×3 matrices over `F2[S3]`. A paid move is `I + (h + e) P`, where `h` is
`s` or `t` and `P` is one of the 28 rank-1 idempotents over `F2`. The
missing transposition is `g = (0 2)`. Its generator length on one register
is 3, by the word `s t s`.

The scratch model is any number of extra registers, not only the two
companion coordinates of this 3×3 screen. Coupling entries of `P` are
allowed. They do not help at length 2.

## Proof

Write the product of two moves, starting from `I`, as

```text
(I + (a + e) P) (I + (b + e) Q)
  = I + (a + e) P + (b + e) Q + (a + e)(b + e) P Q.
```

Here `a, b ∈ {s, t}` and `P, Q` have entries in `F2`. In characteristic 2,
`(a + e)(b + e) = ab + a + b + e`. Scalar entries do not introduce new group
basis vectors, so every matrix entry lies in the `F2`-span of

```text
{e, s, t, s t, t s}.
```

Those five permutations are the Cayley ball of radius 2. With the product
that applies the right factor first, `s s = t t = e`, `s t = (1, 2, 0)`,
and `t s = (2, 0, 1)`. The transposition `g = (2, 1, 0)` is the sixth basis
vector, so it is outside the span. No entry of a length-1 or length-2 word
can equal `g`, and none can carry `g` as a summand.

The rank-1 and idempotent restrictions are not used. The same span contains
every length-2 product `I + (h + e) M` for an `F2`-matrix `M` of any size.
Adding scratch registers therefore does not create a shorter word for `g`.

The bound is sharp at length 3: right-multiplying register 0 by `s`, then
`t`, then `s` yields `diag(g, e, e)`.

## Enumeration

The stated 3×3 alphabet has 2 × 28 = 56 moves. All 56 length-1 states and
all 3,136 length-2 products were multiplied in `F2[S3]`. The coefficient of
`g` is zero in every one of the nine entries. The length-3 coordinate
control above matches `diag(g, e, e)`.

## Scope

Task card `bit-new-register-model`, priority revision 7, base
`fbc9ea0249746acca4f504d4fda2b84e0e36cf0d`. Scope status is **refined**.

This is item 6 of the eligible list below. It is the open question of the
merged diagonal screen, not a new nonabelian supplier and not an escape from
the rational-frame three-register bound. The bit side of #4470 is not the
binding constraint on the selected κ, so this obstruction does not move κ.

Ordered eligible list for session r18, after dropping work already delivered
by this account, covered by an open PR, or closed on current main. Open
handoffs in the 19 October index come first. Priority-table rows whose
stated next decision is still open come next. Catalogue cards not in that
table follow, skipping cards this account already answered.

1. P104 consumer of `(w, q, v_N)` (discussion comment 19030045). Distinct
   from the encoded-exit and `(N-P)⊗M` consumers.
2. R437 fresh T385 wrapper replay (comment 19030047). Distinct from the
   merged compiler integration #4176 and from the reverse coefficient #4147.
3. QQ16 six-tape binding of one F0/B1 event (comment 19030049). Distinct
   from the F0 magnitude ledger and the adjacent-ADD price.
4. Four-provider ordinary/outer rebind of #4088. The idle-cost block is
   recorded; the four-id rebind is not.
5. Matched park/restore bill for the #4166 QQ16 caller. #4172 leaves that
   comparison unpriced.
6. This package.

Excluded before this cut, with the reason: the coordinated-retiming handoff
(comment 19030053) by #4122, #4128, #4116 and open #4567; `uniform-transfer-audit`
by the #4100 audits including #4371, #4373, #4376 and #4377; the R437 card's
"close one obligation" by merged #4176; `p104-side-correction` by the slot,
chart, encoding, fiber and consumer packages; `independent-moment`'s named
#4088/#4091/#4067 checks; `formal-interface-lemma`'s compact-switch audit
#4321; `bit-helper-contract` by the R439 K tally and compensated-shear
certificate; `complex-rank-shape-decoder` by open #4596, #4627, #4629 and
#4633; centre-path, coverage, connector, selected-stock, census, replay,
portable replay, scope navigation, packing and scalar-itinerary cards by the
packages and open PRs named in the session notes. The retiming handoff is
the index item that was dropped, so it is not item 4.

## Reproduce

From the repository root, Python 3.12, standard library only:

```sh
python3 scripts/research_package.py --package research/s3-scratch-transposition-gap --check-only
python3 -B research/s3-scratch-transposition-gap/verify.py
python3 -B research/s3-scratch-transposition-gap/independent.py
python3 -B research/s3-scratch-transposition-gap/test_verify.py
```

`verify.py` prints `PASS_S3_SCRATCH_TRANSPOSITION_GAP ball=5 length2_gap_bits=0 moves=56 length3_control=1`.

`independent.py` rebuilds the length-2 support with sets of permutations and
does not import `verify.py`. `test_verify.py` checks that paying the gap
label itself would light the same bit, so the zero count depends on the
generator restriction.

Not run: Lean, Docker, the selected cold replay, and any length-3 scratch
search.

## Open next questions

1. Can a length-3 coupling word write `g` and restore every scratch register
   at a cost below one coordinate word of length 3? The length-2 support
   bound does not speak to length 3. First multiply the 56³ words and count
   restored hits. A hit still needs a native bill before it can change a
   supplier. Nothing in the present certificate prices that bill.
2. Does some other paid label set, outside `{s, t}`, make a length-2 scratch
   word for `g`? One extra label equal to `g` writes it in one coordinate
   move, which is a different alphabet. The three-register rational-frame
   theorem is not this Cayley graph.

## Credit

The alphabet, the 28 rank-1 idempotents, the representation, and the open
question are from Riquelme Soares (@hevlyo),
`research/s3-diagonal-rank-screen`, following open PR #3893. The
three-register bound named by the card is not replayed. No source from that
screen is modified.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
No independent human review and no formal-kernel acceptance are claimed.
