# Observer Limits and Physical Costs in Native Constructions

This report offers tools and scoped findings for researchers trying to improve
the integer-multiplication exponent saving κ. Its main contributions are ways
to screen proposed reuse mechanisms, identify what a repair must change, and
connect a local operator improvement to the full cost budget. No new κ is
established.

The work extends the recovered `filtered_native` packet. It combines exact
phase-aware history analysis, an observer quotient with rational certificates,
literal program-to-invoice checks, exploratory feedback searches, and a
conditional arithmetic budget. The practical value is to make subsequent
construction attempts more selective and easier to verify.

The repository baseline at the pinned research snapshot was the conditional
κ = 0.00302015 construction in [PR4470](https://github.com/CrocSwap/integer-mult-bounds/pull/4470).
The findings are author-checked scoped research prepared for public review;
they do not update the selected frontier. Sources are pinned to canonical `origin/main`
`7c472563474e60185e6ca101a17622133d047e56`, dated 2026-10-23.

At submission refresh, canonical main
`1ec1119972c9aefe42525172d07b332fcff81cb4` selects the conditional
[PR4610](https://github.com/CrocSwap/integer-mult-bounds/pull/4610) construction,
independently audited in [PR5241](https://github.com/CrocSwap/integer-mult-bounds/pull/5241).
The earlier baseline above is retained as research provenance. The two arithmetic
dependencies used here are unchanged at that refresh. These results concern the
pinned source words and do not establish a new exponent for the newer selection.

## Findings researchers can use

| Finding | Evidence | How it can guide another construction |
|---|---|---|
| Cheaper native execution changes the endpoint | Deleting eight H8 centers exposes a defect controlled by eight R modes | Carry the changed operator and its repair cost into the caller; the old target inventory cannot be credited automatically |
| Unchanged-history snapshots lack a needed dense coefficient | All 2,965 distinct source-X physical terms have Clifford grade at most 8; the following thin query needs grade 9 at all 112 ports | Run a phase-aware support census before investing in a passive cache construction |
| Simple end-only observers do not give a cheap repair in the tested families | Individually clean gathers cost lift rank mass 72 versus deleted mass 64; 204,291 two-frame pairs of total lift rank at most 8 are excluded exactly in the necessary quotient | Investigate earlier observer injection, more frames, or changed contacts; the excluded families can be screened out of future searches |
| Gauge replay can agree while its cost inventory remains unbound | The pinned [PR5270](https://github.com/CrocSwap/integer-mult-bounds/pull/5270) literal reuses nine axes while its invoice credits fresh-stage targets through rank 153 | Bind every target and paid job to literal coordinates and chronology, in addition to checking operator equivalence |
| Joint arithmetic can be evaluated before a full physical implementation | Exact interval and independent integer-root checks quantify the value of hypothetical center replacements | Use the budget to compare candidate repairs, then require endpoints, phases, helpers, ordinary work, and both complex/BIT branches before admitting an increased κ |

These findings have different strengths. The support argument concerns a fixed
whole-field macro grammar. The observer exclusions concern specified finite
families in a necessary quotient. The MILP and active-feedback runs are search
results. None gives a universal barrier to increasing κ.

## A cheaper native word comes with a repair problem

The recovered packet builds on the center-free coded-producer direction in
[PR4929](https://github.com/CrocSwap/integer-mult-bounds/pull/4929). It uses

`P = RᵀR/56`, `A = I − 14P`, `C_F = A + (I−A)F`.

Deleting eight H8 centers reduces the paid inventory, but changes the native
endpoint. The defect factors through the eight R modes. This gives a concrete
repair target: recover or otherwise handle those modes while preserving the
arbitrary original inputs and independent helper outputs.

For another researcher, the useful interface is the changed operator together
with its complete input/output contract. A proposed observer, inverse code, or
caller should be checked against that interface before its rank savings are
included in an exponent calculation. A repair may consume the entire apparent
saving.

The predecessor's paired inverse codes, causal companion, even-head resolvent,
and encoded-mode controls remain verified components worth reusing. They do
not discharge the missing odd-Q ordinary-caller obligation. Algebraic inverses
and physical implementations must be connected through the actual phase and
frame conventions.

## Screen passive reuse with physical support

`history_grade_probe.py` replays all 632 independent original amplitudes,
including 408 independent helpers, using the actual phase-sensitive K_G
operators and conjugate raw-dual canonical frames. It checks the original
endpoints and owned-zero return, and observes 21,480 row snapshots.

Among 2,965 distinct source-X physical terms, every Clifford grade is at most
8. A snapshot has at most 24 source-X terms in total. By contrast, the X
coefficient needed for the following thin query has grade 9 at each of the
112 ports.

For column width f, a grade-r Clifford coefficient has at most `2^(rf)` nonzero
entries per row. Monomial recoding preserves row support. A sum of M recoded
snapshots therefore has row support at most `24M·2^(8f)` in a fixed X input
column, whereas the required coefficient has exactly `2^(9f)` nonzeros per
row. Equality requires `24M ≥ 2^f`.

If an expression is built from snapshot inputs using L whole-field binary
additions, it has at most `2^L` leaves, giving `L ≥ f − log₂24`. A fixed finite
number of these operations cannot supply the following thin query at every
width.

**Research implication.** For this unchanged history, passive whole-field
linear combinations and monomial recodings cannot provide that query using a
constant number of whole-field operations. A candidate must change an assumption
of this argument, for example by using a new paid provider, a changed native word, or
a different operation grammar. The argument does not bound arbitrary coordinate
algorithms or multiplication. It also does not exclude every form of cache
reuse.

The reusable technique is a **physical grade census followed by a support
comparison**. A census based only on the binary incidence matrix G would not
justify this conclusion; the K_G phase and raw-dual frame conventions matter.
The implementation can serve as a template for screening a different history,
with its own endpoint checks and coefficient census.

A separate bounded alignment screen, `snapshot_probe.py`, considers 424
rank-eight snapshot arrivals and native-word recodings. Each port has three
independent eligible candidates; none recovers the target at any of the 112
ports. Native-Y exit positive controls pass. This exact result is limited to
that recoding family and does not exclude additional group relations or more
general ordinary recodings.

## Use observer quotients to test repair ideas cheaply

The changed, center-free backward word can first be examined in the necessary
specialization `K_G |0⟩ = |0⟩`. The observer probe keeps all 632 original
amplitudes and the 408 independent helpers, checks the changed endpoint in
this specialization, and grants full-frame snapshots as free side information.
That side-information span has rank 482; eight R-mode directions remain missing.

This relaxation supports inexpensive tests before attempting a full physical
operator identity. Its exact subspaces are exported in
`evidence/observer-subspaces.json.gz` for other searches. A quotient-level
candidate still needs phase-aware physical recovery, chronological access,
helper preservation, and a complete invoice.

### Individually clean observations

`observer_probe.py` examines 1,001 non-full contact frames. At ranks 1–8, no
same-frame scalar gather individually supplies a pure missing-mode combination
modulo the free side information. Ground-frame gathers recover all eight modes,
but their full lifts cost rank mass `8·9 = 72`, exceeding the removed mass 64.

This exact optimum applies to the individually clean lift family. It does not
settle jointly decoded noisy observations. Its practical use is to prevent
repeating a clean-observer search over the same contacts without changing the
model.

### Two noisy observations, with exact certificates

`exact_pair_check.py --maximum-cost 8` examines 204,291 pairs from 871 contact
frames, allowing arbitrary same-frame gathers and a summed full-lift rank at
most eight. None yields a missing-mode direction in the necessary quotient.

For 202,749 pairs, a full-rank minor over F65537 proves that the nuisance
projection is injective over Q. The remaining 1,542 pairs are checked by exact
rational elimination. A deliberately planted joint-noise cancellation passes
the positive control. The earlier budget-four calculation is retained too.

**Research implication.** Two-frame repairs within this cost budget are
excluded in this family. Researchers can turn to other timings, three or more
frames, larger budgets, or changed sources without treating those possibilities
as already ruled out. The modular-minor shortcut plus rational fallback is also
a reusable way to turn a fast modular screen into an exact finite certificate.
A negative modular search alone would not provide that certificate.

### Wider joint searches remain exploratory

`observer_milp.py` searches 986 frame selectors and 2,312 continuous row
coefficients. With coefficient bound 32 and total lift rank budget eight,
HiGHS reports infeasible for each of the eight target modes. A budget-nine
positive control reconstructs over Q.

This is bounded numerical search evidence. It can help choose follow-up
experiments, but it is not an unrestricted rational infeasibility proof and
does not extend the exact two-frame exclusion to arbitrary collections of
frames. The retained solver inputs and subspaces make that boundary explicit.

## Bind literal programs to the claimed rank inventory

`repeated_head_probe.py` provides a concrete review example at
[PR5270](https://github.com/CrocSwap/integer-mult-bounds/pull/5270), pinned head
`df9e5037587ce0cfbd23c2a944515526b301e820`. Its two source files are retained
byte-for-byte in `inputs/`. The probe traces the actual listing and dispatch
with empty payloads.

Every LETTER and IDLE uses the same `range(9)`, while the invoice credits fresh
eight-axis stage blocks and a maximum target rank of 153. The p19 middle IDLEs
execute 4,032 rank-nine field jobs, whereas their thinned invoice contribution
is zero. Equality to a reference using the same reused head demonstrates gauge
equivalence; it does not establish those target ranks or paid-job omissions.

There is a separate adaptation cost: turning native D into R = DQ by the
direct two-bank post-Q recipe costs 4,256 H1 jobs at p19. Even a relaxation
that grants H9 main targets and discards every idle charge has rank-mass surplus
−2,240 after that direct upgrade. This applies to that explicit recipe, not
every possible redesigned caller.

**Research implication.** A supplier certificate should connect its literal
coordinate maps, its target operators, and every charged operation. Agreement
between two programs sharing the same coordinate reuse does not establish an
independent-stage invoice. This check is useful for other controller proposals,
including ones with different pair counts or stronger headline savings.

## Explore feedback while retaining its physical obligations

The active-feedback experiments allow selected-mode controls on six original
banks plus one or two owned scratch banks. They test 128 width-two sectors with
seven independent stage signs and one filtered stage. Three starts with one
scratch bank and three with two banks plus internal selected feedback found no
numerical hit.

These runs do not exclude feedback repair. Their reusable contribution is a
small discovery model and recorded controls/residuals for a mechanism that is
broader than passive observation. A promising continuation would change the
physical contacts or observer timing, reconstruct any numerical hit over Q,
and then replay every arbitrary input column with the actual phases. Owned
restoration and ordinary work remain part of the cost contract.

Relevant primary literature suggests directions without supplying that
compilation automatically:

- [Vinciguerra, *An Operator Approach to Register Programs for Catalytic Computing* (2026)](https://arxiv.org/abs/2609.18692)
  treats closed operator loops and restoration, motivating actively written
  owned-bank feedback. Its register operations still need a compilation into
  the repository's Gaussian ABI and cost model.
- [Alekseev, Filmus, Mertz, Smal and Vinciguerra, *Catalytic Computing and Register Programs Beyond Log-Depth* (MFCS 2025)](https://drops.dagstuhl.de/storage/00lipics/lipics-vol345-mfcs2025/html/LIPIcs.MFCS.2025.6/LIPIcs.MFCS.2025.6.html)
  provides a restoration/register-program perspective relevant to that search.
- [Alman and Li, *Kronecker Powers, Orthogonal Vectors, and the Asymptotic Spectrum* (2025)](https://arxiv.org/abs/2509.14489)
  is relevant to spectrum and depth-two rebalancing obstructions. Such results
  do not settle this changed operator endpoint or its tape model.

## Translate a local saving into a joint κ budget

For a proposed saving κ, the raw inventory test compares

`M(κ) = Σ_r T_r r^(1−κ) − Σ_r P_r r^(1−κ)`.

This is a useful first arithmetic screen once the target inventory T and paid
inventory P are justified. If a fixed caller has sixteen backward invocations,
replacing s rank-b centers per backward call by one H1 each increases this raw
margin by `16s·(b^(1−κ) − 1)`, provided every endpoint and helper target is
preserved. A changed endpoint requires a new inventory or a separately charged
repair before this formula can be used.

`acceptance_budget.py` connects a hypothetical local replacement to higher
moments, both charged tails, a logarithmic compiler, an ordinary BIT cover,
and 54 strict plus four functional outer checks. `independent_budget_check.py`
uses integer roots to check the raw margins independently of the retained
logarithm/exponential engine. The retained scripts implement one fixed
conditional invoice; they are reference implementations to adapt for another
candidate, not a general parameter-search interface. Their evidence records
retain the numerical parameters and unfulfilled implementation obligations.

**Research implication.** Compare repair ideas using their full marginal cost,
then track which of the complex and BIT branches limits the joint bound. A
complex improvement may leave the joint κ unchanged when the BIT branch is
insufficient. Favorable moments alone do not establish a new supplier: the
physical-word, arbitrary-input, phase/all-width, helper, ordinary-work, and
precision/tape obligations remain separate.

## Related PRs and where these findings fit

| PR | Relevant contribution | Connection to this report |
|---|---|---|
| [PR4929](https://github.com/CrocSwap/integer-mult-bounds/pull/4929) | Center-free native producer with an explicit rank-eight port code | Supplies the changed-endpoint setting; deleting centers leaves a mode-recovery obligation |
| [PR4933](https://github.com/CrocSwap/integer-mult-bounds/pull/4933) | Phase-correct normalizers and a coded p16 caller | Provides physical conventions for distinguishing scalar owner mixing from the actual port code |
| [PR4940](https://github.com/CrocSwap/integer-mult-bounds/pull/4940) | Coded reverse stages and inverse-code query shears | A caller direction whose scalar-to-physical substitution needs explicit checking |
| [PR5036](https://github.com/CrocSwap/integer-mult-bounds/pull/5036) | First physical substitution gap for the coded reverse controller | Shows why a scalar inverse recipe cannot be assumed to realize the physical thin source |
| [PR5270](https://github.com/CrocSwap/integer-mult-bounds/pull/5270) | Materialized p19 coded-reverse word | The pinned literal-to-invoice case study above; the findings concern the inspected head |
| [PR5283](https://github.com/CrocSwap/integer-mult-bounds/pull/5283) | Gaussian cache reuse for cross-frame ADDs and paid history | Related cache work; this report's support argument specifically concerns the following thin query |
| [PR4760](https://github.com/CrocSwap/integer-mult-bounds/pull/4760) | Compact partial helpers for an ordinary BIT supplier | A complementary branch improvement to consider when evaluating the joint budget |

The BIT minimum-completion experiment in
`research/kappa-rebuild/bit/pr589_minimum_completion.py` also examines the native
primitive from [PR589](https://github.com/CrocSwap/integer-mult-bounds/pull/589).
Its local mass saving is lost to its direct global-Q repairs, illustrating why
adaptation costs must accompany a proposed local gain.

These links identify relevant contributions and review questions. Their
publication or archival integration does not itself admit a new supplier.
The source pins and scope of each result still govern its use. In particular,
the following-thin-query exclusion here should not be transferred to every
cache task studied in [PR5283](https://github.com/CrocSwap/integer-mult-bounds/pull/5283).
The related [retained-snapshot investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/5355)
reports finite clean-word cache screens. This package adds the phase-aware
following-query support argument and changed-source observer quotient; it does
not claim those earlier cache screens as new findings.

## Open next questions

1. **Can an observer be injected before later paid jobs?** The end-only families
   above leave this route open. First attach a selected observer before a later
   climb and replay all 632 arbitrary columns with actual K_G phases. Progress
   requires a chronological repair word and its complete paid/ordinary inventory.
2. **Which BIT changes would complement a proposed complex gain?** First build
   the analogous changed-source DAG and lower-frame observability data for BIT,
   then evaluate both branches against the candidate joint saving. Progress
   requires an endpoint-preserving BIT program and a charged account of global
   Q adaptation; local mass savings alone have already proved misleading.
3. **Can a broader observer or feedback grammar recover the missing modes?**
   First test changed contacts, earlier timing, or more than two contact frames
   in the exported quotient. A surviving candidate needs rational reconstruction,
   full phase-aware replay, ownership restoration, and an ordinary-work budget.
   The numerical no-hit runs do not resolve this question.
4. **Can a coded-reverse caller use genuinely fresh stage coordinates?** First
   list the coordinate map for every LETTER and IDLE and price D-to-R adaptation.
   Progress requires a physical fresh-stage word and a target/paid recount;
   a same-head gauge comparison does not discharge those obligations.

## Sources and reproduction

The original recovered archive is retained unchanged:

`integer_mult_filtered_native_implementation_2026-10-23.tar.gz`

SHA-256 `595f988e748b1f3b25e7525a226da173966e4278a70f511b2919245cec1b45f7`.
Its 359 source-manifest entries and fourteen focused checks passed. The replay
transcript is `evidence/predecessor-replay.log`. Exact sources, environments,
commands, and limitations are recorded in `SOURCES.json`; the evidence index is
`RESULTS.json`. The selected baseline and its review were resolved through
`certificates/selected-result.json` at the pinned snapshot.

Python 3.11 with NumPy 1.26.4 and SciPy 1.15.3 was used. Core continuation checks
use the standard library; predecessor replay and optional MILP require the
listed numerical dependencies. Optional feedback optimization used PyTorch
`2.8.0.dev20250501` and is time-limited and non-deterministic.

The unchanged predecessor archive is included at
`inputs/original-packet.tar.gz`, with its original license and notices inside.
This archive-based package can be replayed from a clean checkout without local
download files. From the repository root:

```sh
python3 -B research/filtered-native-kappa004/verify_continuation.py
```

From the standalone export, which includes the original archive, the unchanged
arithmetic dependencies, and the license:

```sh
python3 -B research/filtered-native-kappa004/verify_continuation.py --replay-predecessor
```

An explicit `--archive /absolute/path/to/archive.tar.gz` can select another copy
of the same pinned predecessor bytes. The verifier authenticates source bytes,
extracts into temporary directories,
and compares recomputed scientific outputs with the saved evidence, ignoring
elapsed times. `--with-milp` additionally reruns the bounded solver screens and
their positive control. The optimization searches are excluded from default
verification. No Lean, Docker, full repository suite, or theorem-level proof
replay was run. Existing technical paths retain their original names so the
recorded replay commands remain usable.

The HTML report is generated from this README and `report.css`. Regenerate it
with `python3 -B research/filtered-native-kappa004/render_report.py`; the
document-only dependency is `markdown-it-py==3.0.0`.

## Credit and scope

The recovered filtered-native packet and its pinned upstream sources retain
all attribution and notices. The interval/compiler source credits zxv and
substantial OpenAI Codex assistance; mixed-target flow credits Jacob Alan
Sussman's Theorem 1G; the retained outer/native/compiler/cover authors keep
their credit. [PR5270](https://github.com/CrocSwap/integer-mult-bounds/pull/5270) source files retain their original notices unchanged.
New continuation code and this report were prepared with substantial OpenAI
Codex assistance under Apache-2.0. The report supplies reusable research findings
and explicitly scoped evidence, with no claim of a new multiplication theorem
or scientific approval of an external draft.
