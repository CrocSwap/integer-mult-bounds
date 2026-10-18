# Cross-call kernel demotion

**Conditional kappa = 0.001675224519162937.** Conservative endpoint:
**0.001675224516317980**. Frozen comparison is
[PR1148](https://github.com/CrocSwap/integer-mult-bounds/pull/1148) at
`98235a9cf4ce355ec5cf3fac2eca7b3b98a20838`, kappa 0.001675121647789207.
The absolute improvement is 0.000000102871373730, about 0.006141 percent.
The latest public PR bodies were reviewed through PR1153; no later-frontier or
unconditional multiplication claim is made.

From the repository root, with Python 3.10+ and a new output directory:

```sh
python -I -B research/crosscall-kernel-demotion/verify.py --out ../crosscall-result
```

The replay is self-contained and standard-library-only. Three newly reconstructed
providers run sequentially with bounded native Python children, at BelowNormal
priority on Windows. No C++, GPU, WSL, network, optimizer, Lean build or persistent
service is used. Allow approximately a minute for the full replay on a typical
desktop. Programs, charts, receipts and logs are written outside the source tree.

## Two coupled mechanisms

PR1148 supplies the three-demotion, eight-rank-seven-end local word and its actual
T16 table. We add three disjoint demotion islands at groups **627, 635, 651**.
Searching every codimension-one subspace of each five-dimensional start frame
finds legal directions that a last-vector-only rule misses: group 651 works while
retaining the required vector 30. Each concrete joint prefix is recounted and
independently checked; a local algebraic fit alone is not a scalar certificate.

The selected four-helper subframes are:

```text
627: [68,34,24,1]     635: [170,102,30,1]     651: [139,96,25,7]
```

The extra helper indices are `(403,405,406,407)`, `(411,413,414,415)` and
`(427,429,430,431)`. Prefix k widens exactly 4k helpers from four to five and
changes its complete local paid profile by
`k * (-8H1 + 8H2 + 4H3 - 4H4)`.

A same-call allocation hosts 42 extra groups. Cross-call width-four donor
exchanges raise this to **89 groups across 52 calls**. A donor can execute at a
different call only when both literal inactivity windows, active-family
exclusions and per-call uniqueness checks allow the exchange. Swapping the
width-four roles preserves every occurrence and every old family load; widening
the selected target then consumes one actual unit of slack. All subsequent
offsets are rebuilt chronologically. The final map consumes **356 of 360 unit
axes**; no fractional or shared helper is introduced.

Prefixes zero through three occur **92, 30, 7, 15 times**. The complete profile is:

```text
{1:340860, 2:71848, 3:59684, 4:18364, 5:11808,
 8:1152, 24:1, 48:4918}
```

The complete difference is 89 copies of `-12H1+8H2+4H3-4H4`, including the paid
remainders. Rank mass stays 1,041,408, live stock 14,336 and deficit 5,120. There
are 69,120 literal helper roles, 144 complete calls, 1,409 changed owner records,
4,923 paid remainders and 10,271 actual 73-column chart types. The source-bound
literal edits reconstruct the final table from PR1148 exactly.

## Fresh checks and charged work

Each changed local prefix is checked on all 704 arbitrary input columns in both
orientations, including dirty helpers, complete monotone frame histories,
low-end cones, exact native emitted programs and 25 emitted corruption controls.
Every changed Clifford edge and endpoint wrapper is checked including global
phase: prefixes one/two/three have 9/18/27 changed edges, 1/2/3 changed wrappers,
and 10/20/30 phase controls.

The independent owner audit reconstructs source events and inactivity windows,
checks all actual pending axes, literal per-call inventories, family identities,
disjoint chronological blocks, source/phase geometry and full orthogonal charts.
It recounts every paid residual and performs 13 role/geometry/dispatch controls.
The full profile is priced by two exact rational moment engines, with native and
conservative brackets and all 47 strict outer inequalities. The retained bit
profile's complete mass and exceptional-residue arithmetic are repriced; its full
circuit is not cold-replayed.

The fresh invoice reads the actual changed programs. The local child count is
3,498, adapters 387,120, and local primitive bound 10,039,700,351,134. It adds the
entire fresh per-vertex bill **3,589,198,021,555,152** to the pinned prior allowance
**2,877,946,989,724,568**, giving **6,467,145,011,279,720**. All nine finite guards
and four invoice controls pass. Actual prefix 397 fits the charged 512-bit
reserve; physical row 16,469 fits the retained 20,161 limit. Chart cost is bounded
per occurrence; a lower distinct-chart count is not treated as free work.

## Two distinct OpenAI proof structures for each worker

Sources were inspected in the registered [OpenAI math](https://github.com/openai/math)
collection. These are sourced mathematical adaptations, not newly compiled Lean
imports, eight independent exponent gains, or priority claims for those sources.

| Worker | Two structures used | Evidence |
|---|---|---|
| Local words | Split-flag coordinate projections; postselection transporter bijections | `notes/cells/OPENAI-MECHANISMS.md`, `OPENAI-SOURCE-LEDGER.json` |
| Owners | Matching augmentation that preserves covered roles; explicit disjoint physical pool templates | `notes/owners/OWNERS-PROOF.md`, `OPENAI-SOURCE-LEDGER.json` |
| Controller | Direct-sum tensor restriction; joint-signature histogram/orbit lifting | `notes/recurrence/SUFFICIENT-TRANSPORT.md`, `OPENAI-SOURCES.json` |
| Root | Exact positive capacity scans; semantics and additive cost under program relabelling/composition | `notes/lead/OPENAI-MECHANISMS.md`, `OPENAI-SOURCES.json` |

The notes preserve the sufficient proofs, exact source hashes, checked scopes,
hyperplane census, same-call fallback and bounded final augmentation search.
The naive PR1148/T37 composition priced worse and was stopped before a large
replay. PR1129/1131/1152 inform that alternative; none of their gains is added.
Failure of a restricted last-four-gap search is not a global optimality theorem.

## Conditional scope and provenance

Fresh checks establish this changed finite construction. Unchanged PR1148 scalar
admission/phase edges, compiler/all-size interfaces, common-label and mutable
source realization, complete-call hosting, precision/tape and exact recovery,
analytic transfer and inherited bit H1-H5 remain explicit assumptions. This is
not an unconditional multiplication theorem, new Lean certificate, hosted CI
result, independent human review or global packing optimum.

`MANIFEST.json` binds every other file by SHA-256 and exact file inventory before
replay. `vendor/pr1148/SOURCE-PINS.json` binds ancestor inputs. Preserve raw bytes
and disable automatic line-ending conversion when cloning; fresh gzip headers
may differ across Python versions, so generated byte bindings and mathematical
equality are checked together.

The candidate `data/PLAN.json` contains only the geometry fields used and checked
by this verifier. The unchanged full upstream plan is retained separately in
`vendor/pr1148/PLAN.json.gz`. Actual per-call widths and profiles come exclusively
from `data/DISPATCH.json` and the freshly reconstructed native providers; old
registry metadata is not retagged as a certificate of the new mixed controller.

Direct credits include PR1148, PR1111, PR1117 and our preceding adaptive-prefix
method; PR1018/987, PR1030, PR1005/1004, PR1022/858/870/1074, PR942, PR864,
PR635 and retained ancestry; PR589 supplies the unchanged bit contract.
PR1129/1131/1152 supplied the new T37 comparison. The Apache-2.0 license and
original source notices are preserved. See `NOTICE.md`, `UPSTREAM-NOTICE.md`,
`vendor/pr1148/NOTICE.md` and `local/UPSTREAM-NOTICE.md`. New work was prepared
with OpenAI Codex assistance; no submitting-user name or email is added.
