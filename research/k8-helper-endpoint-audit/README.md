# Selected k8 helper endpoints: fixed-schedule rigidity and rank camouflage

**Scoped adversarial audit; no new κ and no selected acceptance bug.** All
480 helper final frames of the selected PR1094 k8 word are minimal under its
unchanged gates, entrances, gate frames and early/full cleanup schedule.
Consequently no helper end can be replaced by a smaller subspace, and an
equal-dimensional replacement must be the original subspace. This also holds
for simultaneous endpoint-only replacements. Changing the schedule or gate
frames can escape the statement.

The added evidence is a complete endpoint-forcing certificate and 78 concrete
same-rank adversaries. It makes explicit why a correct scalar map and a valid
rank-only owner allocation cannot replace local frame admission. The existing
local audit already enforces that admission; this package corroborates it.

## Reproduce and evidence

From the repository root, Python 3.12+ and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/k8-helper-endpoint-audit
# Direct read-only replay, including all 78 retained local rejection runs:
python3 -I -O -B research/k8-helper-endpoint-audit/verify.py
```

Expected status: `PASS_K8_HELPER_ENDPOINT_BOUNDARY_AUDIT`. Normal verification
compares its deterministic result to [RESULT.json](RESULT.json), writes only
temporary files, and runs six additional small-domain/tampering tests through
the registered command. `--write PATH` explicitly regenerates the receipt.

| Check | Evidence |
|---|---|
| Restricted endpoints | 32 rank-four and 46 rank-eight ends; every last native frame equals the committed end |
| Other endpoints | All 402 helpers occur in an ordinary full-frame cleanup gate |
| Positive local replay | Retained exact rational audit: all 704 columns, both orientations, frames, entrances and cones |
| Positive owner replay | Retained PR1091 auditor: all 69,120 roles, 144 calls and 288 windows; profile agrees with current PR1094 SPEC/PLAN/PROFILE |
| Endpoint adversaries | One per restricted helper, 78 actual retained local rejection runs; each passes both scalar endpoint tests first |
| Owner diagnostic | Every adversary has the identical ordered vector of 480 residual widths; all other owner-auditor inputs are unchanged |
| Counted exclusion | 105,927,652 alternative single-end same-rank caps containing their original entrances; excluded by span inclusion, not enumerated |

Only **one** complete owner replay is executed. The owner auditor is a function
of geometry, widths, profile, roles and plan, so unchanged inputs give the same
result for every adversary. We do not claim 78 separate global or owner replays.
The retained local and owner implementations are explicitly reused comparison
targets. The new span certificate and explicit-set checks do not import a
supplier builder or the retained auditors' span functions.

## Exact boundary and proof

Let `E_q` be a helper's entrance label subspace and `F_q` its committed final
subspace, inside `F₂⁹`. These binary spaces describe **labels**; the retained
scalar endpoint tests use exact rational coefficients.

For a helper absent from ordinary full cleanup, propagate its frames through
the literal A/B and early-cleanup chain. Every allowed final cap `G_q` must
contain the last frame `L_q`, by monotonicity. The receipt supplies the last
gate and exact basis witnessing `L_q = F_q` for all 78 restricted helpers.
For each of the other 402 helpers it supplies an ordinary cleanup gate index.
The inherited local contract requires every register in such a gate to have
a full final frame, so its cap is forced to `F₂⁹`.

Thus every admissible `G_q` contains `F_q`. Smaller dimension is impossible;
equal dimension implies equality. The argument is coordinatewise, so changing
several endpoints together cannot evade it while the schedule and gate frames
remain fixed. This is a statement about endpoint subspaces, **not** a global
moment optimum, an arbitrary frame reassignment bound or a cleanup-resynthesis
lower bound. Enlarging endpoints is not excluded or priced here.

For an end of dimension `d` containing a fixed entrance of dimension `s`, the
number of dimension-`d` caps containing the entrance is the binary Gaussian
coefficient `[9-s choose d-s]₂`. Exactly one equals `F_q`; the others fail the
necessary inclusion above. The restricted ends comprise 32 `(s,d)=(0,4)`,
16 `(0,8)` and 30 `(1,8)`, giving

```text
32 * (3309747 - 1) + 16 * (511 - 1) + 30 * (255 - 1)
= 105927652 alternative single-end caps.
```

The six tests independently enumerate all subspaces up to ambient dimension
four as point sets, check the Gaussian and quotient counts, compare elimination
with explicit XOR closure, exercise invalid labels and frame witnesses, and
reject a corrupted source input. No floating-point acceptance is used.

## A minimal same-rank adversary

Register **273** is a cold helper with final basis `[388,96,24,2]`. Replace
only that final basis by `[388,96,24,1]`. Both spaces have dimension four,
the entrance remains zero, and every scalar instruction and claimed width is
unchanged. Its last early-cleanup gate, original cleanup index **40**, requires
label `2`, which the replacement does not contain. Both exact scalar maps pass;
the retained local audit then rejects `frame not monotone (273, ...)`.

Each of the other 77 fixtures similarly replaces one complementary basis
direction by a direction outside the old end, while preserving its entrance.
The receipt names a missing required label and the observed rejection site.
These are invalid **frame contracts**, not counterexamples to the scalar
identity or the selected construction.

## Source binding, enforcement and scope

Base: `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`. Selected PR1094 audited
head: `0fc329d0bec93ca7cd288eaea1295172e8789810`. [SOURCES.json](SOURCES.json)
pins each consumed input by Git blob and SHA256, with the selected record and
task catalogue retained as historical provenance. The PR1091 diagnostic word
copy has decompressed hash
`c2b294300760e1fd6eeab8c22c4d13e4633dca40e52cac8da0d68163a76e3ca8`,
which is checked against the selected-source-bound k8 recipe's output pin.

The retained source shows two separate defenses. `verify_slots.py` binds the
rebuilt word to its content hash and explicitly executes `independent/audit_local.py`;
the latter checks monotonic final climbs before computing width inventories.
`scripts/verify_frontier1042.py` runs that slot layer; PR1094 inherits the checked
local word. By contrast PR1091's `word_widths()` only subtracts endpoint and
entrance ranks, as appropriate for an owner audit that assumes local admission.
Our mutated raw words deliberately enter **below** the immutable word binding.
They are rejected locally and do not match the frozen recipe payload.

This package does not rerun the selected cold replay, native compiler, phase
recipes, precision/tape proof, bit H1–H5, outer moment/assembly or analytic
transfer. It establishes no all-size theorem or physical supplier admission.
Source pins and the selected construction are unchanged. [TASK.json](TASK.json)
records the assignment, bounded domain and overlap check; coordination is in
[Discussion #1378](https://github.com/CrocSwap/integer-mult-bounds/discussions/1378).

## Open next questions

Can a changed tail schedule permit a smaller endpoint for one current rank-eight
helper after paying every partner's frame change and restoration? This matters
because endpoint-only reductions are excluded here, while PR1030/PR1090 show
that changed gate frames and tails can achieve rank-seven ends. First inspect
one receipt's forcing gate and propagate a proposed lower frame backward
through all its operands. The blocker is constructing and pricing the complete
new local word and hosting it, not obtaining another unchanged-width owner run.
The structured question is in [TASK.json](TASK.json); no search for this next
question was conducted.

## Credit and overlap

Rohan Arun's PR1094 supplies the selected owner map; Jeremy Kothe's leaver/k8
lineage and the retained gauge44 contributors supply the word and local audit.
Josie Elliston's PR1091 (`b4c13a228acb80f74c682b7097f0ce9bbf51bc4e`) supplies
the owner-audit comparison and word copy; Sagar Thakrar's PR1049
(`6d0a145e8b4774b1b0d4e3da56890af5adc9b04f`) already independently audits the
word's scalar/frame semantics. Douglas Colkitt's batch1099 composition applies
the owner auditor to PR1094. This package claims no priority for monotone frame
inclusion, Gaussian subspace counting or their existing admission checks.

PR1358 fixes endpoints and studies singleton B-gate enlargements; PR1312 studies
X2 cross-child owner-axis collisions; PR1238 studies the source/target end-cap
wall. PR892 (`9778ba2d891468996b81eb50c389bb4169df0025`) already proves a
rank-eight endpoint floor for a different historical coded helper using its
inverse row, with a broader changed-cleanup argument. This package instead
supplies the selected word's fixed-schedule **helper** endpoint
census and paired scalar/rank-blind versus frame-sensitive fixtures. Live
overlap was checked across open PR bodies (including drafts), discussions,
local notes and the ledger; this is not an exhaustive search of every code diff.

Prepared for Arham Tahir with substantial OpenAI Codex assistance in code,
investigation and writing. No independent human peer review is claimed.
New work is Apache-2.0; predecessor files and notices are retained unchanged.
