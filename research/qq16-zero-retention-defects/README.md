# Completed-error allowance for QQ16 zero-retention decoding

This closes one local precision question in
[PR #2707](https://github.com/CrocSwap/integer-mult-bounds/pull/2707), pinned at
`efa51a6c7ffec6edd556a98deedfe9deeba65809`. Its line-normalized word differs
from the retained-record word studied in PR #2628/#2670/#2692. Their error
numbers do not transfer. The decoder word, ideal native semantics and local
invoice are unchanged.

For arbitrary supplied current X/Y arrays, fix a positive upper bound B on
their maximum per-owner payload Hilbert norm. A completed-instruction relative defect

```text
u <= 2^(-b-22), b >= 0
```

suffices for strict error below `B*2^-b` at every initialized field and cut,
at every positive common payload tensor depth. All 224 borrowed arrays are
exactly unchanged because the literal word never writes them. Owned CLEARs
are exact, and uninitialized owned dirt is never read. This is a sufficient
caller lemma, not a physical component-rounding format or complete supplier.

[PROOF.md](PROOF.md) specifies the local defect premise and proves

```text
all-cut error <= B * 2919388*u / (1 - 199144*u)
all-cut magnitude <= 32368*B + all-cut error
```

when `u < 1/199144`. The guard follows from
`2^21 < 2919388 + 199144 < 2^22`. Twenty-two is minimal only for this
particular majorant's uniform sufficient test, not for the actual decoder.
For absolute per-instruction tolerances, the separate bound is

```text
67401*eps_add + 32711*eps_line + 33464*eps_map.
```

These triangle bounds deliberately discard signed cancellation. No envelope
is claimed to be a sharp operator norm.

## Evidence and reproduction

The independent checker imports no predecessor executable. It authenticates
exact source snapshots, propagates six rational weights through every
instruction, then checks every cut by a separately implemented reverse
adjoint traversal. [RESULT.json](RESULT.json) records all 3,816 cuts and
22,896 matching weights, with all peaks at event 3807, `W0 -= Z0`.

```sh
python3.12 -Werror -I -B scripts/research_package.py \
  --package research/qq16-zero-retention-defects
python3.12 -Werror -I -O -B research/qq16-zero-retention-defects/verify.py
```

Expected primary result:

```text
PASS_QQ16_ZERO_RETENTION_DEFECTS cuts=3816 P=32368 J=2919388 K=199144 guard=22 borrowed_writes=0 no_new_kappa
```

The primary takes about 13 seconds on Linux/WSL2, CPython 3.12.15. The
registered replay runs normal and optimized checks plus eleven behavioral
test groups. Controls exercise noncommuting isometries, a cleared real
transient, missing defect loads, dirty reads, borrowed writes, scratch
cleanup, capacity, guard failure, and actual CLI source/typed-receipt
corruption, including duplicate JSON keys and an altered cut weight. A Git-free relocated replay preserves every copied file.
The default command is read-only; `--write PATH` creates only an absent
receipt and refuses to overwrite one.

[PREDECESSOR.json](PREDECESSOR.json) gives the exact PR head, Git blobs and
SHA-256 hashes for retained source files. Links inside those verbatim source
documents refer to the original PR package, not a complete vendored replay.
[SOURCES.json](SOURCES.json) pins the base catalogue/selected record as
historical provenance. No current selected input or frozen predecessor
package changes.

## Scope and remaining obligations

The native line/map isometry premise is inherited from the retained source
proof. A completed line includes its wrappers; a completed map includes its
entire owner/payload action. Defects affect only the specified destination.
Exact owned CLEAR and exclusive owned storage are explicit assumptions.
This check does not implement or prove those physical contracts.

Entry/F0/B1 error bounds, recursive child internals, component rounding,
physical map/wrapper/movement/hosting costs, output consumption, supplier
admission and a new kappa remain open. The 22-bit allowance is relative to
B in a Hilbert norm; it is not a per-component bit count. No full selected
cold replay, independent human review or proof-assistant verification is
claimed. A scoped internal review and local checks are recorded in TASK.json.

## Open next questions

Can one physical rounded implementation supply the completed line and map
premises with the stated u? Begin with a literal signed rank-one recipe,
including its wrappers, and bound component-rounding defects in the declared
payload norm. The child internals and actual payload dimension are blockers.

Can the complete caller bound B at the post-B1 entry and afford these
allowances together with movement and its output consumer? Pin one caller's
entry/ownership/consumer contract and price the entire construction before
further optimization. No such complete caller is admitted here. Structured
questions and the local-only-module expansion decision are in [TASK.json](TASK.json).

## Implementation constraints

The fixed word bounds execution to 3,823 events, 464 named fields and
3,816 adjoint traversals of prefixes. Input reads are capped at one megabyte
per source and two megabytes per receipt. Functions stay below 60 lines;
checks remain enabled under `-O`. Managed Python/Fraction allocation is a
Power-of-Ten rule-3 deviation. Live data are bounded by these fixed
capacities, not a steady-state allocation prohibition. Fraction bitlength
is bounded by the finite rational recurrence. A fixed-buffer implementation
would be needed for a stricter runtime target. Strict receipt parsing uses
one fixed JSON object-validation callback, capped at 464 pairs; it rejects
duplicate keys before comparison. Lint and behavioral checks cover this
package, not unrelated frozen scripts.

## Credit

New lemma and checker by Nick Petalas, Apache-2.0. Credit ywz65 for PR #2707
and PR #2540, Arham Tahir for PR #2681, Ali Romman and the retained QQ16/native
lineage, and the earlier completed-defect analyses in PR #2628/#2670/#2692.
The exact predecessor proof and README retain their original notices.
[Canonical claim and findings](https://github.com/CrocSwap/integer-mult-bounds/discussions/2727).
