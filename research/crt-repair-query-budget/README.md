# Current-state CRT queries in an exceptional repair key

The literal `T(S^-1(q))` key reads CRT controls at **three current states**:
inside each of the inverse word's two loads, then at the recovered origin for
`T`. Reusing the entry offset can send an exceptional payload to the wrong key.
Modulus-only inverses can nevertheless be prepared once: **m+1 inversions
suffice per fixed left group/target**, with none during subsequent queries.
This is a construction, not an inverse-count lower bound.

This answers the inverse-macro handoff in
[PR4409](https://github.com/CrocSwap/integer-mult-bounds/pull/4409).
[PROOF.md](PROOF.md) gives the quantified cache identity and query argument.
It also amends PR4377's source-table arithmetic for three reconstructions,
six conservative rotation networks and explicit padded-validity comparisons.
Under the stated inherited local tariffs and aligned-input premise, the
allowance still satisfies `E_src <= 2^(4 ell)(p+2)^16` for every integer
`p>=2, ell>=1`; the existing guard amortization follows with constant one.
This does **not** price the entire key evaluator or establish a new κ.

## Caller evidence

[caller.py](caller.py) combines source-authenticated retained CRT/Beneš code,
the PR4169 literal inverse word, and PR4174 reservoir descriptors. The fixture
uses proper prime widths `(4,4,5,5)` and moduli `(11,13,17,19)`. The target is
root axis 2, local Beneš row 6; three bits from inactive axis 3 are exchanged
into the borrowed fields. One left-coordinate bit moves above the target,
where exceptional carries can change its current CRT value.

Two exact witnesses appear in [RESULT.json](RESULT.json):

| Input `(u,t,y)` | Offsets at the three live queries | Correct key | Key with entry offset frozen |
| --- | --- | --- | --- |
| `(0,1,4)` | `5,4,4` | `(0,1,30724)` | `(1,1,30724)` |
| `(1,1,4)` | `5,5,4` | `(1,1,30724)` | `(1,1,31236)` |

Both have valid left coordinates throughout; the padded target domain is
allowed. The second recovers the same inverse origin even with the stale
source, isolating the need to refresh the final `T` query. The mutant still
reads the **current target coordinate**; only its entry CRT offset is frozen.
No claim requires three distinct offsets.

The frozen receipt checks all 32,768 middle fields and all 131,072 dirty
`(u,t,y)` states of this switch. It verifies literal inverse/forward agreement,
16,384 good states, all 114,688 exceptional keys, and complete repaired payload
correspondence. The back bit is an omitted spectator. A separate inverse spy
permits exactly three setup calls and rejects any later inversion. Four small
fixed-modulus cases cover 548 padded vectors (266 valid), including nontrivial
right prefixes. Controls reject missing invalid-left disabling, dropping the
right-prefix factor and noninvertible fixed data.

The arithmetic grid covers 7,960 pairs (`p=2..200`, `ell=1..40`). Its largest
exact allowance/envelope ratio is `3162627/536870912`, about 0.005891, at
`p=2, ell=1`. The proof, rather than this finite grid, establishes the unbounded
tail. Host operation counts are not bit-step measurements.

## Reproduce

From the repository root, using Python 3.12 and only its standard library:

```sh
python3.12 -B scripts/research_package.py --package research/crt-repair-query-budget --check-only
python3.12 -B scripts/research_package.py --package research/crt-repair-query-budget
```

The registered commands run ordinary and optimized Python with a 120-second
limit each. Both compare the existing receipt without changing it. Direct
replay is `python3.12 -B research/crt-repair-query-budget/verify.py`; the explicit
`--write-result` option is only for authoring a new receipt. Eight live inputs
are checked by SHA256 and Git blob identity before their captured Python bytes
are executed, avoiding predecessor bytecode caches. A Git-free package export
supports direct replay; generic provenance validation requires Git history.

## Scope, overlap and limitations

Base: canonical main `b58ad9ef4d4e861b0eaa5dba41742bdc072dca51`, priority revision
7. [TASK.json](TASK.json) records the refined `uniform-transfer-audit` card;
[SOURCES.json](SOURCES.json) pins every retained input. The selected record and
catalogue are historical provenance. Selected conditional #4470 is unchanged.
Coordination: [Discussion #4709](https://github.com/CrocSwap/integer-mult-bounds/discussions/4709).
The live check covered 476 open PR bodies, 3,629 Discussion records and all
5,860 tracked local note records before the claim. PR4650's one-axis arena
tariff and PR4637's mask bridge are complementary; neither supplies this trace.
PR4644 joins the one-target unary producer, reverse keys and repair, but uses
a different key machine and explicitly leaves a reverse-shear bit-step price open.

This is a reduced fixture with `H=G=1, K=5`, below the production dimension and
guard constants. Its counterexamples reject a frozen-offset shortcut; they
are not counterexamples to the asymptotic construction. The universal cache
identity applies to arbitrary fixed coprime groups, but a finite current-y
lookup table is only a verification accelerator. We do not claim its memory
cost as a runtime algorithm. No physical coordinate materialization, complete
modular address-update cost, tape erasure, extraction/sorting, native lifting,
or outer multiplication theorem is verified here. Forward `S` adds its own
two source queries if included in a larger task.

## Open next questions

Bind the three current-state epochs to copied physical descriptors in a
literal complete key evaluator, then meter its address updates, fixed cache
and restoration. Start by joining the interface here to the pending #4650
shared arena and #4637 repair-mask work. This matters because source-table
arithmetic alone does not discharge CRT total repair. No blocker prevents a
scoped trace, but a full tariff needs their tape/head-movement premises.
See the structured handoff in [TASK.json](TASK.json).

## Credit

Cinna Davis supplies #4100's CRT construction; unpaidmoon supplies #4377's
local tariffs and envelope; Ryanson Jonathan supplies #4409's independent
arithmetic check and caller handoff; ToikY supplies the predecessor #4192
Beneš audit. Our prior #4169/#4174 supply the literal inverse and placement.
The generic exceptional-stream repair follows John-Michael Smith and Douglas
Colkitt's #763 lineage. Those results are reused, not claimed anew.

Prepared by Hiroki KUMAZAKI (@kumagi), with substantial OpenAI Codex assistance
in research, code, agent review and writing. Apache-2.0. No independent human
review, proof-assistant acceptance or complete theorem acceptance is claimed.
