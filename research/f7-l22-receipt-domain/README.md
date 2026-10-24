# Bind the length-22 acceptance domain to the recorded census receipts

**Scoped successor to #4221 Open next question 2. No new census, no new kappa,
no newly proved `f(7) = 24`.** This package replaces trust in a copied split
list with an independent arithmetic reimplementation of the credited #3708
mathematics and an exact acceptance adapter. It leaves every predecessor package,
engine, selected record and ledger intact.

## Result and evidence status

The supplied checker derives **eleven** representatives `s >= t` at `n=7, L=22`
from four necessary conditions, before any 17-point exclusion. It compares every
arithmetic row with #3708's retained pre-import result, including revisits and
self-avoidance. It then requires the four completed #3818 receipts and seven
completed #4221 receipts to form an exact partition of that domain. Duplicate
split rows are rejected before constructing a mapping; coverage cannot be
silently narrowed by deleting a domain entry and its receipt together.

**Completed scoped acceptance adapter; author-checked/orchestrator-replayed.**
On 2026-10-22, the orchestrator observed metadata validation and both registered
normal and `-O` replays pass under **CPython 3.12.13**. Both replays emitted
`PASS_F7_L22_RECEIPT_DOMAIN domain=11 prior=4 deep=7 controls=30 no_census_replay`.
The emitted `recorded_deep_nodes=173808188827` is the sum of authenticated
historical receipt counts, **not nodes executed by this adapter**. Read-only
Git-object extraction and standard hashing also found all twelve declared
source files equal to their package-base working bytes. A completed independent,
read-only AI review found no blocking mathematical or acceptance defect; the
reviewer performed no execution. Neither that review nor the replay receipts
constitute independent human review, formal verification or scientific endorsement.

This is an **authenticated-recorded-counts adapter**, not independent census
replay. Its finite controls test the acceptance boundary; they do not manufacture
mathematical novelty or establish the correctness of the full enumeration.

## Exact scope and source lineage

Package base: `b58ad9ef4d4e861b0eaa5dba41742bdc072dca51`, priority revision 7.
The selected conditional kappa at this base is `0.00302015`, unchanged.

- [#4221](https://github.com/CrocSwap/integer-mult-bounds/pull/4221), Nick
  Petalas, head `9d21222c67ecd40f49935a1e56b11f2b50d54613`:
  [deep-shard census](../f7-l22-deep-shard-census/README.md), especially
  `verify.py`'s `check_receipt()` and
  [Open next questions](../f7-l22-deep-shard-census/README.md#open-next-questions),
  question 2, “Recompute the domain inside the verifier.” Its receipt, engine
  manifest and cover generator are retained unchanged.
- [#3708](https://github.com/CrocSwap/integer-mult-bounds/pull/3708), head
  `ba1aff20ee3ce3dce35e4978feab0b6be08c7168`:
  [split-domain proof](../f7-l22-split-domain/README.md#the-derivation-and-what-is-proved-here)
  and [length-22 domain](../f7-l22-split-domain/README.md#the-length-22-domain),
  arithmetic in `verify.py`'s `identity_need()`, `even_budget()`, `split_row()`
  and `admissible_splits()`, and the pre-import `RESULT.json` rows.
- [#3818 union census](../f7-l22-union-census/README.md): retained `RESULT.json`
  and unchanged `engine/union_census.c`. The latter is hashed, never compiled.

All `SOURCES.json` source pins resolve at the package base, so every source
commit is an ancestor of the base (the base itself). The two historical PR heads
above identify attribution and review context, not extra unmerged dependencies.
The originating catalogue card and selected record are Git provenance; the ten
research inputs are live and all are listed in `VERIFY.json`. The original card
was copied from the committed base object, not from a mutable task-picker result.

The catalogue's `census-pruning-audit` card is **refined** to one downstream
acceptance-boundary audit. This answers the explicit retained open question
rather than repeating a tiny-domain prune audit or launching a larger search.
No pruning implementation changes. The scoped budget is 60 minutes; registered
replay is bounded by two 30-second command timeouts, without compilation or
enumeration of length-22 words.

Final local overlap intake on **2026-10-22** covered **299 open PRs** at
**19:49:07Z** and **3,721 Discussion records** at **19:49:40Z**, with complete
pagination, plus all **5,860 tracked local notes** and two other new package
notes. Exact phrase searches found predecessor/own-note references only. This
is not a novelty proof, an arbitrary-diff search or an exhaustive search of
closed remote PRs. Coordination is local-only; no public Discussion claim is
asserted. Canonical refresh `624de9dc66858af0945e5f8a0942488d62280d43` left
the guidance, catalogue, selected record and all source packages unchanged
relative to the pinned scientific base; the original base and card pins remain.

## Derivation and proof boundary

Let `q_0,...,q_22=q_0` be the restored singleton prefix walk in `F_2^7` and let
`P` be its distinct prefix states. Write `E,O` for their Hamming-weight parity
classes and `s=|E|, t=|O|`. A universal prefix set has `P+P=F_2^7`. The following
are necessary conditions, **not sufficient conditions for a word to exist**.

1. **Time:** parity alternates with step number. Among positions `0,...,21`
   there are eleven of each parity; `q_22=q_0` supplies no new state. Thus
   `s,t <= 11`.
2. **Odd budget:** each of the 64 odd masks needs an `E x O` pair, so
   `s*t >= 64`.
3. **Even budget:** the 63 nonzero even masks need unordered, distinct same-class
   pairs. Thus `B = C(s,2)+C(t,2)-63 >= 0`.
4. **Pair identity:** let `A_x,B_x` be unordered pair multiplicities at nonzero
   even mask `x` within `E,O`, and let `r_y` count cross pairs at odd `y`.
   Counting four-cycles gives
   `sum_y C(r_y,2) = 2 sum_x A_x B_x`.
   Since every odd mask occurs and `C(r,2) >= r-1`, the right sum is at least
   `ceil((s*t-64)/2)`, denoted `need`. Let `a,b >= 0` be the collision excesses
   within the two same-class supports. Their intersection has size `B-a-b`.
   Expanding `A_x B_x` on that intersection bounds its sum by
   `(B-a-b)+a+b+a*b = B+a*b`. In particular `a+b <= B` and
   `a*b <= floor(B^2/4)`. Hence `need <= B+floor(B^2/4)` is necessary.

At `L=22`, the even-budget condition is redundant once the identity-bound check
is enforced: the adapter makes its identity upper bound negative when `B < 0`,
whereas `need >= 0`. These are four stated necessary conditions, not four
separately load-bearing acceptance controls.

A one-step rotation translates the restored prefix set by an odd state and
swaps its parity classes, preserving universality. Therefore `s >= t` is a
complete quotient of the ordered split problem. This written implication and
the underlying singleton prefix-walk interpretation are inherited from #3708;
they are not re-proved by the finite controls or checked in a formal kernel.

`verify.py` enumerates all positive `1 <= t <= s <= 22`, deliberately beyond the
time bound, and applies the four conditions using only integer arithmetic.
This is an independent arithmetic reimplementation of #3708's mathematics,
not an independent discovery or proof of those necessary conditions. There is
no acceptance-domain table in the adapter. The recorded table is used **only as
a comparison oracle after recomputation**, not as the source of accepted splits.
The integer product bound is also checked by direct maximization over
`a+b <= B` for `B=0,...,47`; the ceiling check includes the odd excess 57.

| Split | Distinct points | Revisits among cyclic positions | `B` | `need` |
|---|---:|---:|---:|---:|
| (11,11) | 22 | 0 | 47 | 29 |
| (11,10) | 21 | 1 | 37 | 23 |
| (11,9) | 20 | 2 | 28 | 18 |
| (10,10) | 20 | 2 | 27 | 18 |
| (11,8) | 19 | 3 | 20 | 12 |
| (10,9) | 19 | 3 | 18 | 13 |
| (11,7) | 18 | 4 | 13 | 7 |
| (10,8) | 18 | 4 | 10 | 8 |
| (9,9) | 18 | 4 | 9 | 9 |
| (11,6) | 17 | 5 | 7 | 1 |
| (10,7) | 17 | 5 | 3 | 3 |

Here revisits count `22-|P|` among `q_0,...,q_21`, excluding the mandatory final
return. Only `(11,11)` forces a simple cycle; all other representatives require
revisits. `(9,8)` passes time and both budgets but has `B=1, need=4`, so the
identity excludes it. `(11,6)` and `(10,7)` remain in the acceptance domain:
**no #2773/#2870 17-point exclusion is imported**.

## Receipt binding, controls and inherited guarantees

The adapter first authenticates every live source byte against both SHA256 and
Git blob pins. It parses JSON with duplicate-key rejection. It imports no old
Python helper and launches no subprocess; source closure therefore does not
silently depend on those helpers' imports or runtime-generated artifacts.
The fixed `n=7, L=22` interpretation is inherited from the exact authenticated
source context; these are not parameter fields read from either census receipt.

From the authenticated #3818 receipt it records each original completion state.
A capped row is never promoted to complete by changing its flags. At the semantic
boundary it checks strict Boolean completion, exclusion-flag consistency, zero
hits, recorded count types, the global depth-four prefix inventory and cap
consistency where recorded. Its four completed splits are
`(9,9), (10,8), (11,7), (11,8)`. Among those four, only `(9,9)` records
`shards_recorded=15` and `capped_shards=[]`. The other three are `source:control`
unsharded runs without `shards_recorded` or `capped_shards` fields. The global
depth-four inventory does not establish individual shard evidence for those
three rows, and their recorded `sharded_nodes` fields do not supply shard logs.

For the deep receipt it independently generates restricted-growth words over
seven labels: 203 depth-six prefixes, replacing `012345` by its 49 depth-eight
extensions, yielding 251 entries. Every depth-eight restricted-growth word must
have exactly one cover prefix. It requires the recorded cover metadata, exact
ordered per-shard keys, nonnegative integer counts, total equality, strict
`complete=true`, zero hits and empty hit-word arrays on all seven deep rows.
The deep receipt's engine hash explicitly covers these seven deep rows and must
agree with the actual engine bytes, the new manifest and #4221's unchanged
manifest. The prior receipt has no engine hash: its same-engine provenance rests
on retained history, not an authenticated runtime engine field. Finally the
deep keys must equal **derived domain minus prior completed keys**, not merely
contain some claimed remainder.

Controls operate on deep copies of the **actual authenticated receipts**. They
require positive acceptance of the original pair and reversed split-row order,
then rejection of:

- each of the eleven individual admissible-row omissions;
- duplicate deep and predecessor rows, and duplicate JSON member names;
- incomplete deep rows, truthy non-Boolean completion, false predecessor
  incompletion, and a capped predecessor falsely marked complete with its
  exclusion/cap fields changed consistently;
- positive hits in either receipt and hidden hit words despite a zero hit count;
- an unexpected `(9,8)` row;
- a narrowed domain alone, and a co-mutated domain **and actual receipt** removing
  both 17-point rows (an imported-exclusion-shaped mutant);
- a missing shard, wrong total, negative shard count, changed engine identity,
  omitted cover entry and overlapping cover prefix.

These controls run through the real acceptance adapter, with reason-checked
rejections. They cannot pass just because a generic parser crashes or an
always-rejecting adapter rejects everything. Explicit exceptions, not `assert`,
enforce all obligations under normal Python and `-O`.

| Boundary | Added or preserved here | Not discharged here |
|---|---|---|
| Domain arithmetic | Independently reimplement credited #3708 arithmetic for eleven pre-import rows, compare all row fields, classify revisits | Formal necessity/rotation proof; realizability of any admitted split; `n=7,L=22` inherited from authenticated source context, not receipt fields |
| Receipt acceptance | Exact partition, unique split identity, completion/hit rejection | Fresh completion of any census process |
| Deep sharding | Independent 251-prefix partition, per-shard keys, integer totals | Raw shard logs, engine traversal/pruning correctness |
| Engine identity | Hash exact unchanged C source; compare #4221 manifest and engine hash covering seven deep rows | Prior receipt has no engine hash; its same-engine provenance is retained history, not a runtime field; no compilation, independent engine or giant replay |
| Historical predecessor totals | Authenticate recorded bytes and check count types; `(9,9)` records 15 shards, three other completed rows are unsharded controls | No individual shard evidence for `(10,8), (11,7), (11,8)`; global depth-four inventory does not supply it |
| Theorem/frontier | No altered source, selected kappa, tariff or supplier | New `f(7)=24` proof, formal kernel certificate or multiplication theorem |

In particular the deep aggregate receipt records one completion flag per split,
not raw per-shard completion/exit logs. Authentication preserves that historical
claim; this adapter does not invent missing logs. Balanced changes to counts and
totals are excluded by source authentication, not by arithmetic total checks
alone. Recorded cover sums repeat prefix nodes across shards; they must not be
compared with differently sharded or unsharded counts as though identical.

## Reproduction

From the repository root, using CPython 3.12 (observed: 3.12.13):

```sh
python3.12 -I -B research/f7-l22-receipt-domain/verify.py --emit
python3.12 -I -B -O research/f7-l22-receipt-domain/verify.py
python3.12 -B scripts/research_package.py --package research/f7-l22-receipt-domain --check-only
python3.12 -B scripts/research_package.py --package research/f7-l22-receipt-domain
```

The first two commands are the registered bounded replays; metadata validation
(`--check-only`) and invocation of both registered commands through
`scripts/research_package.py` passed on 2026-10-22 under CPython 3.12.13.
The observed marker from each replay was:

```text
PASS_F7_L22_RECEIPT_DOMAIN domain=11 prior=4 deep=7 controls=30 no_census_replay
```

`--emit` printed deterministic derived rows, receipt partition,
`recorded_deep_nodes=173808188827` and names of rejected controls. That count
comes from recorded census receipts; no census nodes were executed. All source
inputs are read-only and the adapter creates no files. Normal and optimized
replays each have a 30-second manifest timeout. The orchestrator reported
1.13 seconds for the combined shell command including environment setup and
metadata validation; this is **not a precise adapter benchmark**. These are
orchestrator replay receipts, not contributor-run checks. The completed read-only
AI review is separate evidence, with no reviewer execution and no human or formal
endorsement.

## Open next questions

The structured questions and blockers are also in `TASK.json`.

1. **Can an independent engine reproduce the seven deep exclusions?** This would
   address the single-engine dependency that no receipt adapter removes. First
   separately scope lifting #3005's `L<=20` C++ gate, then compare one split
   shard-by-shard. Blockers: explicit compute authorization, extension review and
   unknown length-22 throughput; this is not an instruction to run it here.
2. **Can a proof kernel check the pair-identity necessity and rotation quotient?**
   Exact finite arithmetic does not formalize the universal-walk implication.
   First formalize the four-cycle double-counting identity and one-step rotation.
   Blocker: a separately scoped formal model and proof-assistant contribution.

## Attribution and license

Nick Petalas's #4221 deep census, #3708 split-domain work and #3005/#3731/#3818
union-budget/census lineage are the direct predecessors; the existing source
notices remain unchanged. Retain Ross Richardson's PR943 prefix-walk model,
Aaron Wang's PR2542/PR2634 word-model contributions, and Nicholas Stone's #2973
corrected Hamming-weight-parity engine and calibration. The historical 17-point
line #2773/#2870 is credited in predecessor sources to Aaron Wang / `navinor`;
its exclusions are not dependencies of this adapter. Douglas Colkitt's source
binding, package registration and review conventions are retained.

This user-authorized contribution was prepared with substantial OpenAI Astra
assistance in code, controls and prose. Internal source inspection is not an
independent human review. Apache-2.0; no predecessor attribution is replaced.
