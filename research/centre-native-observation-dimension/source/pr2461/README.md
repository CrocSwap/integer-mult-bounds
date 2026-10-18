# Sharp owner-local observation cost for selected centre reuse

**Scoped information theorem with exact finite premises; no new supplier or kappa.**
For selected calls 0 (forward stage 0) and 4 (backward stage 1), recovering the
**whole later eight-query field** from the saved first eight-query field needs
**104 additional scalar coordinates at every old cover owner**, if each extra
observation depends only on that owner's initial 112 source values. This is
sharp in that observation model. Arbitrary cross-owner observations are a
different interface: the eight later query fields themselves suffice.

This answers the additional-old-chart-observation handoff of
[PR2391](https://github.com/CrocSwap/integer-mult-bounds/pull/2391), head
`5efcbb6058d27aa8b988db8f18c7b678166b2783`. That predecessor gives one native
kernel counterexample. The new result quantifies a complete repair under an
explicit locality restriction; it is not another scalar rank census or another
check of that one witness.

**104 is an information dimension per owner, not 104 recursive children or
104 rank-mass units.** A full-cover field has one scalar at *each* owner. The
separate 112-read result below counts evaluations for one output owner, not
112 full-cover fields. No such number is substituted into a supplier invoice.

## Contract and theorem

Let G be the actual finite orthogonal cover group. For every physical owner
`g in G`, let `x(g) in C^112` be arbitrary independent source-data differences.
Each coordinate is a payload-constant function on every physical address and
spectator factor. Initial target/helper dirt is held fixed in the two compared
executions. Restricting input differences this way does not assume clean
workspace. This is a valid restricted input model, not a claim that all native
inputs are constant.

Let R be the eight-by-112 forward centre matrix extracted from the pinned
selected word. After undoing invertible carrier conventions, the old transcript
is `z(g) = R x(g)`. Let `rho_p` be the actual stage-1 route for port p. The
later pre-transport query at common owner d is

```
y(d) = sum_p H[:,p] x_p(d rho_p),       H = R/4.
```

The program, complete first scalar endpoint, physical family IDs, schedule,
all 112 route matrices, and the coefficient identity are verified here. Native
interpretation of these two equations uses the inherited common-frame and
constant-endpoint identities described below; it is not established by treating
frame moves as identity.

A permitted repair records `e(g) = E_g x(g)` at each old owner g. The matrices
E_g may differ arbitrarily by owner and may mix all 112 ports at that owner.
Their outputs may then be decoded together with **all** old z fields, using
arbitrary cross-owner linear processing. No other source-dependent state is
available. Observation dimensions are charged by `dim e(g)`. We require every
y(d), not only the final completed supplier endpoint.

**Theorem.** Every such repair has `dim e(g) >= 104` for every g. Equality is
attainable as a linear-information interface.

**Proof.** Fix any g and vary only x(g). Port p contributes to the later
output owner `d_p = g rho_p^-1`. The verifier proves the 112 rho_p are distinct,
so these 112 d_p are distinct. It also proves every column H[:,p] is nonzero.
Consequently the map from x(g) to the complete later field is injective: its
p-th coordinate appears in its own output block, multiplied by a nonzero
column. Its rank is exactly 112. Every old transcript at a different owner is
zero on this input slice, and z(g) has rank exactly eight. Correct decoding
therefore requires the stacked map `[R; E_g]` to be injective. Its rank is at
most `8 + dim e(g)`, proving the lower bound. This kernel argument also allows
nonlinear decoding of the stated *linear* observations.

For attainment, the receipt gives eight pivot columns J for R and the 104
complementary coordinate reads. Observe x_p(g) for p outside J. Subtract their
contribution from z(g) and invert the eight-by-eight pivot minor to recover all
x(g). The displayed route formula then recovers every y(d). This proves only
an abstract recovery map. It grants arbitrary final routing/aggregation and
supplies no native read, storage, restoration, hosting, precision or tape bill.

The proof is a direct-sum information argument, not a new general rank lemma.
The contribution is its source-bound application to the 112 actual distinct
routes, with a sharp repair and exact failure witnesses.

## One output owner: why eight and 112 are also correct

Fix one later owner d. Its inputs come from the 112 distinct owners d rho_p.
On each such owner, the old observation R x leaves coordinate x_p undetermined:
`rank([R; e_p^T])=9` for **every** p. The receipt gives 112 exact rational
vectors w_p with `R w_p=0` and `(w_p)_p=1`.

If extra observations must each concern one old owner, at least one is needed
at every one of those 112 owners. Otherwise w_p at an unobserved owner is an
exact collision with nonzero output H[:,p]. One coordinate tap at each owner
attains 112 evaluations, granting free aggregation. If the extra observations
may already aggregate across owners, exactly eight scalars suffice: the
missing-output quotient has rank `rank(H)=8`. The old observations on these
112 relevant owners have rank 896; appending the demanded eight outputs gives
rank 904. These are two different locality contracts, not inconsistent costs.

Making all route owners identical is a meaningful positive control: then
`y=R x/4` is already known and requires zero extra information. The distinction
between cover-owner routing and payload permutation is essential.

## Source binding and native scope

Base and refreshed canonical main:
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4.
`SOURCES.json` pins the selected archive and record by Git blob and SHA-256;
four unique full-path archive members are authenticated before decoding.
No pending implementation is imported.

The proof's native interpretation inherits these explicit premises:

1. The common-frame conjugation identity transports normalized scalar rows
   through the emitted word. [PR2048](https://github.com/CrocSwap/integer-mult-bounds/pull/2048),
   head `a0e55f357344f1742f72942f94ae2a6f13ff7065`, checks all used children
   and adapters, including phases, and proves this factorization. Its source
   normalization is `C_q^-1`; translation roots C_q fix constant payloads.
2. The complete first local call sends constant D differences to the same
   constants on D and T, and leaves zero helper/private differences. This is
   the inherited endpoint under the same conjugation and endpoint-adapter
   identities, explicitly used and native-tested on a witness by PR2391.
3. The retained native local-view/cover contract reads physical owners
   `d rho_p`. Row charts and entry translations preserve constant initial
   payloads. Local intertwiners, rather than an assumption that intermediate
   states remain constant, justify the local representation. This is the
   cover interpretation in PR2391, not a rebuilt global compiler.

Here both complete **scalar** endpoints are independently replayed. Calls 1-3
use none of the 224 D/T physical families; the first five schedule events are
exactly the local sweeps 0-4. Thus no bridge or idle event is silently omitted.
Every 73-column route is checked for orthogonality, involution, fixed port,
chart swap and both stage-translation formulas. On the constant slice, the
second call sees matching D/T values at each routed port; its eight normalized
queries are precisely the computed H combination. General nonconstant native
operator rank is not inferred from this calculation.

The exact observation-model theorem is unconditional finite linear algebra.
Its application to the native supplier is **conditional on the three inherited
premises above**, which are credited, not independently re-proved here. This
package does not run a native word evaluator, all-column Clifford replay,
complete supplier cold replay, global compiler or Lean. It is not a theorem
about all centre-sharing mechanisms, retimed/mixed-owner observations,
nonlinear encodings, or final-output-only contracts.

## Evidence and replay

```
python3 -I -O -B research/centre-owner-observation-floor/verify.py
python3 -I -O -B research/centre-owner-observation-floor/independent.py
python3 scripts/research_package.py --package research/centre-owner-observation-floor
```

Expected: `PASS_CENTRE_OWNER_OBSERVATION_FLOOR` and
`PASS_INDEPENDENT_CANONICAL_OWNER_FLOOR`.
The primary checker uses exact rational arithmetic on the emitted programs.
The second checker independently reconstructs R/H from canonical A, cut,
precondition and compensation records, never importing the first interpreter.
It directly verifies every rational kernel and uses modular nonzero minors
for independent exact-rank lower certificates, with matching dimension upper
bounds. Every one of the 112 omitted-owner failures has an explicit receipt.
A 103-coordinate repair loses one dimension; the 104-coordinate repair is
invertible. Seven semantic control groups include owner-collapse, redundant
old observations, a valid new observation, and failure away from its owner.
Normal replay is read-only; `--write NEW_PATH` refuses an existing file.

The first working ceiling and lever commands passed. Baseline
`a_cap=0.001690054109089`; ideal two-call sharing is about 1.90x, before repair
costs. This result removes no charge: the baseline retains eight rank-eight
children and centre mass 64 per call. It proposes no changed profile, so no
new `ceiling(centre=...)` value or improved kappa is justified.

## Overlap and credit

Selection nonce `66c64b84eb2cd95a3d22ad91c21c86ed`, card
`centre-path-sharing`, scope key `a55534776f5479f1686c`.
Final live text overlap at 2026-10-15 11:14-11:18 UTC covered 655 open PRs
and 1,185 Discussion records with complete pagination and no freshness warning. The helper excludes
arbitrary diffs and some closed work; it is not a novelty certificate.
The existing PR2048 native lift and PR2199 all-call scalar census were
explicitly avoided. The current work follows PR2391's additional-observation
handoff in Discussion 1884; no advance public claim was posted in this local
preparation phase.

Credit Aaron Wang/navinor (PR2391), Sagar Thakrar (PR2199, exact Clifford
conventions), Adam Gall (PR1918), commdata2338 (PR2048), the common-frame proof
lineage of DreamingOfClouds, and the selected construction/emitter lineage of
Rohan Arun, Jeremy Kothe, Hao Yan and icekylinx. The scalar quarter identity,
source matrix, route formulas and native counterexample are their prior work.
The new result is the sharp locality-dependent repair theorem and its exact
selected-source certificates. Prepared for **ywz65** with substantial **OpenAI
Codex assistance** in scoping, proof, implementation and writing. Apache-2.0.
No independent human or formal-kernel review is claimed.

## Open next questions

- Can one explicitly priced mixed-owner observation realize any of the eight
  aggregate repair fields? First specify its physical input owners, chronological
  cut and endpoint, then test all 112 retained kernel witnesses. The blocker is
  legal access plus a complete storage, restoration, hosting and precision bill;
  the abstract eight-dimensional output does not supply an implementation.
- Can a final-output-only contract identify later query differences that no
  longer matter after overlapping scatters? First compute its exact fixed-dirt
  quotient with every intervening event. The internal-query contract proved here
  does not answer that different question; physical continuation is the blocker.

Validation on Windows / CPython 3.12.14: the full registered replay passed,
including the independent checker and four corruption tests (22.643 s for
the test group). Direct checks also passed on the installed Python 3.14.
This is local author validation, not hosted CI or independent human review.
