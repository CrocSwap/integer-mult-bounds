# An exact alpha74 deletion-quantifier obstruction

A direction-dependent ONE-root deletion can admit an eight-dimensional
orthogonal family after fixed P112 binary seven-flat and four-flat covers.
For this SAME eight-normal family, ONE common cut of at most two roots admits
at most two dimensions. The exact vectors, cover closures, functional spectra
and all 6,216 common two-cuts are checked with integer/binary arithmetic.

This is a partial result from the reserved universal common-two span-five
question. That original predicate is UNSETTLED. The maximum two applies only
to the exhibited eight normals, not all qualifying directions. No caller
exclusion or new kappa is claimed.

[PROOF.md](PROOF.md) gives the argument. [WITNESS.json](WITNESS.json) contains
literal roots, normals and individual cuts; [RESULT.json](RESULT.json) binds
all proof-relevant counts. The purpose is to show why the direction-dependent
relaxation in the predecessor finite tester cannot resolve the common-cut
handoff. PR3154's original no-extra-cut alpha74 theorem remains unchanged.

## Reproduce

From a checkout, with an existing Python 3.12 installation:

```sh
python3.12 -Werror -B scripts/research_package.py --package research/p112-alpha74-cut-quantifiers
```

The committed package export and its declared geometry input also run without
Git. Run ALL three direct commands from the export root:

```sh
python3.12 -Werror -B research/p112-alpha74-cut-quantifiers/verify.py
python3.12 -Werror -B research/p112-alpha74-cut-quantifiers/independent.py
python3.12 -O -Werror -B research/p112-alpha74-cut-quantifiers/test_verify.py
```

The primary checker authenticates exact source inventories, reconstructs the
canonical roots/labels, checks complete cover closures and the Gram matrix,
and enumerates all 512 binary functionals for each normal. The second checker
uses a separate matrix elimination on all 6,216 common cuts. It shares the
root-label input and authentication helpers, which is an explicit dependence.
Controls reject changed cuts, dependent normals, invalid covers, bool-valued
schema/index fields, altered source usage/inventory and corrupted input bytes.
Actual primary and second-checker processes reject the corrupted source.

Set TMPDIR to your own writable scratch directory when replaying a read-only
export. Controls create fresh writable copies there; they never change the
export or source permissions. No third-party Python dependencies are needed.
Retained vendor/ C/proof files are documentary source inputs, not executable
replay commands. Their original limitations and attribution remain intact.

## Source and verification scope

Base main is 463113d675af7410ac91d53a4fed51ec6494eb9a, priority revision 6.
SOURCES.json pins canonical geometry and historical orientation metadata.
PREDECESSORS.json pins verbatim PR3154 at708f0ad8928c383de8294aea3c126e9461d2066d
and PR3289 ate8570c50f9591c9ca653a527ed9626aaa703c3bc. No pending fork Git objects
are needed for the direct replay. Source authentication is not mathematical
admission. CHECKS.json records actual runs and the bounded search limits;
REVIEW.json records the designated internal read-only review when available.

Public overlap at entry covered 342 open PRs at21:05:35Z and 2,137 Discussion
records at21:06:07Z with complete pagination; 2,630 closed PRs had the older
20:44:55Z cutoff. Arbitrary diffs and unpublished work were not exhaustive.
The exact partial scope correction was recorded before freeze. Sibling A2
rank-six, universal566 commoncut32, rank-seven capacity and QQ16 depth work
have distinct predicates. No sibling tentative lemma is used here.

## Code inspection and bounded deviations

The new Python paths use structured control flow, explicit fixed 112-root,
eight-normal, nine-bit and 512-functional bounds, checked return values and
runtime contracts that remain enabled under optimization. Functions stay below
60 physical lines after formatting. Input reads are capped at100,000 bytes.

Power of Ten rule3 has a managed-runtime deviation. Python and exact rational
source reconstruction allocate dynamically; live data is bounded by the fixed
root inventory, eight33-root supports, one512-functional scan or one33-by9
matrix, and the input-size limits. Rule8 has one bounded source-execution
deviation: runpy compiles the sole authenticated canonical geometry.py, with
no .pyc import or generated code. The fixed target and byte hash are checked
before execution. It imports only its documented standard-library dependencies.
The immutable retained C proposer is not executed by the package; its legacy
recursion, allocation and diagnostics are not adopted as verifier code.
Static diagnostics cover the new three Python scripts; source-model mathematics
and the standard library remain explicit dependencies.

Separate Before Serializing Shared State kept all scratch and control copies
session-owned, with short OS locks only for shared Git/claim transactions.
Prove It Works required actual committed read-only, Git-free replay of all
three scripts. Unslop kept the claim and the remaining obligation explicit.

## Open next questions

Does the universal common-two span-five statement hold for arbitrary fixed
seven-flat and four-flat covers? This could address the named historical
quotient-basis seam under PR3289's hypotheses. Start with a fixed deletion set
and classify the whole qualifying direction set; the eight-normal bound here
does not supply that classification. Family decision: retain this exact
partial obstruction and stop this session. Physical supplier/consumer costs
remain unknown and unused.

Credit DreamingOfClouds/PR3154, Nick Petalas/PR3289, the canonical PR3161/3162
root-simplex source and the retained E8/P112 lineage including joaqcoo.
Apache-2.0. Internal computational review is not human or proof-kernel approval.
