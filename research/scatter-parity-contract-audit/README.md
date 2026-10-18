# Scatter schema boundary: the exact parity contract and what the simple-support guard rejects

**Boundary audit; no new κ.** This is an independent answer to the decision
PR2977 and PR2992 leave open: which scatter schema should the successor checker
and exporter enforce? For the frozen selected sources, the symbolic checker's
scatter operator (one XOR per list occurrence, `xcheck_p.py`) and the record
exporter's scatter operator (one ADD per row membership, `export_records.py`)
agree on a row **exactly when every positive multiplicity in that row is odd**.
The proposed simple-support guard (`simple-scatter-v1`, every index distinct) is
**sound but strictly stronger**: it never admits a divergent row, and on an
exhaustive small domain it rejects 296 rows that agree, the smallest being
`[0, 0, 0]`. The selected producer's rows are simple supports, so either
contract preserves the selected word bytes. No supplier, frontier or κ change.

```sh
python3 -B research/scatter-parity-contract-audit/verify.py
```

Expected:

```text
PASS_SCATTER_PARITY_CONTRACT domain=1365 divergent=1004 simple_accept=65 exact_accept=361 over_rejected=296 term_mismatch=1300 mutant=divergent selected_rows=111 selected_terms=527 selected_simple=true guard=sufficient_not_necessary coefficient_unchanged=true
```

Python 3.10+. The frozen sources are read and line-bound, not executed; the
pinned tuned word is bound by SHA-256. No C++ or native backend is run.

## The contract, exactly

Fix one target `t` and one retained total `k`, and let `m >= 0` be the
multiplicity of `k` in row `t`.

- The checker runs `for k in row: val[v + t] ^= copies[k]`, so the coefficient
  of `copies[k]` in the target is `m mod 2`.
- The exporter runs `if k in row: rec.append(...)` once per `(k, t)` pair, so the
  emitted coefficient is `[m > 0]`.

Over F2 these are equal for every `m` iff `m` is odd or zero. Hence:

> The two scatter operators agree on a whole word iff every positive
> multiplicity in every scatter row is odd.

The proposed simple-support guard requires `m <= 1`, which is the `m in {0,1}`
special case. It is therefore sufficient for agreement but not necessary.

## Exhaustive domain and guard comparison

All 1,365 tuples of length 0..5 over four retained-total indices, classified by
an independent implementation (multiset parity versus set membership):

| class | rows |
|---|---:|
| domain | 1,365 |
| divergent (parity ≠ membership) | 1,004 |
| simple supports (guard accept) | 65 |
| odd-multiplicity admissible (exact agreement) | 361 |
| agreeing rows the simple guard rejects | 296 |
| rows whose occurrence count differs from the emitted ADD count | 1,300 |

`simple ⊆ exact` and `divergent ∩ simple = ∅` hold on the whole domain, so the
guard is sound. The smallest agreeing row it rejects is `[0, 0, 0]`
(parity `1`, membership `1`). The PR2977 mutant `[4,5,6,7,8,0,0]` has an even
positive multiplicity, diverges, and is rejected by both contracts; replacing
the occurrence loop by membership makes it agree, which isolates the divergence
to the loop rather than to the index range.

**Accounting consequence.** The checker reports
`scatter_terms = sum(len(r) for r in scatter)` (occurrences), while the exporter
emits one ADD per membership. The two counts coincide on simple supports
(527 = 527 on the selected word) but differ on every row with a repeated index,
including the 296 agreeing rows. If a future schema admits odd multiplicities,
it must also say which count is authoritative for cost or receipt purposes.

## Where the contract has to live

- **Generator.** `decoder_rows` in `gen_p3.py` returns `list(C)` from
  `itertools.combinations(range(len(cvals)), k)`, so its rows are strictly
  ascending and duplicate-free; `pwordl.build` serializes them unchanged.
- **Tuner.** `apply.py` rewrites only `A` and rebuilds `C`
  (`w["A"] = newA`, `w["C"] = wlib.rebuild_C(w)`); the string `scatter` does not
  occur in it, so the tuned word cannot acquire a repeated row.
- **Checker and exporter.** The exporter takes the word path as `argv[1]` and
  the checker accepts arbitrary in-range rows, so an arbitrary word JSON is the
  effective boundary. That is consistent with enforcing the schema at both
  entry points (PR2992) rather than only at the generator.

The pinned selected word has 111 simple, ascending rows over nine retained
totals with 527 terms; its occurrence count equals its membership count. Both
candidate contracts therefore accept it byte-identically.

## Reproduce

From the repository root:

```sh
python3 -B research/scatter-parity-contract-audit/verify.py
python3 scripts/research_package.py --package research/scatter-parity-contract-audit --check-only
python3.12 scripts/research_package.py --package research/scatter-parity-contract-audit
```

## Open next questions

1. **Decide the schema and the authoritative count.** If the successor keeps
   simple supports, document uniqueness as a producer restriction rather than a
   semantic necessity; if multiplicity is meaningful, the exact minimal
   contract is odd-multiplicity admissibility, and the schema should fix whether
   `scatter_terms` (occurrences) or the emitted ADD count (membership) is
   authoritative. First step: add the `[0,0,0]` fixture and the mutant to the
   successor's checker/exporter sequence; blocked by the adoption review of
   PR2977/PR2992, not by arithmetic.
2. **Gate operand lists.** The checker already rejects repeated gate operands
   (`len(set(regs)) == len(regs)`), and the exporter emits one ADD per source, so
   accepted words cannot diverge there. The exporter itself does not enforce
   distinctness; a schema validator could cover both fields uniformly. First
   step: extend the guard test to the gate lists; no known divergent word exists.
3. **Native acceptance of an odd-multiplicity row.** Does the native column
   checker accept an agreeing row with an odd multiplicity ≥ 3 (which the simple
   guard rejects)? This audit does not run the native backend. First step: run
   PR2977's optional native replay on a `[0,0,0]` variant; blocked by the C++17
   toolchain and by the fact that the synthetic word is outside the selected
   producer.

## Scope, credit and verification limits

The counterexample, the prior guard and the boundary handoff are Nick Petalas's
([@petalas](https://github.com/petalas)) PR2977 and
[discussion #2976](https://github.com/CrocSwap/integer-mult-bounds/discussions/2976);
the opt-in enforcement at both entry points is Arham Tahir's
([@Arham-Tahir64](https://github.com/Arham-Tahir64)) PR2992. The exporter is
Dylan Crow's, and the selected word and checker retain the eumemic /
DreamingOfClouds / PR589 lineage. This package adds the exact agreement
characterisation as a checked domain statement, the guard-versus-agreement
comparison, the producer row-space check and the term-count observation; it
claims none of the predecessors' work as new.

Base `836b19bfa309ceafbc8ee32a15e8c4b10dde7e11`, priority revision 6. The frozen
sources and selected word are read, not executed; the audit is finite and
source-bound, not a native, compiler or formal-kernel result. Prepared by Kumagi
([@kumagi](https://github.com/kumagi)) with substantial AI assistance (DeepSeek
V4.1 Flash in the OpenCode harness). No independent human review is claimed.
Apache-2.0; predecessor attribution retained.
