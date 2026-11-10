# The helper-462 swap-free word does not beat the published ordinary bill

## Statement

Let `S` be the pinned helper-462 matcher in
`research/bit-completed-backend-api/science/RESULT.json`. Two right
factorizations into axis swaps, single-column scales and shears are compared
at tensor width `N = 8f`.

The published factorization has 5 swaps, 5 scales and 14 shears. Four of
those shears update the earlier column. The zero-swap factorization has 7
scales and 27 shears, of which 10 update the earlier column. Both words
multiply to `S`, and both inverse words multiply to `S^-1`.

Under the inherited stream rule, each swap site and each earlier-target shear
site is a completed ordinary call, and an earlier-target site contributes two
such calls. Later-target shears and scales contribute none. The pair bills are

```text
published ordinary calls  = 208 f^2
swap-free ordinary calls  = 320 f^2
```

For every positive integer `f`, `320 f^2 > 208 f^2 > 80 f^2`. At the published
pair ledger, `f = 1`, the swap-free bill is 320 ordinary calls against 208,
and 320 does not beat 80. No new κ follows. The selected value stays
`781451/250000000`.

## What the pinned sources actually charge

The route generator emits, for an additive factor `(add, i, j, z)`,

```text
ordered_shift(target = row*N + j*f + lane,
              source = row*N + i*f + lane,
              coefficient = z)
```

and one `older_full_swap` for a swap factor in the full-width branch. The
inverse negates a shear coefficient and inverts a scale, and it keeps the
same address pair. `physical_tape_cost_closed` is false in that generator.
Coefficient preparation remains a charged P2 obligation there; it is not given
a number.

`add_high` in `qadic_streams.py` returns immediately when the high length is 1.
Otherwise a reversed-field call runs `completed_swap_oracle`, then the forward
scale/rotate body, then `completed_swap_oracle` again. The forward call does
not. The oracle records one `meter.ordinary` entry and its docstring charges
that body as `T_old`, never as a linear stream primitive. The function text
contains no transition count. The earlier-target proof states the same two-call
charge and says no fixed-tape transition bill for the oracle is claimed.

On this address layout the target is the earlier column exactly when `j < i`.
The earlier-target proof anchors the published elimination at four such
shears and ten later shears, hence `64 f^2` earlier sites and `160 f^2` later
sites. Recomputing the elimination from the pinned matcher reproduces that
split. The same address test applied to the zero-swap word gives 10 earlier
shears and 17 later shears. The inverse keeps both splits, because negation
does not exchange the two columns.

A swap site is one P2 older completed ordinary interchange of the two high
fields. An oracle call is one completed ordinary call exchanging those same
two high fields. They are the same call shape, so they add. They are not given
a common transition number.

## The two bills

Each letter expands once per direction, once per row in `0 .. 8f-1`, and once
per lane in `0 .. f-1`. That is `16 f^2` sites per letter. With two ordinary
calls on each earlier site,

```text
published = (5 + 2*4) * 16 f^2 = 208 f^2
swap-free = (0 + 2*10) * 16 f^2 = 320 f^2
```

The published ledger's 80 ordinary chunk interchanges are the `80 f^2` swap
sites at `f = 1`, not the oracle calls. Adding the inherited oracle charge,
which the published word also pays (`128 f^2` calls), is required before the
two words are on the same ordinary bill. The zero-swap reading that charges
those shears at no ordinary calls would report 0 and would beat 80. The
source text rejects that reading.

The coarse ledger sometimes treats `f` as not multiplying the 8-row count.
That reading gives the same pair totals 208 and 320, without an `f^2`. Either
reading has the swap-free word strictly above both 208 and 80.

The borrowed branch replaces each full-width swap by a narrower high
interchange plus the raw-body wrapper. It does not remove the earlier-target
oracles, which still exchange full high fields of length `q^(w-1)`. The
published side then has `128 f^2` full-width oracle calls plus `80 f^2`
narrower interchanges. The swap-free side has `320 f^2` full-width oracle
calls. It remains strictly above 80 full-width ordinary calls.

Carry shifts and the two low-type commits are emitted from `S`, not from the
choice of factors. They are the same for both words and cancel in the
comparison.

## Affine sufficient charges that were not added

Both words' scale coefficients, including inverses, lie in the signed-dyadic
family `{2, 1/2, -1, -2, -1/2}` stated for this route. That family's
sufficient charge is `2048 V_s` transitions per site, with `V_s = P Q S`.
The pair scale sites are `80 f^2` and `112 f^2`, so the sufficient charges at
`f = 1` and a common site volume are `163840 V_s` and `229376 V_s`.

Every shear coefficient that occurs has absolute value `1`, `2` or `1/2`.
For odd `Q > 2` each has a residue in `0 .. Q-1`. The forward affine kernels
bound a supplied residue by `1024 V_h` transitions, `V_h = P Q^2 G S`. The
linked half program prepares `(Q+1)/2` inside that bound. Other residues,
including the modular images of `-1`, `-1/2` and `-2`, remain supplied
descriptors; preparing them is still a caller cost. Counting one forward body
on every shear site, the sufficient charges at `f = 1` are `229376 V_h` and
`442368 V_h`.

`V_s`, `V_h` and `T_old` are different units. The sufficient charges above are
upper bounds, not exact invoices, and the oracle term has no transition
number. They are recorded so the priced families are visible. They are not
added to the ordinary-call bill, and they are not a claim that the swap-free
word loses by a specific transition total. The ordinary-call comparison does
not need that total: both words are charged in the same positive ordinary
call, and the swap-free word uses more of them.

## Stop

The comparison asked whether this legal word beats the published pair on the
completed ordinary bill, and whether that bill beats 80 ordinary interchanges.
It does neither. The missing numeric transition tariff for one
`completed_swap_oracle` would put `T_old` and the affine bounds on one tape
invoice. It cannot reverse an ordinary-call gap of `112 f^2` calls while
those calls stay positive and equal. This package does not search another
factorization, shorten the 27 shears, or install the word in a caller. No
selected-frontier change is made.
