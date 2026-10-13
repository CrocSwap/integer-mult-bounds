# Mechanism brief and replacement specification

Douglas Colkitt, with OpenAI Codex assistance. Apache-2.0.
October 8, 2026. Preparation pass; no new construction or exponent.

## Main conclusion

Search for a **geometry and circuit that work together**, with a full
recursive cost profile. The present advantage is not explained by scalar
gate count, low matrix rank, or scratch compression alone.

The earlier [two-field core brief](../../docs/research/rank-product-core.md)
already identified the characteristic-dependent mechanism. This pass does
not claim to rediscover it. It updates the mechanism and selection criteria
to the reviewed PR82 two-stage, copied-center, mixed-width checkpoint.
Historical three-stage thresholds such as n>6rd must not be used as the
current acceptance test.

A useful refinement emerges: an independent transparent producer satisfying
JLV=I_n needs at least n auxiliary roles, by rank. This is stronger than
counting the current distinct source ports, but still scoped to that
factorization. Together with the current data-profile budget, it prevents
the rank-one 23x25 model from reaching 2^-9 through producer compression
alone, even with zero central loss and perfect batching.

## Where the positive saving actually comes from

**1. Different fields make the core possible.** For the triple construction,
let X have triple indicator columns. The binary central map is

    C_ST=|S intersection T| mod 2.

Its factor passes through h point totals. Its off-diagonal ones occur
exactly at intersection one. The rational form H=I-J/9 gives

    X_S^T H X_T=|S intersection T|-1,

so those pairs are rationally orthogonal while every label has norm two.
The side map adds the intersection-one contributions; over F2 it cancels
the off-diagonal central contributions and leaves the identity.

More generally, a binary diagonal-one matrix C of rank r and a rational
fitting matrix F of rank d, with nonzero diagonal and mutual off-diagonal
zeros where C has ones, yield compatible rational rank-one idempotents.
Neither matrix need be symmetric. If both ranks were computed over the
same field, the diagonal entrywise product would force n<=rd. Their
different characteristics avoid that obstruction. In the triple example,
the integral rational fitting matrix has diagonal two, which becomes zero
modulo two; importing its rational normalization into F2 is invalid.

This is the positive mechanism in the known structured core. It is not a
proof that every future multiplication algorithm must use two fields.

**2. The circuit makes that geometry usable.** Every intermediate producer
value needs a compatible frame, not just each input label. Nested frames
let most differences cost precisely their rank increase. For a point
center, the support lies in a codimension-one space of dimension h-1.
The cancellation-free producer, carrier continuations, and later frame
compiler keep these intermediate transitions affordable. A generic low-rank
factorization or a short XOR expression supplies no such guarantee.

**3. Completion and copying determine how much survives.** The two scalar
shears plus their paid rank-one endpoint correction replace the earlier
three-stage exchange. The copied-center schedule transforms a read-only
copy for scatter and sends the original directly to its cleanup frame.
It changes a center's paid rank pair (r,h) to (r,h-r); the r transform on
the copy remains paid. Arbitrary original auxiliary values still restore.

For the current pair construction the data operations, including the
endpoint correction, cost 2m-1 per data pair. Auxiliary roles cost their
full base m plus the remaining copied central losses. Therefore

    s=Wm-N+L,       Delta=N-L.

The gross saving is one rank unit per pair. It is a consequence of the
completed scalar/frame construction, not a free omission of a data role.
Role compression reduces W; copied centers reduce L; geometry and physical
batching determine how these rank units split into recursive calls.

At these particular small dimensions, copied centers do more than improve
a constant. Without that extension, the old two-stage ledger would give
N-2L=-379,500: no positive rank deficit. With it, N-L=1,846,900 is positive.
A proposed replacement must preserve or replace this readout mechanism;
importing only the older all-role core compiler loses a decisive ingredient.

## Current quantitative diagnosis

All figures refer to the [pinned PR82 inputs](../kappa-nine/baseline/SOURCE.json),
not a claim about later submissions or the selected release. The selected
release and all prior research remain unchanged.

| Quantity | Pinned value |
| --- | ---: |
| Ambient dimension m | 575 |
| Data pairs N | 4,073,300 |
| Independent roles W | 133,289,600 |
| Copied central loss L | 2,226,400 |
| Surviving rank saving N-L | 1,846,900 |
| Fraction of gross saving retained | 45.3416% |
| Roles per data pair W/N | 32.7228 |
| Normalized rank deficit eta | 0.0000240979 |
| Certified bit saving | 0.000052035506438388 |

The complete child profile, not eta alone, determines the saving. Define

    w_t=n_t*t/(Wm),
    Psi(a)=sum_t w_t*exp(a*log(m/t)),
    H=sum_t w_t*log(m/t).

Then Psi(0)=1-eta and the required test is Psi(a)<1. Since exp(x)>=1+x,

    a < eta/H

is a necessary condition. For the actual profile H is approximately
0.463058244; eta/H is approximately 0.000052040763. This closely brackets
the certified saving. H is a measure of the cost of splitting rank into
smaller recursive children; it is not a separately supplied implementation.

At a=1/511, the actual moment is approximately 1.00088553625. The required
bit saving is about 38 times the pinned saving. The retained balanced
assembly already converts almost all of its bit saving into kappa, so
assembly tuning cannot provide that factor while the finite network stays
fixed. At beta=1/20, the complex target is b>20/9709, about 29 times the
retained complex saving 717/10^7. A bit-only improvement is insufficient.

The script derives exact rational enclosures for H independently of the
stored logarithms and records each physical class's target moment penalty.
Decimals here are display summaries. No approximate inequality is used
to certify a budget or a bound.

## Required properties versus replaceable choices

| Property | Status and scope |
| --- | --- |
| Correct complete operation for arbitrary original data | Required by the retained interface; a zero-workspace example is insufficient |
| Account for every physical recursive call and its volume | Required; temporary dependent copies cannot enlarge independent role volume |
| Compatible intermediate frames and ordered tape implementation | Required by this transfer route; endpoint geometry alone is insufficient |
| Exact restoration of every auxiliary individually | Required by the present transparent invocations; a different fully specified all-role action may replace it in another contract |
| Triple subsets, point centers, dimensions 23 and 25 | Choices of the present construction |
| Rank-one labels, orthogonal projections, symmetric fitting matrices | Structured choices, not requirements of the general rational-frame interface |
| Cancellation-free side DAG and its grouping | Sufficient mechanisms for cheap frames; replaceable with an audited alternative |
| Two tensor stages and copied-center adapter | Current proven infrastructure; a different adapter requires a new proof |
| JLV=I through one independent auxiliary space | Current producer contract; replacing it changes the storage lower bound and proof obligations |
| Exact mixed-width moment test | Acceptance criterion for this recurrence; rank deficit alone is only a preliminary screen |

Changing a choice does not automatically preserve the rest of the proof.
For example, arbitrary idempotents are supported by the old raw core
compiler, but this does not automatically extend all modern copied-center
and ordered-batching arguments to them. Block labels likewise require an
explicit new ledger; substitute neither d/ell for d nor an unproved modern
profile merely because an older block compiler exists.

The characteristic-zero lift and fractional-routing obstructions have their
stated all-role additive-frame contracts. Apply them only after matching
the actual circuit, endpoints, copies and volume obligations. A copied
temporary is not a new independent demand. We do not promote those older
screens into universal obstructions for every copied-stream adapter.

## A joint design budget for the retained rank-one adapter

This is a **necessary optimistic screen**, not a theorem compiling arbitrary
new cores. A candidate must separately justify using this ledger.

For two axes let d_i be the rational dimension, n_i the label count,
R_i the independent producer role count and ell_i its copied central loss.
Define

    rho_i=R_i/n_i,       lambda_i=ell_i/n_i,       m=d_1*d_2.

Let f(t)=(t/m)^(510/511), and grant perfect whole-rank batching. The
data/growth numerator per pair is

    D=2f((d_1-1)(d_2-1))+f(1)+2f(d_1-1)+2f(d_2-1).

Compiler rank d_i*R_i+ell_i is packed into width-d_i children; each
auxiliary exterior is packed into one width-(m-d_i) child. The complete
optimistic moment is

    [D + sum_i rho_i*(f(d_i)+f(m-d_i))
       + sum_i (lambda_i/d_i)*f(d_i)] / (2+rho_1+rho_2).

Thus geometry, storage and central loss compete for the **same** budget:

    sum_i rho_i*A_i + sum_i lambda_i*B_i < C,
    A_i=f(d_i)+f(m-d_i)-1,
    B_i=f(d_i)/d_i,
    C=2-D.

Both A_i and B_i are positive. This formulation prevents crediting role
removal in the numerator while keeping its volume in the denominator.
Failure excludes the specified ledger; passing supplies only optimistic
headroom. Real fragmentation and added restoration can consume that headroom.

**The storage floor is algebraic within this producer model.** The maps
V:k^n -> k^R, L:k^R -> k^R and J:k^R -> k^n obey JLV=I_n. Therefore

    n=rank(I_n)=rank(JLV)<=rank(V)<=R.

This works over any field and does not require separate named input ports.
It covers a producer that factors the entire identity through its auxiliary
space. It does not cover a direct source-to-target contribution, interleaved
source access that no longer has this factorization, or a joint invocation
with different input/output obligations.

The following three named illustrations are specifications, not a parameter
search or proposed realizable networks. Ratios are taken equal on the two
axes to make the shared budget readable.

| Dimensions | Maximum rho per axis, granting zero central loss | Maximum lambda per axis, granting rho=1 |
| --- | ---: | ---: |
| 12 x 12 | strictly below 4.23457 | strictly below 0.260647 |
| 16 x 16 | strictly below 2.30633 | strictly below 0.152485 |
| 23 x 25 | strictly below 0.588180 | negative: impossible for nonnegative loss |

The last row conflicts with rho>=1 even if central loss vanishes. The
smaller rows show the scale of the desired joint improvement, not a reason
to start another small-dimension scan. For orientation, current triple
labels at h=12 and h=16 would have lambda=0.6 and 3/7 respectively, already
above the displayed limits before paying realistic producer storage.
Reducing dimension without changing the incidence/center mechanism fails.

The practical selection question is now: **which explicit new incidence or
block geometry comes with a circuit whose actual storage, central spans and
physical profile fit a budget of this kind?** Optimizing n/(rd) alone does
not answer it. In a copied-center compiler, the relevant central quantity
is the sum of the actual retained-center dimensions, not automatically rd.

## Replacement submission specification

A proposed replacement should provide the following together. Unknowns
must be marked as missing lemmas rather than filled with favorable counts.

1. **Exact algebraic core.** Label generator, scalar field, C and a certified
   factorization; rational F or block frames with normalized diagonal and
   mutual annihilation checks. Record n,r,d and block rank if applicable.
   Explain which identity uses the characteristic difference.
2. **An implementable producer.** Full source/mixer/scatter maps or a clearly
   different contract; physical role inventory; intermediate frame labels;
   all retained center spans and read/write lifetimes. Give a construction
   for the claimed R and ell, not just a scalar addition count.
3. **Completion.** Exact complete data map and arbitrary-auxiliary behavior;
   paid source, boundary, correction and copied-stream operations. State
   which existing adapter applies, or provide the replacement lemma.
4. **Physical profile.** Every child width and volume, one common ordered
   basis or a paid layout implementation, and complete normalized moment.
   An optimistic profile is a research gate; only an implemented profile
   can support a finite saving. Changed child volumes require a new recurrence.
5. **Complex partner.** Gaussian-dyadic scalar realization and binary phase
   frames, including normalization, forward/inverse signs and corrections.
   Merely exchanging the two fields of a fitting pair is insufficient.
   Supply a partner or identify the concrete missing phase lemma early.
6. **Scaling and provenance.** Exact finite controls plus a proof of the
   generative family or the full finite object. Identify inherited lemmas,
   contributors and unproved extensions. A tiny example's improvement must
   have a reason to persist at a useful scale.

After a complete pair of networks exists, recompute scalar guard charges,
maximum children, halving degrees, row stock, reservations, eventual
thresholds and all assembly inequalities. The old bridge is not reusable
without checking its changed inputs.

## Selection and next milestone

Prioritize a different characteristic-dependent incidence structure or a
block representation **with a proposed intermediate-frame construction**.
This is a search direction, not a selected candidate. The fixed triple
rank-two branch remains parked; these numbers do not reopen it.

Use two gates. First require a specific mechanism improving the joint
budget and an explicit producer strategy. Then require a complete positive
finite construction and a defensible scaling comparison before investing
in a large proof or claiming a route to 2^-9. A weaker positive replacement
may be worthwhile if its advantage scales; a family failing its own
optimistic budget should not enter construction search.

No particular new candidate currently meets this specification. The output
of this pass is the modern mechanism brief, a quantitative scorecard and
the evidence required to select the next experiment. It is not another
construction campaign or a promise of a breakthrough.

## Reproduction and attribution

```sh
python3 research/mechanism-prep/scorecard.py --output /tmp/mechanism-prep.json
python3 -m unittest discover -s research/mechanism-prep -p 'test_*.py' -v
```

See [exact certificate](certificate.json) and [validation](validation.json).
The preparation uses the repository's prior core/frame work, Paureel's
two-stage/copied-stream construction, Zhihao Chen's compatible transfer
accounting, icekylinx's copied centers, and the subsequent community producer,
basis and assembly improvements. The pinned PR82 data and existing source
notices retain their provenance; this pass claims no new construction or
priority for those ingredients. The full upstream analytic and fixed-tape
theorem remains an inherited assumption.
