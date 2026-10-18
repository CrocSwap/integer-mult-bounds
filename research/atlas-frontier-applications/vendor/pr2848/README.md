# T248: coalesce two cold-start residues

Two interleaved copies of Marius-Paul Dumitrean's PR2843 T124 allocation admit a
single helper move that changes the complete paid profile by

\[
H_2+H_{16}-2H_9<0.
\]

For the common power cost \(H_r\propto r^{1-a}\), strict concavity proves the
inequality for every \(0<a<1\). Both old idle ranks are nine; the new idle ranks
are two and sixteen. No local operation or helper width changes. This is an
actual allocation change, not a more precise root calculation.

The exact target is
`0.001718658508304930004819 - 10^-46 - 10^-70`, a gain of exactly
`2.30463210106193e-10` over PR2843's full modern outer headline. The independently
implemented arithmetic check places the complex root strictly in
`(0.0017186585083049300048199, 0.0017186585083049300048200)`.
The release uses the conservative 24-decimal lower endpoint above.
**Complete clean release passed:** `PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE`
and `PASS_RELEASE`; see [CLAIM.json](CLAIM.json) and `evidence/full/`.

This is a conditional finite construction. The selected result is unchanged.
The exact comparator is PR2843's `CLAIM.json`, not PR2833's supplier-only claim
and not a rounded decimal. Pending predecessors remain pending; this package
makes no maintainer-adoption claim.

## The independently reviewable change

Interleave corresponding calls from two disjoint T124 copies and offset every
second-copy replica/owner by 124. After this deterministic duplication, change
exactly two rows:

| Role | Old owner / offset | New owner / offset |
|---|---|---|
| time 0, helper 224, child 0, port 0 | 0 / 0 | 124 / 0 |
| time 1, helper 224, child 0, port 0 | 124 / 0 | 124 / 7 |

Here helper 224 means index 224 in the fill's provider-width array.
Both roles have width seven. They fit in the second copy's rank-16 bin, which
leaves rank two; the first bin becomes an idle rank sixteen. The new family is
absent from every other role at time zero. Literal pending windows, compact
prefixes and family uniqueness are checked over all **910,656 roles**, **2,232
calls** and **248 replicas**, including every source stage and bridge.
`generate.py` reconstructs the entire fill from immutable PR2843 inputs;
`verify.py` compares decompressed payloads, independently replays the PR2833
words and checks five deliberately invalid allocations. [PROOF.md](PROOF.md)
gives the local argument and its scope.

The complete profile is:
`{1:5374656, 2:1450801, 3:615586, 4:285696, 5:90024, 8:17856, 16:1, 48:89230}`.
Its rank mass is 16,141,824; live stock is 222,208 and physical stock is 222,698.
Every local call, bridge, helper, centre, buffer and remaining idle child is paid.

## Complete budget and evidence

The precision consumer is Dugongue's PR2839 tensor-block contract, freshly bound
to Jeremy Kothe's actual PR2833 words. It checks all 632 arbitrary input columns,
zero helper-to-data response, 72 cleared private buffers and eight cleared
centres. The measured local prefix is 70. The admitted T248 geometry has global
prefix 1453, conservative reserve 1511 below payload 2048, full-stock bound 2646
bits, L2 stock bound 1323 bits, and row 19549 below the cap 20161.
No unknown restoration or consumer charge is assigned zero.

`check_release_evidence.py` authenticates the retained release, cache archive,
exact claim layers and published input identities; it does not rerun that proof.
The finite checker and two new independently implemented auditors are separate:
`independent_owners.py` expands source events without importing the producer or
inherited owner engine; `independent_moment.py` derives the baseline and candidate
profiles and uses 100-term atanh / 18-term exponential rational bounds. Both
retain their checks under `python -O`. The AST derivation check authenticates the immutable PR2839 admission driver
and permits only the declared source/comparison records, defaults and docstring;
all other executable logic is identical, and seven semantic mutants reject.
The inherited frame engine requires
assertions enabled and its wrapper explicitly rejects optimized execution.

Four native chains (both current and both retained providers) and all 16 retained
parent-admission stages passed freshly. The clean release passes 119 admission,
12 BIT, 25 controller, eight independent-owner and six geometry rejection cases;
the modern outer layer checks 63 strict inequalities, 17 rejection cases and
19 exact replays. The inherited supplier summary says controller=15; the actual
25-entry control array is authoritative, as bound in `evidence/full/ACTUAL-CONTROLS.json`.
Complete candidate admission explicitly
reuses that source-authenticated cache. The executed original native preparer
is preserved byte-for-byte; the portable version adds environment recording and
an early cache-directory rejection. These are distinct executable identities.
The generic block-energy proof is inherited from PR2839; **no fresh Lean kernel
audit** is claimed. Finite replay does not discharge all-size compiler,
source-access, whole-call hosting, precision/tape, exact recovery, ordinary
recursion, BIT or analytic-transfer assumptions.

One early exploratory import generated bytecode in a frozen source directory.
Quarantine preserved it outside the source, but left an empty `__pycache__`
directory. The release guard correctly rejected the first T248 attempt because
`copytree` retained that empty directory, although file hashes still matched.
The failed attempt is preserved separately. Only the empty untracked directory
was then removed; all 541 immutable source hashes and the cache-path absence
were checked before a fresh full attempt. No scientific predicate was relaxed.

The retained local-word envelope, run on the actual paid profile
`{1:2382,2:650,3:266,4:128,5:26,8:8}`, gives a complex-saving ceiling below
`0.001758437153251`; the candidate realizes about **97.73784%** of that cap.
`check_ceiling.py` reproduces it. The historical `a/(1+a)` conversion is not
applied to the newer outer recipe. PR2843 also reports the tighter fixed-bin
continuous cap `0.001718659522042026471847`; this contribution does not re-prove
that LP certificate or claim its integer attainability.

## Reproduce

The finite checks use only Python's standard library:

```sh
python3 -I -B research/t248-dirtentry-residue/verify.py
python3 -I -B research/t248-dirtentry-residue/independent_owners.py
python3 -I -B research/t248-dirtentry-residue/independent_moment.py
python3 -I -B research/t248-dirtentry-residue/check_ceiling.py
python3 -I -B research/t248-dirtentry-residue/check_release_evidence.py
python3 scripts/research_package.py --package research/t248-dirtentry-residue --check-only
```

The registered replay targets Python 3.12. This session ran the commands directly
with **Python 3.13.7**, not the Python-3.12-only launcher; metadata was checked.
The exact full-replay dependencies are in `requirements-reproduction.txt` and
the observed environment in `RUNTIME-VERSIONS.json`.

The complete immutable PR2833 source tree is intentionally not duplicated here.
Fetch its pinned object, then materialize and authenticate a fresh Git-free source
export. Fetching does not change the working branch:

```sh
git fetch --no-tags https://github.com/CrocSwap/integer-mult-bounds.git refs/pull/2833/head
python3 -B research/t248-dirtentry-residue/materialize_source.py \
  --repo . --out /tmp/t248-pr2833-source
python3 -B research/t248-dirtentry-residue/reproduce.py \
  --source /tmp/t248-pr2833-source --work /tmp/t248-full-release --jobs 4
```

The convenience wrapper was checked by actual source export, argument/path
preflights (including a path with spaces) and dry runs. Its new top-level entry
point was not run end-to-end; the retained complete run executes its exact
constituent native/admission commands. No Windows replay was run.

The default complete command prepares the four native providers and retained
parent freshly, then runs the entire candidate admission and outer release.
`--prepared-native /absolute/path` is explicit reuse: full source/cache inventories,
word identity and stage receipts must authenticate. Output paths must be fresh.
The wrapper rejects cache directories before expensive work; it never cleans or
modifies an input source. Exact recorded argv arrays are retained with evidence.

## Provenance, overlap and credit

The branch started at main `8dc7cef9d60b4eb974f61362b277cbc85121fdda` and refreshed
through `d359705715f45a25d46c593a542e8d071c47160a` and finally
to `116a714d150b6b45e134063a5fc1f873b3e1155d` before publication. Priority revision 5
and the selected exponent were unchanged. The original task draw is retained in
`TASK.json`; its changed scope is explicitly declared. This continuation answers
PR2843's concrete open residue-exchange question. The earlier T148 version is a
local positive control, superseded by the T248 comparison. The canonical claim is
[Discussion 2612](https://github.com/CrocSwap/integer-mult-bounds/discussions/2612#discussioncomment-18962648).
Live open-PR search covered 616 records at the recorded checkpoint; broad
Discussion pagination failed with network EOF. Targeted threads were read; the
coverage limitation is retained in `evidence/OVERLAP.json`. No novelty guarantee
is inferred from absent search matches.

Exact predecessor pins and preserved source notices are in `SOURCE-PINS.json`:

- **Jeremy Kothe**: PR2833 dirt-entry words, head
  `e9307b48d7d1b690939935ecef0f8e524e6d92f4`.
- **Marius-Paul Dumitrean**: PR2843 T124 literal allocation, head
  `47a7227c044cd0cabb1432a06c61dd5d60c07f5a`, and PR2802/prior lineage.
- **Dugongue**: PR2839 tensor-block replica contract and independent machinery,
  head `2fdd289fcd0896f4691f9dd78a8bf1511573e434`.
- **Tekalign**, Mason Hale, Philippe Van Velzen and all contributors named in the
  retained `NOTICE`/`CREDITS` files: native, owner, admission and source lineage.
  The packing-envelope tool retains Douglas Colkitt's notice.

Prepared for **Yiyang (@Lyy-iiis)** with substantial **OpenAI Codex assistance**,
including parallel construction and separately implemented audit agents. This
is not independent human review. New work is Apache-2.0; inherited notices and
source-specific licenses are preserved.

## Open next questions

Can an actual source-window-respecting exchange improve the remaining rank-two /
rank-sixteen residue? Start with one explicit exchange in the stored T248 fill,
price its complete histogram, and reject it before expansion if the moment or
physical/precision budget loses. The fixed local inventory limits the available
gain. Separately, the inherited all-size interface obligations need proof;
a useful first step is one explicit source-access or precision/tape interface
audit against the selected review and the retained block-norm proof. Structured
questions and blockers are in `TASK.json`.
