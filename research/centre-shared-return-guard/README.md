# Shared two-panel centre return with a precision guard

This completes the **reverse centre-phase contract** complementary to
[PR1708](https://github.com/CrocSwap/integer-mult-bounds/pull/1708), at
`4d163c04c0980c5b0e9092fbd5864c7cfadc125d`. It binds the eight selected R480
backward blocks and supplies a fully charged conditional two-panel rewrite.
No new generic adjoint identity, supplier admission or kappa is claimed.

## Contract and proof

There are eight shared source/sink rows `S_k` **after A**, two disjoint panels
`D_a,D_b` of 112 rows each, and eight scratch roles `C_k`. Sources, panels and
scratch are disjoint. Both panels are at frame ZERO. For each centre, both
invocations use the same exact return operator `B_k`, chart and sink. No source
or panel mutation, observation or required canonical checkpoint intervenes.
Both comparators reuse the **same eight scratch rows**; their arbitrary incoming
contents are erased, and all scratch outputs are zero. Scratch dirt is not
promised to return to its incoming value.

The pinned reverse block is: CLEAR at ZERO, 22 panel gathers, one rank-8 ascent
`0 -> 415+k`, source subtraction, CLEAR at `415+k`. Its forward counterpart
uses the inverse operator `F_k`; in the retained unitary semantics,
`B_k=F_k^-1=F_k^dagger`. The 22 actual coefficients `d_kj` are real rationals.

Write `u_k=sum_j d_kj D_aj` and `v_k=sum_j d_kj D_bj`. The two separate blocks
write `S_k <- S_k-B_k u_k-B_k v_k`. The fused block gathers both panels before
one ascent, then writes `S_k <- S_k-B_k(u_k+v_k)`. Linearity proves equality
for every complex payload and every exact common `B_k`. Neither panel changes.
Initial CLEAR removes arbitrary scratch dependence; final CLEAR establishes
the promised zero endpoint. This is the signed adjoint of the **persistent
block**, not the transpose of an invertible full scratch map: CLEAR is singular.

The rewrite needs one common operator per corresponding centre, not one
operator shared by all eight centres. A caller must establish the shared
post-A rows and the stated uninterrupted phase window. This package supplies
neither a full pair of fused local calls nor an eligible selected owner pair.

## Complete phase bill and precision boundary

| Backward primitive | Two literal phases | Shared return |
| --- | ---: | ---: |
| Rank-8 return | 16 | 8 |
| ADD, including every panel read | 368 | 360 |
| CLEAR | 32 | 16 |
| Total macros | 416 | 384 |

All **352 panel gathers** remain; the eight saved ADDs are source writes.
Backward has no COPY. These compare the literal retained grammar, not optimal
circuits. Required initial CLEARs and label resets are retained in both words.

For each centre, the single-panel positive gather envelope is
`E=sum_j |d_kj|=11/2` times the common input bound. The combined envelope is
`E_a+E_b <= 2 max(E_a,E_b)=11` times that bound. A fixed exact linear child
prefix may also depend on unchanged private dirt `w`: write
`P_t(u,w)=K_t u+L_t w`. With a common worst-case private envelope `E_w`, its
positive bound satisfies
`|K_t|(E_a+E_b)+|L_t|E_w <= 2 max(|K_t|E_a+|L_t|E_w, |K_t|E_b+|L_t|E_w)`
componentwise. Thus the factor-two guard does not assume clean child-private
scratch. Actual child prefixes and their private envelopes remain uninstantiated;
this exact argument does not certify nonlinear or rounded prefixes.
The source endpoint has the same two-panel contributions as
the baseline. One extra **magnitude bit suffices for this local positive bound**.
It does not establish rounding-error, native guard, tape or global admission.
Observed cancellation is unusable: inputs `+1,-1` have final sum zero but a
nonzero prefix. The positive bound is attained by aligned panel signs.

If `mu` supports the complete separate phase, conservatively price every fused
primitive at `mu+1`. With the actual primitive tariffs and additional overhead
`DeltaH` for preparation, routing, ownership and hosting, compare

```
separate = 16 R8(mu) + 368 ADD(mu) + 32 CLEAR(mu)
fused    =  8 R8(mu+1) + 360 ADD(mu+1) + 16 CLEAR(mu+1) + DeltaH
```

The rewrite helps only if `fused < separate`. No actual tariff or zero overhead
is inferred. Under the illustrative tariff where every macro costs its width,
the saving is `32 mu-384-DeltaH`: zero-overhead tie at `mu=12`, positive at
integer `mu>=13`, and at `mu=13` extra overhead must be strictly below 32.
This is a model example, not a recursive child price or runtime claim.

## Evidence and reproduction

[RESULT.json](RESULT.json) binds all eight blocks to decompressed members of
the selected replay archive, including both complete event hashes, frame bases
and all 176 coefficients. Separate and fused emitted words agree with an
independent closed-form endpoint on **480 complex basis inputs**: eight shared
rows, both complete 112-row panels and eight private roles, with two coordinates
per row. Eight exact phase-bearing Gaussian-rational unitary representatives
and their adjoints exercise the abstract child interface. This is **not** a
replay of the actual 512-dimensional centre operators; the written linearity
argument covers arbitrary operators under the stated hypotheses.

Seven exact fault witnesses reject missing initial/final CLEARs, a missing
panel read, wrong source sign, using the forward operator, mismatched second
operator and crossing an intervening sink scale. The full weighted bill,
positive envelopes and strict overhead boundary are checked separately.

```
python3.12 -B scripts/research_package.py --package research/centre-shared-return-guard
```

Normal replay is read-only; `verify.py --write-result NEW_PATH` refuses to
overwrite. [TASK.json](TASK.json) records the refinement of the revision-3
`centre-path-sharing` card, nonce `1e94dbbfba8c1dc58dbab4dcba380ae3` and base
`0b1cccf86e2f5132ed286a26ef0a681a495740ea`. [SOURCES.json](SOURCES.json) pins
every input. The selected record and frozen predecessor packages are unchanged.

## Open next questions

- Does an actual caller have these shared post-A rows, matching charts and an
  uninterrupted two-panel phase? Trace one pair through the selected owner and
  call schedule; preparation, cleanup, ownership and disjoint footprints remain
  blockers. An abstract common sink does not establish an eligible pair.
- Do actual child/scalar tariffs and available precision headroom satisfy the
  guarded inequality? Instantiate the native prefix/error bounds and `DeltaH`.
  One magnitude bit alone does not prove fixed-precision or tape admission.

Credit Cinna Davis/1337isnot1337 (PR1708 forward fanout), Sagar Thakrar (PR751
common-target backward batching), Ryan Haines (PR830 transposed work and prefix
warning), Scratch-net (R480 private-centre adjoint/CLEAR audit), Jeremy Kothe,
Rohan Arun, Hao Yan, DreamingOfClouds, icekylinx, Chafik Boukhalfa and the retained
selected-construction lineage. Generic batching/adjoint algebra remains prior
work. New selected-source return certificate and precision guard: @ToikY with
substantial OpenAI Codex assistance, including bounded implementation and review
subagents. Apache-2.0; original notices preserved. No human or Lean review.
