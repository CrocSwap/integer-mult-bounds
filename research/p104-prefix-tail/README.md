# The P104 pooled correction first reaches dimension 98 at cut 2754

This resolves the interval left open by
[PR #2345](https://github.com/CrocSwap/integer-mult-bounds/pull/2345):

| Completed original events | Exact rational shared correction dimension |
|---|---:|
| 2718–2753 | 99 |
| 2754–2823 | 98 |

The lower proof uses fixed compressed determinants **−2** and **−1**.
A new 46-contact certificate attains dimension 98 at cut **2754**. The
rank-99 witness at cut 2646 is retained from #2345 and independently replayed.
In particular, **no earlier prefix can attain dimension 98**. This fills the
gap before the reported late-prefix results in
[Discussion #2245](https://github.com/CrocSwap/integer-mult-bounds/discussions/2245#discussioncomment-18940216).
We do not recertify that separate late-prefix package here.

**This is a rational pooled-snapshot model, not an executable correction or
a transport-cost reduction.** Pooling grants access at different times; the
new directions have no implemented creation, restoration or hosting bill.
There is no supplier or κ claim and no selected-frontier change.

## Exact model and independent replay

Use the unchanged PR #1972 word retained by the native PR #1991 package:
104 source inputs, 104 target inputs, 72 independent dirty helper inputs,
4,058 events and 4,059 cuts. A cut counts completed events. For each target,

```
S_t(c) = span_Q { v_r(d) : d <= c, r != Y_t,
                 frame(r,d) = frame(Y_t,d) as binary subspaces }.
```

All snapshots come from the original word; inserted rows do not change later
snapshots. Basis changes within a frame are free in this relaxation. Let `R`
be the 8-by-104 doubled root-coordinate matrix and `C=I_104-R^T R/8`.
The number `h(c)` minimizes `dim H` over rational spaces in all 280 boundary
coordinates such that `C_t in S_t(c)+H` for every target.

[trace.py](trace.py) is a fresh sparse integer/8 implementation, with no
imports from the earlier dense replay or native producer. It checks source
hashes, all 280 independent columns, every frame transition, private-copy
lifetimes, source/dirty restorations, the complete `G/2` endpoint and unchanged
local rank mass 2368. It independently recovers the same 110,814 distinct
target/snapshot pairs as #2345.

The collector visits each changed frame group. At an unchanged group both
membership and every logical row are unchanged, so revisiting cannot add a
snapshot. Requested contacts are checked separately at their exact cut,
including cuts where nothing in their group changes. This is exact reuse,
not sampling cuts. The relevant prefix pools contain 324 and 427 nonzero
target/coefficient pairs at cuts 2753 and 2823.

## Reduction to an eight-dimensional residual

We use the reduction proved in #2345, retaining its hypotheses and giving
the argument for standalone review. The full replay checks `R R^T=104 I`,
source projections in `row(R)`, absence of a target's own dirt from every
eligible donor, and availability of the other 175 independent nuisance units
at cut zero. The last two facts imply `pi_X(S_t)=S_t intersect X`: each
nuisance component can be subtracted inside the pool. Projecting any serving
`H` therefore gives a serving source-only space of no greater dimension,
and source-only spaces are allowed choices.

Put `L_t={a in Q^8 : aR in S_t intersect X}`. Choosing one local row per target
and taking the residual row span yields

```
h(c) = min_{A_t in L_t(c)} rank(C+12 A R)
     = 96 + min_{M in E(c)} rank(I_8-M),
E(c) = {R A : A_t in L_t(c)} = span{r_t a : a in L_t(c)}.
```

The substitution by −12 preserves each linear `L_t`. To see the rank identity,
write `D=R^T/8-12A`, so `C+12AR=I-DR` and `RD=13I-12RA`.
The restrictions of `R` and `D` are inverse maps between `ker(I-DR)` and
`ker(I-RD)`. Rank-nullity gives `rank(C+12AR)=96+rank(I-RA)`.
These statements quantify rational coefficients, including arbitrary dirty
components of the original `H`; they do not identify rational minimum rank
with a real or complex constrained minimum.

## Two small universal lower certificates

Indices below are zero-based, and `e_i` are the standard vectors of Q^8.
Use columns

```
p=e1-e0,  q=e2-e0,  w=e2+e3+e4+e5-e6+e7,
a=e0+e1,  b=e0+e2,  k=e7-e6.
```

For every generator `r_t alpha` of `E(2823)`, the checker establishes

```
p^T M a = p^T M b = q^T M a = 0.
```

These linear functionals then vanish on all rational linear combinations,
not only sampled matrices. For every residual `N=I-M`, the compression with
left rows `(p^T,q^T)` and right columns `(a,b)` is

```
[ 0  -1 ]
[-1   * ]       determinant = -1.
```

Compression cannot increase rank, so `rank N>=2` and `h(c)>=98` through
cut 2823. At cut 2753 the additional exact functionals are

```
p^T M k = q^T M k = w^T M k = 0.
```

Since `p^T k=q^T k=0` and `w^T k=2`, left rows `(p^T,q^T,w^T)` and right
columns `(a,b,k)` give

```
[ 0  -1   0 ]
[-1   *   0 ]
[ *   *   2 ]       determinant = -2.
```

Thus `rank N>=3` and `h(c)>=99` for every prefix through 2753. No nonlinear
search, optimizer status, approximate rank or characteristic-two determinant
is used for these rational lower bounds.

## Matching upper certificates and the exact break

Each entry `[target,cut,register,weight]` in [WITNESS.json](WITNESS.json)
contributes `weight * pi_X(v_register(cut)) R^T/104` to the target's row of
`A`. The code replays its availability, and the lifting facts above remove
nuisance components. The resulting `K=C+12AR` serves every correction row
since `K_t-C_t in S_t`.

The 18-contact cut-2646 witness from #2345 has `rank K=99`; it remains
available at every later prefix. The new 46-contact cut-2754 witness gives
exactly

```
N = x (e1+2e7)^T - e1 e2^T,   x=-e2+e3+e7.
```

This has rank two: the persistent compression is nonsingular, and the
displayed sum has at most two rank-one terms. The checker independently
computes both `rank N=2` and `rank K=98` by rational elimination.
At this cut the old `q^T M k=0` constraint is no longer true: in the new
residual `q^T N k=-2`, while `p^T N k=0` and `w^T N k=2`. Thus the earlier
3-by-3 argument cannot be extended past its checked prefix.

Pools grow monotonically. The cut-2646 upper and cut-2753 lower prove 99
throughout the first interval; the cut-2754 upper and cut-2823 lower prove
98 throughout the second. Contacts are algebraic membership certificates,
not literal added chronological instructions.

## Reproduce

Standard-library Python, with read-only default commands and no network,
Git or pending-package code needed for the direct checks:

```sh
python3.12 -I -O -B research/p104-prefix-tail/verify.py
python3.12 -I -O -B research/p104-prefix-tail/test_verify.py
python3.12 scripts/research_package.py --package research/p104-prefix-tail
```

Expected primary line: `PASS_P104_PREFIX_TAIL 99 through2753; 98 from2754 through2823`.
The full [RESULT.json](RESULT.json) must match. `--out NEW.json` writes only
to an unoccupied path. The registered replay also runs failure controls;
its metadata needs Git provenance, unlike the direct replay. Tests cover
corrupt contacts, future/self contacts, nonzero compensation/cleanup faults,
and low-rank counterexamples when required compression constraints are dropped.

The proof and finite certificates were checked with rational arithmetic and
a separately implemented source-projection exploration. Native Gaussian
recipe regeneration, chronological correction execution, global moment and
owner assignment, precision/all-size admission and selected cold replay are
not performed. Hosted CI and independent human review remain separate.

## Open next questions

- **Turn one complement into a fully charged chronological construction.**
  The available snapshots do not make its 98 shared directions free. Begin
  with source reads, frame paths, creation/restoration and owners, then price
  the entire word. Existing fixed-frame/retained-cost obstructions still apply.
  No implementation contract is supplied here.
- **Connect the independently published prefix certificates.** The reported
  97 interval from 2824 and 96 interval from 2912 can be combined with #2345
  and this package after checking their exact artifacts and source bindings.
  Start with a source-bound replay/index of those certificates; external
  late-prefix evidence is not rerun by this package.

## Sources and attribution

Scientific base: canonical main `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`,
priority revision 4, freshly fetched at the second-round checkpoint. Only
this new package is added; the first-round PR is not a parent dependency.
[TASK.json](TASK.json) records the handoff, scope, freshness and overlap;
[SOURCES.json](SOURCES.json) pins both frozen inputs.

Gonzalo Mier/#2173 supplied the pooled model and dimension question;
Gareth Davidson/@bitplane/#2251 supplied the full-pool complement;
@josecarlosgonzalezroque-design supplied the late-prefix result and the
handoff in Discussion2245 comment18940216. AAAmirinu/#2345 at
`2a5fa34a967e7567abf01611f92a6ab69e8c901a` supplied the rank reduction and
the reused cut-2646 witness. Those are not new claims here.

Rohan Arun/#1972 supplied the scalar/frame channel; Chafik Boukhalfa/#1991
its native realization; Adam Gall/#1940 the schedule; Josie Elliston/#1071
the fixture, with Ali Romman/#1125 and the retained geometry/decoder lineage.
Original files and notices remain unchanged.

Prepared for AAAmirinu with substantial OpenAI Codex assistance in proof,
implementation, testing and prose, including separate projection exploration,
sparse replay and mathematical review. Author-checked evidence; no independent
human review or proof-assistant claim. Apache-2.0.
