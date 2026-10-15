# A terminal-cut floor for the P104 side correction

**Scoped obstruction, not a new supplier or kappa.** After the complete P104
native channel has finished, any correction in the canonical common-chart model
below costs at least **104 additional paid ranks**, even if owned clean copies
and their disposal are granted for free. Without allocation/disposal the floor
is **208**. The lower bound concerns arbitrary-length schedules, arbitrary
rational scalar mixing and arbitrary dirty workspace, not a search over a few
words.

Under the retained paired-chain, one-unpaid-coordinate coverage contract, the
104-rank floor alone makes the completed channel's moment exceed one already
at saving zero. At nine stages, even the optimistic full bill is

\[
 M(0)\ge\frac{72\cdot832+(56+104)\cdot9}{73\cdot832}
       =\frac{1917}{1898}>1.
\]

Thus this **post-completion route cannot improve the selected supplier within
that coverage contract**, regardless of idle packing. Earlier interleaving,
changed chart operations and changed coverage laws are outside the theorem.

## Exact object and predecessors

Rohan Arun's [PR1972](https://github.com/CrocSwap/integer-mult-bounds/pull/1972),
head `fd82d172f46933fd253c2c6de4bd5eaff5429cfd`, supplies the full scalar/frame
word. Chafik Boukhalfa's [PR1991](../p104-native-channel/README.md) supplies its
native realization. Their result is retained, not claimed new:

- 104 sources, 104 targets and 72 independent arbitrary dirty helpers;
- 4058 events and the local paid profile
  `{1:1074,2:58,3:86,4:104,5:48,6:24,7:8,8:8}`;
- rank mass `2368 = 2312` persistent boundary progress `+ 56` private-copy mass;
- terminal logical rows `X_s=x_s`, `Y_t=y_t+(Gx/2)_t`, with every dirty helper
  restored; `G[t,s]` is the ordinary Gram matrix of the pinned 104 E8 root lines.

The cut is **after all 4058 events**, including query cleanup. Every source and
all 72 helpers are at the full nine-dimensional frame `F`. Target `t` is at its
rank-eight hyperplane `H_t=q_t^perp`; all 104 hyperplanes are distinct. The
correction is `S=I-G/2`. Each row has 48 nonzero entries, all off diagonal.

Concurrent public claims by **1337isnot1337**,
[18931708](https://github.com/CrocSwap/integer-mult-bounds/discussions/1167#discussioncomment-18931708)
and [18931718](https://github.com/CrocSwap/integer-mult-bounds/discussions/1167#discussioncomment-18931718),
now collected in [discussion 2080](https://github.com/CrocSwap/integer-mult-bounds/discussions/2080),
already describe the terminal target-up/add/down construction with 208 rank-one
uses and its direct-target path floor. Neither that construction nor that
restricted floor is new here. Our 208 bound permits arbitrary mixing and moving
other registers; the stronger new question admits disposable copies and proves
the 104 floor and complete coverage obstruction. The earlier
[query-live proposal](https://github.com/CrocSwap/integer-mult-bounds/discussions/1167#discussioncomment-18931651)
was withdrawn by its author for independent query-dirt leakage. Earlier cuts in
general are not excluded by our theorem. Discussion 2080's favorable conditional
profile screen is not used as a coverage proof: the new terminal mass must be
charged in addition to, not in place of, required idle progress.

## Model: an explicitly favorable relaxation

Each register has a canonical binary subspace chart `Gamma_W` and an exact
logical row over the independent persistent inputs. Permitted operations are:

1. arbitrary rational additions between registers in the **same chart**;
2. a nested transport `Gamma_B Gamma_A^-1`, charged `|dim(B)-dim(A)|>0`;
3. fresh owned zero rows, same-chart copying, and disposal of owned rows.

All persistent logical endpoints and frames must be restored except for the
required target increment `Sx`. Extra arbitrary dirty helpers may be supplied at
`F`, but must be restored there. No informative input may be inserted for free
at a target chart. Free monomials inside a paid recipe do not authorize an
unpriced change of the declared common chart.

Allocation, copying and disposal in item 3 are deliberately **more permissive
than a demonstrated physical supplier contract**. In particular, preparing and
discarding a full-frame copied address function is not asserted to be an
admitted all-size primitive. Granting these operations can only weaken a lower
bound. The attaining 104-rank word below is an attainment in this relaxation,
not a completed physical P104 supplier. The older channel's private lifetimes
remain unchanged.

## Proof of the terminal floor

### 1. Every target chart must be touched by a transport

Fix `H_t` and suppose no transport has either endpoint there. Initially the
only nonzero row in that chart is

`z_t = y_t + (Gx/2)_t`.

Every additional row created there is zero or is copied from a row in that
chart. Additions, copies and disposal therefore leave all rows in the linear
span of `z_t`. This remains true for any finite number of registers and any
finite-length schedule. Arbitrary dirt at other charts cannot enter.

The final persistent target would have to equal `c*z_t`. Since `y_t` is an
independent input and its final coefficient must be one, `c=1`. But the required
final row is `z_t+(Sx)_t`, and `(Sx)_t` is nonzero. This is a contradiction.
The argument allows arbitrary mixing and does not assume a selected set of
reads, a particular correction factorization, or a bound on program length.

### 2. One transport cannot pay for two distinct target charts

Two distinct eight-dimensional subspaces of the same nine-dimensional space
are incomparable. A nested transport therefore has at most one of the 104
`H_t` as an endpoint. Its rank is at least one. Charge each target chart to one
incident transport; no transport receives two charges. There are at least 104
paid ranks.

Without allocation or disposal, register occupancy at each chart is conserved
between the fixed initial and final boundaries. Once a chart is touched, an
arrival must be balanced by a departure. Thus there are at least two incident
transport occurrences at each `H_t`, proving the 208 floor in that smaller
model. This is an occupancy argument, not an assumption that the target itself
must move.

The executable checks the actual physical hyperplanes and the nonzero side
rows. The arbitrary-length implication above is a written proof; finite
mutation tests are not its substitute.

## Matching relaxed word and native transport identity

For each target `t`, sequentially:

1. Initialize owned `C=0` at `F` and copy one source into it.
2. Use same-chart rational additions to make `C=(Sx)_t` exactly. The coefficient
   of the copied source is adjusted by one, so the COPY is counted explicitly.
3. Transport `C: F -> H_t` with one positive rank-one child.
4. Add `C` to `Y_t` and dispose of `C` at `H_t`.

All sources, all dirty helpers, and every target frame stay fixed. There are
104 owned lifetimes, 5096 scalar additions, 104 copies, 104 initializations,
104 disposals and 104 rank-one transports: **5512 correction events**. The
completed local profile is
`{1:1178,2:58,3:86,4:104,5:48,6:24,7:8,8:8}`, rank mass **2472**.

The new frame transport is checked as a complete operator, not just by counting
a dimension difference. Let the pinned rank-zero exit adapter be

`A_t = F9 C_q^-1 Gamma_H^-1`.

Then

`Gamma_H F9^-1 = A_t^-1 C_q^-1`.

For the odd nonzero physical normal `q`, `C_q^-1=X_q C_q`. Choose an invertible
binary matrix `P` with `P e_0=q`. Then `C_q=P C_e0 P^-1`: one positive rank-one
child, surrounded by monomials. The retained independent Gaussian-dyadic
interpreter checks this expression against the literal chart transport for
all 104 targets, including signed Pauli action and a nonzero exact state column
to fix the global phase. It also rechecks the pinned exit adapters and all
14,400 physical root-pairing identities. No Clifford compiler or producer is
imported.

This verifies the new **operators**. It does not upgrade the relaxed owned-copy
lifecycle into a physical construction. The prior native core is inherited
from PR1991; this package independently replays its scalar/frame word over all
280 arbitrary persistent inputs rather than rerunning all of its native recipes.

## Completed optimistic bill and why idle mass is not a credit

We keep the paired-chain skeleton with `s=2p+1` stages, `m=16p+9=8s+1`, and
`W=2p*v=(s-1)v` live data families per replica. These formulas are source-bound
to Dominik Scholz's retained
[`larger-gain` model](../larger-gain/geometry/stage_relaxation.py), lines 34–40.
Substituting `v=104` is an **explicit conditional template choice**, not an
assertion that a P104 global owner construction has been admitted. At `p=4`,
`W=832`, `N=s=9` and `m=73`.

The coverage premise is one unpaid coordinate per live data family, with all
other coordinates advanced by the local boundary paths or the idle children.
Sagar Thakrar's [PR1012](https://github.com/CrocSwap/integer-mult-bounds/pull/1012)
and Douglas Colkitt's [packing-ceiling package](../complex-local-word-ceiling/README.md)
supply the coverage-law context. We do **not** silently apply the unchanged
selected-word ceiling to a changed word.

The actual core boundary contribution is

`104*8 + 104*8 + 72*9 = 2312` per call.

Its 56 private drop ranks do not advance persistent endpoints. Under the fixed
coverage premise, nine calls leave

`72*832 - 9*2312 = 39096`

units of idle coverage to be advanced. These are not free spare paid ranks.
After the strict completed cut, every persistent register starts and ends at
the same frame, so the correction has **zero net persistent frame progress**.
A persistent excursion must return; an owned private drop advances no live
family's endpoint. Hence the added terminal transport mass does not replace
any of those 39096 units. Debiting 104 per call from that old idle amount would
claim coordinate progress that the correction does not provide. The verifier
includes precisely that erroneous invoice as a rejecting control.

Favorably charge no scalar cost, no new allocation/disposal cost, no extra
precision cost and no hosting penalty. The full lower bill still is

`9*(2312+56+104) + 39096 = 61344 > 73*832 = 60736`.

Every recursive child has `0<r<=m`. For `0<=a<1`,
`(r/m)^(1-a) >= r/m`, so the zero-saving rank-mass inequality already rules out
`M(a)<1`. This conclusion needs no numerical root or irrational interval.

Fully paid auxiliary banks do not repair the deficit: a bank contributes `m`
to both paid mass and capacity, as in the retained
[`screen_stages.py`](../larger-gain/stages/screen_stages.py), lines 61–66. With
`B` such banks the bound is `1+608/[73*(832+B)]>1` for every finite `B`.
A bank granted an unpaid coordinate would be a changed coverage contract.

More generally, if the same retained template is feasible at another odd stage
count, its deficit satisfies

`D <= 104*(s-1) - (56+104)*s = -56*s-104 < 0`.

This algebraic extension is conditional on the same coverage assumptions. It
does not certify a global template or hosting at any additional stage count.

## Reproduce and evidence

Standard-library CPython 3.12; all external inputs are authenticated before the
retained Gaussian interpreter executes. Source archives and selected evidence
are read-only. The normal command regenerates the complete result in memory and
compares canonical parsed JSON, not gzip headers:

```sh
uv run --python 3.12 --no-project python -I -O -B research/p104-terminal-correction-floor/verify.py
uv run --python 3.12 --no-project python scripts/research_package.py --package research/p104-terminal-correction-floor
```

`--write` explicitly regenerates `RESULT.json`. The receipt records the complete
source hashes, correction program digest, native-circuit digest, paid profiles,
exact budget and eight semantic controls: omitted correction, wrong coefficient,
dirty copy contamination, omitted frame descent, disposal of a persistent
target, unrestored source, wrong native global phase, and double-spent idle
credit. `-O` does not disable the verifier's checks.

The author-run optimized generation and registered replay both passed. A
separate AI-assisted reviewer read the proof and code and ran the unchanged
registered package successfully, including all eight controls. This is a
separate replay, not an independent human or formal-kernel verification.

The task card's working example passed `PASS_RESEARCH_BASELINE_BINDINGS_ONLY`:
the selected conditional kappa remains `0.001672660197076918`. This is a source
binding check, not a selected cold replay. Actual package validation is recorded
in `TASK.json` and `RESULT.json`; no hosted CI or formal-kernel run is claimed.

## Open next questions

1. **An earlier chronological cut.** Can the side correction reuse a source and
   target chart before their native paths finish? This could avoid a separate
   terminal excursion. First list the simultaneous charts at one earlier cut
   of the pinned witness, then test a fully priced identity. This package does
   not supply that schedule.
2. **A changed coverage contract.** Could an actual interface provide more
   unpaid coordinates or share the correction with another required operation?
   First derive its complete family/call and endpoint coverage law. Simply
   deducting terminal cost from old idle coverage is not such a derivation.

Structured first steps and blockers are in `TASK.json`. An arbitrary native
operator alphabet allowing chart changes outside the stated nested common-chart
model is also outside the lower bound. Precision, physical copy/erase admission,
chronological hosting, all-size lifting and the bit supplier remain untouched.

## Provenance and credit

Base `564148b82ae9df72163f22106f15e73efca8aff2`, priority revision 4;
one independent selector seed `cfe3b8f6d8ab3b2c86dececdc8d1d726`, retained in
`SELECTION.json`. Exact Git/SHA256 pins and overlap limits are in `SOURCES.json`.
Submission overlap covered 353 open PRs including drafts and 738 discussion
records with complete pagination, plus targeted live and local source reading.
Canonical main `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2` changed guidance only;
its updated instructions were read and original scientific pins retained.
This is not a literature-priority or novelty guarantee.

Credit Rohan Arun / PR1972 for the complete low-rank word; Chafik Boukhalfa /
PR1991 for the native channel and physical label binding; Adam Gall / PR1940 for
the target-order schedule; Josie Elliston / PR1071 for the P104 fixture; Ali
Romman / PR1125 for the earlier path-cover bound and PR1862 for the independent
Gaussian interpreter, retained through PR1931; the PR968/717/446/595/620 geometry
lineage; and Dominik Scholz, Sagar Thakrar / PR1012 and Douglas Colkitt / PR1240
for the template and coverage context. Predecessor files and notices are unchanged.

Prepared for Adam Gall with substantial OpenAI Codex assistance in proof,
implementation and exposition. New material is Apache-2.0. No independent human
review, formal proof assistant, admitted supplier or new multiplication exponent
is claimed.
