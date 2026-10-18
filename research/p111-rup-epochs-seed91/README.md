# Faster ordered RUP replay for the archived P111 certificates

**Verification tooling, seed 91; no new kappa.** This opt-in checker accelerates
the two proof traces retained by Gareth Davidson's PR1097. It replaces per-lemma
assignment dictionaries with a signed epoch array and inlines the same rejecting
guards. Every lemma and ordered hint is still checked. The complete regenerated
PR1097 receipt is byte-identical after canonical JSON serialization.

Base: `1b59b624d21924f8e3537cdc1ac52d3be6eda2fe`.
PR1097 reviewed head: `ad0cc538d7f827461da6364c3c0e09176b10bcae`.
The selected conditional witness at this base is PR1094,
`kappa = 836330098538459 / 500000000000000000`. It is unchanged.

## Reproduce

Python 3.12 or newer; standard library only. From the repository root:

```sh
python3 -I -O -B research/p111-rup-epochs-seed91/verify.py
```

Expected: `PASS`, **37,044 additions**, **1,409,475 checked hints**,
**272,759 semantic cases**, **12,277 truth-table entailment checks**,
**12 packaging negative controls**, and `new_kappa: false`.
On the recorded machine this takes seconds. No solver, compiler, network or
repository-wide replay is needed.

To use only the complete optimized predecessor replay:

```sh
python3 -I -O -B research/p111-rup-epochs-seed91/replay.py
```

`--engine baseline` runs the unchanged checker through the same wrapper;
`--receipt PATH` writes the complete canonical receipt. Both give SHA-256
`ab65ab6dba482fb9c9741f7ff10235c972ed03052197ea1795374fd539a67d84`
(without trailing newline in the hash), exactly PR1097's receipt.
The wrapper authenticates the predecessor, rejects preloaded predecessor modules,
executes the authenticated source bytes without loading cached bytecode, then temporarily
substitutes only `lrat.check`; its parser, entire formula regeneration, geometry,
positive fitting matrix, original PR620 encoder comparison, all existing controls
and expected-receipt comparison remain active. No frozen file is edited.

## Why the storage change preserves the check

For lemma `position`, let `e = position + 1`. A variable's array entry is `+e`
if true, `-e` if false, and otherwise unassigned in this lemma. Falsifying the
proposed clause and propagating each unit update exactly the same variables as
the dictionary checker. Python integers do not wrap. Thus every assignment from
an earlier lemma is invisible, including assignments made while recognizing a
tautological clause.

The clause database, iteration order and acceptance predicates are unchanged:
strictly increasing fresh IDs; legal proposed literals; no hints after a
tautological addition; only earlier existing premises; no satisfied or nonunit
hint; duplicate copies of the same residual literal still count as one unit;
conflict at exactly the last hint; no intermediate empty clause. Rejections retain
the original diagnostic strings and literal-order priority. By induction over
the hint sequence, both checkers produce the same assignment, rejection or
conflict, and hence the same database and receipt after each accepted lemma.

The raw `check()` contract is deliberately unchanged: `parse()` enforces a
nonempty proof ending in the empty clause, and the authenticated generator
supplies valid original literals. The raw function alone is not a standalone
arbitrary-input LRAT validator. It retains only the positive-hint, deletion-free
RUP subset. Dense storage uses **O(variables)** extra slots (211,456 for c9),
whereas the old dictionary grows with assigned variables in a lemma. It is
intended for these pinned dense-numbered formulas, not arbitrary sparse IDs.

## Measured performance

[BENCHMARK.json](BENCHMARK.json) records seven alternating baseline/candidate
pairs on the same immutable inputs, with complete receipt equality required
after every run. Full runs are fresh processes with `-I -O -B`, from an unrelated
directory. Here "cold" means a fresh interpreter; filesystem caches are warm.
Isolated checker timings include database copying and epoch-array
allocation; formula construction and parsing are outside those isolated timings.
No checked proof result is cached. Times are local measurements, not guarantees.

| Workload | Baseline median | Epoch median | Median paired speedup |
| --- | ---: | ---: | ---: |
| Full cold replay | 2.219 s | 2.052 s | 1.067x |
| c9 ordered RUP, 1,408,137 hints | 0.344 s | 0.235 s | 1.501x |
| c8 ordered RUP, 1,338 hints | 0.425 ms | 0.342 ms | 1.399x |

Environment: CPython 3.14.7, macOS 27.0.1, arm64. The c8 measurement is too short
to support a strong performance inference. Full replay is dominated by unchanged
formula/geometry work, so its gain is modest. The kernel speedup is not the
end-to-end speedup, and neither describes integer multiplication runtime.

Rebenchmark without overwriting committed evidence:

```sh
python3 -I -O -B research/p111-rup-epochs-seed91/benchmark.py \
  --pairs 7 --output /tmp/p111-rup-benchmark.json
```

## Coverage, failure controls and limitations

[test_semantics.py](test_semantics.py) compares the candidate and frozen reference
against a separately written false-literal-set oracle. It exhausts all 21 ordered
clauses of width at most two over two variables, all root pairs and all proposed
clauses, with zero-to-two hints over root/self/missing IDs: 194,481 cases. Every
accepted nonempty prefix is extended with every zero-to-two-hint empty suffix:
78,260 cases. Eighteen additional controls exercise longer propagation, repeated
literals, stale epochs, tautologies, sparse clause IDs and diagnostic priority.
Truth tables independently check entailment of each accepted lemma. This is a
finite implementation audit, not a formal proof of the checker or full theorem.

[test_package.py](test_package.py) rejects seven altered predecessor files, both
altered proof payloads, a deliberately broken epoch reset, a falsified full
receipt and a preloaded unrelated checker module. A calibrated poisoned bytecode
cache is ignored in favor of authenticated source. A relocated minimal two-package layout with spaces in its path accepts
both equivalently recompressed proofs under isolated optimized Python. Pins bind
decoded LRAT bytes rather than gzip headers; all other predecessor files keep
their exact SHA-256 pins. [SOURCES.json](SOURCES.json) records the inventory.

This changes neither the archived P111 puncture/root order nor the mathematical
claims established by PR1097. It does not transfer those claims to a supplier's
different root order, prove the separate copy-cost floor, admit a physical word,
or discharge the selected construction's all-size/compiler, realization, hosting,
precision, recovery and analytic assumptions. Native LRAT and full selected
frontier replays are not rerun here because neither construction nor proof
payload changes. No Linux CI result or independent human review is claimed.

[CLAIM.json](CLAIM.json) records the seed, three candidates, overlap check,
bounded scope and local claim. No pinned coordination issue existed at entry.
See [NOTICE.md](NOTICE.md) for predecessor credit and substantial AI assistance.
