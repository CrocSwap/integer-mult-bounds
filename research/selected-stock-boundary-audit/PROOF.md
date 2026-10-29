# PR185 row-wrapper containment; selected-stage application unbound

## Conditional statement at the retained recursive boundary

Let the parent row wrapper receive two complete radix-`q` chunks `H,D`, each
of width `e`, and arbitrary complete spectators `Z`. Let `S(e,w)` be the
parent cover's row stock and `k = ceil(log_q S(e,w))`. Where `k < e/2` and the
retained completed-call contract applies, one completed high-part interchange
needs **zero additional external rows** beyond its two passed chunks. The
inner call can borrow internally; its borrow is contained in those chunks and
its row coordinate is restored before return.

This is a conditional result about the source-defined row wrapper. It is not a
numerical stock coefficient and does not, by itself, bind this wrapper to a
particular selected stage.

## Exact row-range trace

The retained `notes/three-stage-cover-rows.tex` splits the parent chunks as

```text
H = (H_hi, H_body)     D = (D_hi, D_body)
```

with `k` digits in each high part, in physical order

```text
H_hi, H_body, Z, D_hi, D_body.
```

The complete `q^k` range of `H_hi` is reinterpreted as the parent row field.
Since `k=ceil(log_q S)`, `q^k >= S`. Padding it to a multiple of `S` gives
less than `2 q^k` rows. The completed body wrapper uses this same range and
restores its row coordinate. After removing padding, the order is

```text
H_hi, D_body, Z, D_hi, H_body.
```

One completed width-`k` interchange then takes `(H_hi,D_hi)` as its two chunks,
with the bodies and `Z` as spectators, and returns

```text
D_hi, D_body, Z, H_hi, H_body.
```

Thus `H_hi` is temporarily the parent's row field and then an operand of the
completed child interchange. `D_hi` remains a spectator during the body call
and then becomes the other child chunk. The child does not receive a second,
disjoint row range from outside the parent. The row-range relation is
containment plus sequential reuse, not disjoint stock sets and not an additive
`S_parent + S_child` reserve. The increment in *external rows* at this one
source-defined boundary is exactly zero, conditional on the split and
completed-call hypotheses.

PR185's reviewed `A0` contract supplies arbitrary widths, two complete chunks,
complete spectators, internal high-digit borrowing and row-coordinate
restoration. PR387 states the same completed-call behavior for its own
six-level `A_j` construction, including the `A6 → A5` high-part call. The
retained text also says the legacy 252 allowance is unused slack, not an
estimate of the new leaf's internal reserve.

## Selected stage 6: arithmetic match, physical map missing

The selected record is bound at base
`20ecf2891d80b5acf18f980b2164fb44ea7faa90` (record SHA256
`bb2eaa58647b353f88d0aec2eafb9d30df1be53589231b23e12ceef3e4bad129`). Its
native inputs give

```text
a0 = 384599/10^10
c  = 1733427039589844234749/1000000000000000000000000
b  = 67018507072324140917/40000000000000000000000
beta = 1/10^24
s = min(c, (1-beta)b) - 1/10^27
  = 67018507072324140916999892981492927675859083
    / 40000000000000000000000000000000000000000000000.
```

The frozen PR1087 `outer_witness` initializes this same `a0`, sets
`eta=beta=10^-24`, and performs seven steps of

```text
a_j = (1-s)s + s a_(j-1).
```

Exact rational reconstruction matches every stored native exponent, including
entry 6 = `a6`. This is an arithmetic correspondence only. The PR1087 archive
binds the bootstrap cutoff recurrence and the `m=73` moment input; it does not
bind the selected physical stage 6 to an `A6 → A5` call map. PR387 is retained
in the stock audit's source ledger, but that archive alone does not establish
the selected physical call mapping. Therefore the conditional zero-increment
statement above cannot yet be entered as the selected stage's external-stock
term.

The selected stage-6 cutoff records
`L6 = 27452795513701194724472919763925196307643`. This result does not prove
that its actual parent stock gives `k6 < e/2` throughout `e >= 2^L6`; the
selected stock coefficient and width-domain binding remain open.

## Source pins and limits

- `notes/three-stage-cover-rows.tex` supplies the exact split, order, padding,
  restoration and completed width-`k` interchange. The copy retained in the
  stock audit is byte-identical.
- `research/bootstrap-depth-audit/sources/pr387/PROOF.md` describes its
  six-level call structure and completed borrowing contract.
- `research/bootstrap-depth-audit/sources/pr387/bootstrap-sources/research/community-round8-audit/pr185-proof-reviewed.md`
  binds the inherited complete `A0` interface to PR182.
- `research/complex-t16-rare-pattern-exchanges/upstream1087.tar.gz` is hash-
  bound by the selected source manifest and supplies the seven-step assembler
  recurrence and the `m=73` moment input.

No numeric value for `S6`, `sigma_6`, the internal child borrow, or the selected
additional external stock follows. The PR185 row note's `beta=1/1000` and depth
coefficient are not imported as selected constants. The selected 252 allowance
remains charged as written. No supplier, κ, or frontier claim follows.
