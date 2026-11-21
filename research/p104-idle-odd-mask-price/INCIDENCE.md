# Odd-idle mask incidence: identity, bound, and sharp abstraction

This is a follow-up to the frozen `RESULT.md`, using the same #7852 head
`41beda1d6435760dc99e38bd7e65f36798aad212`. It does not construct a legal
caller or prove a caller ceiling.

## What the word incidence equality gives

For a legal word, `CallerAsm.word_count` states, for every stage `s`,

```
#{r : s ∈ M_r} = #{events e : s ∈ S_e}.
```

Summing over stages and interchanging finite sums gives
`sum_r |M_r| = sum_e |S_e|`. This consequence is a paper derivation of the
pinned theorem; it is not a new Lean declaration here. In a `GramA` or
`GramB` block, the J records contribute respectively 4k or 2k singleton
idle incidences. Thus, with `C=4` for A and `C=2` for B,

```
sum_{plain odd idle e} |S_e|
  <= sum_r |M_r| - C*k
  <= k*(n - C).
```

The first right side is a natural-number difference and is nonnegative under
the incidence equality. Combining it with the tight/block column count
`N_odd <= Q = n-(2k-2)` gives

```
sum_odd |S_e| <= min(Q*k, sum_r |M_r| - C*k).
```

Under the separate 26-bit matching hypothesis described in `RESULT.md`, one
may replace `Q*k` by `Q*min(k,26)`. This bound can be useful when an actual
caller has a small measured sum of target degrees. It does not by itself
control the complete corrected invoice: that also needs the mask-size
distribution or a valid bound on `sum δ(|S_e|)`.

For #7113, direct recount gives `sum_r |M_r| = 196` for each type. Type A
has 68 J incidences and 128 plain idle incidences; type B has 34 J and 162
plain idle incidences. The script checks this equality separately for every
stage. Their odd-idle incidence totals are 0 and 4, respectively. These are
finite data checks; word legality is not inferred from the counts.

## Why LawQ and incidence alone cannot sharpen the generic Q*k cap

There is an explicit abstract construction for **every** `k >= 3`, `Q >= 1`,
and `1 <= d <= k`. It attains `sum_odd |S| = Q*d`, satisfies the exact
stage matching, every field of `Cfg.LawQ`, and the event-data and pairwise
RC2 conditions below. Setting `d=k` attains `Q*k`. Setting
`d=min(k,26)` attains the 26-bit mask-size cap in this abstraction. It does
not assert the existence of a legal word or a signed-Gram frame.

Put `n = 2k - 2 + Q`; give all n roles the full k-stage mask. Take a fixed
d-element stage set `S`.

* For each of Q distinguished roles, take one distinct odd event with mask
  `S`, plus a singleton event for every stage outside `S`.
* For each of the other `2k-2` backbone roles, take one singleton event
  per stage. Choose the singleton pieces of these roles as the mains.

Each role's event masks partition its role mask, so the chosen match maps
each role and stage to its unique incident event. Thus every stage has
exactly n events, and the role-side and event-side incidences agree.
There are Q odd events with total mask size `Q*d`. The nominal column
count `2k+Q` equals `n+2`. There are at least four backbone singleton events
at each stage, enough to mark the 2 or 4 individual J contact incidences;
marking them does **not** construct J host records.

Every role has degree k and every matched piece size lies in `[1,k]`.
There are `(2k-2)k >= 2k` deep mains, no leaves, and `n >= k-2`, so the
degree, piece, mains, leaf and leaf-channel fields of `LawQ` hold. For
every `3 <= l <= k`, each backbone role contributes `k(k-1)` to the
`rowS` sum; the distinguished roles contribute nonnegative amounts.
The total is at least `2k(k-1)`, so all averaged RC2 fields hold.

The same example also has an `EvData`-level realization over the rationals.
Let `x_e=y_e` be the coordinate vector of the event's assigned role.
Different events assigned to the same role have disjoint stage sets, so
the `biorth` field holds whenever two event sets intersect; `x_supp` is
automatic because every role mask is full. Give `bh` and `ah` the first two
backbone coordinate vectors at every stage, zero elsewhere. Every `gBlk(s,t)`
is then the 2-by-2 identity, and each multi-stage distinguished event has
`x_ker` because its coordinate is outside those two backbone coordinates.
In the pairwise RC2 inequality, `gSet` has at most Q events and `wSet` has
n roles, so `2 + |gSet| <= 2+Q <= n`. These are abstract event data and
block matrices, not a matrix factorization of an actual caller word.

Therefore no stricter bound on the odd-idle incidence or per-event delta
can be derived from those abstract fields alone. Any stronger legal-caller
bound must use extra information such as the signed-Gram/endpoint structure,
actual mask distributions, or restrictions on how odd idles are realized.
The 26-bit correspondence is an additional hypothesis even for these
examples, and no 26-bit cap is claimed for the generic word model.

## Replay and pins

Run `python3 -B check_incidence.py`. It checks the construction at k=3, 17,
77, including Q=1 and Q=4 and d=1, 3, 17, 26, 77, and checks each stage of
the pinned #7113 data. The universal family is the elementary paper argument
above, not a Lean proof or exhaustive search.

Source reference paths relative to
`research/p104-lowerbound-toolkit/lean/Nov15/` and their SHA-256 at the
pinned commit:

```
CallerAsm.lean       702e2605d18b2edc337df7f98d0e76a217ba512061a19d7274ec86d68d4b1550
CallerHPQ.lean       51007003f362aebe1ef6e8c601b1dd1fb464680fb27e38e74a91f4cccd85064e
HPDual.lean          448a9ca56bb44cce162915649e1c279016c446c666760ce51ae7379488d1d788
CallerCfgBridge.lean c953575b4fa6bb6e4bc9311bffdce0f81ace3952856d60377a278406cec9a69d
CallerWordD.lean     fdcebd863b7639811782c51255232c0c88288eaacd0ff0e2618ad01799e3f3d8
CallerRC2.lean       b2be732b5314a837d5e80920ea6d3568f71d6d9dc434bc675d6fc7129e66293e
```

The original toolkit is attributed in `RESULT.md`. This follow-up adds the
incidence combination and an independently specified abstract construction.
