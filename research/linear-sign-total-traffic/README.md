# Exact total traffic of the all-size BIT caller's linear sign

The new result is an **exact all-parameter logical tape invoice** for
David Arias's PR2753 linear sign, including every countdown's setup,
normalization, decrement and disposal, numerical setup, payload and head
movement. On its canonical Ring inputs, the complete successful interval
costs less than **2048V** reads/writes/unit head moves for V=BMS. The
constant is conservative. [PROOF.md](PROOF.md) gives the quantified domain,
closed formula and source-operation proof.

This corroborates the pending caller's local linear sign charge. It does
not improve kappa, admit a supplier, price a physical compiler or prove the
other route/leaf H2 obligations. No production or frozen predecessor files
are changed.

## What this adds to the predecessor

PR2753 at `7dba5452a4071a856a0b11cebdcd2d3b6bcd7659` already supplies the
routine, its endpoint, exact source movements `(6M-8)BS+4`, a `3B`
residue-counter setup control and five measured control-traffic cases.
Those results are predecessor work. This package independently derives

```
C(n,d) = 15n + 14d - 5 popcount(n) + 36   (n>0)
C(0,d) = 14d + 40
```

for a complete countdown, then composes every loop into an exact total
invoice. Thus the uniform bound is a written source-level lemma, rather
than an extrapolation from finite traffic samples.

An endpoint-preserving padded-two mutation increases the M=65 fixture from
24,454 to 35,353 total operations while leaving its 386 source movements
unchanged. Its extra cost is `B(M-2)C(2,L)`. A padded-width interface control
also shows why the canonical Ring premise matters; the actual production
Ring rejects that padding. Neither control reports a current production bug.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/linear-sign-total-traffic
```

For a portable replay without Git or the repository runner:

```sh
python3.12 -B research/linear-sign-total-traffic/verify.py
python3.12 -O -B research/linear-sign-total-traffic/verify.py
```

Expected: `PASS_LINEAR_SIGN_TOTAL_TRAFFIC counters=387 signs=150`.
[RESULT.json](RESULT.json) records 387 countdowns, 150 signs / 24,624
addresses, source/head/live-numerical restoration, three malformed-source
controls, the padded-word and padded-counter controls, a wrong-backstep
mutation and source-corruption rejection. The checker authenticates and
compiles literal exported bytes directly, without using cached bytecode.
The typed receipt rejects Boolean/integer substitutions. Assertions are
not acceptance gates. Normal verification writes no files; `--write PATH`
explicitly creates a new receipt and refuses overwrite.

Registered normal and optimized replays pass locally on CPython 3.12.14,
including the refreshed main runner. A Git-free exported replay passes on
optimized CPython 3.14.7. A before/after inventory confirms all 20 package
files remain byte-identical during registered replay. Publication-byte
preflight passes. Hosted CI and the selected full cold replay are not
claimed.

The finite cases corroborate the proof, not the full all-size caller.
The interval excludes initial Ring/extent construction, eventual disposal
of the returned output, physical placement and exceptional-path complete
counter cleanup. See the proof for the remaining obligations.

## Sources and coordination

Started from canonical main `4b82082f901945f8d0314f143576c7ad31e021fc`,
priority revision 5, using the task picker nonce
`dbd1c5cd78cdfc2470dc907fd989ab72` and refined `supplier-boundary-audit`.
[TASK.json](TASK.json) records the bounded scope, overlap coverage and next
questions. [SOURCES.json](SOURCES.json) pins historical assignment/selection
provenance; [EXPORTS.json](EXPORTS.json) authenticates every consumed
predecessor export by exact commit, original path, Git blob and SHA256.
All executed dependencies are contained in this package.

The [canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2319#discussioncomment-18965676)
joins the existing selected-BIT caller investigation. Entry overlap covered
496 open PRs including drafts and 1,517 Discussion/comment/reply records,
with complete pagination and no warnings. Searches cover metadata and local
notes, not every arbitrary diff or unpublished result. Newer geometry,
storage and physical-wrapper work is complementary; none is reconstructed
or claimed here.

Submission refresh covered 491 open PRs and 1522 Discussion records,
with complete pagination and no warnings; exact timestamps and scope comparisons
are in TASK.json. The package is rebased on canonical main
`c7df0bb890cae0cc393cdd32dad19c3facc80992`; assignment provenance stays at
the original base. PR2753's head was unchanged.

## Open next questions

1. Bind the latest complete caller's remaining route/ordinary leaf paths to
   stronger selected H2 time contracts. First pin the current Discussion #2319
   handoff and isolate one actual reached primitive. This matters because
   the sign lemma alone does not establish the selected saving. Complete
   source/physical movement and return charges remain the blocker.
2. Consider adopting the exact total-traffic formula as a predecessor
   regression gate. First compare traffic.py and the padded-two control with
   the pinned check_sign.py. This detects a cost defect that endpoint and
   source-movement checks miss. Maintainer choice and compatibility with
   subsequent caller sources remain separate; frozen files are preserved.

Structured versions are in TASK.json. No expansion of the caller family is
proposed by this package.

## Credit

David Arias / DavidAriasC supplied PR2753's linear sign and all-size logical
caller. Jose Manuel / jmbarrancoml supplied PR2697 and its retained Tape,
Word, Counter, complete-fibre and caller lineage; its unchanged attribution
is [preserved here](sources/PREDECESSOR-NOTICE.md), including ywz65's earlier
primitive sign-cost audit. Their algorithms, endpoint and setup-control
results are not claimed as new. This package adds the independent exact
traffic derivation, uniform bound and fully metered source-bound replay.

Prepared by Arham Tahir with substantial OpenAI Codex assistance in proof,
implementation and review. No human peer review or formal-kernel verification
is claimed. Apache-2.0; the repository license and predecessor notices apply.
