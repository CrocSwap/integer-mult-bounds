# Independent audit of PR2634's resumable 20-cycle census, and completion of the (10,10) exclusion at L = 20

Contributor: **Nicholas Stone** (Kimi agent; substantial AI assistance in scoping,
implementation, verification and writing; no independent human review claimed).
No kappa, supplier, certificate or selected-frontier change. Base: main
`b4560d9e7216f72b73c5aa940ac099c05e33ccf9`, priority revision 5.
Claim: https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18953986

## Scope

An independent audit (own engine, no shared code) of
[PR2634](https://github.com/CrocSwap/integer-mult-bounds/pull/2634) at head
`e2f30d93efbef5658334072aa855aa95e795e394`
(`research/universal-f7-singleton-l20-seed06704c39`), plus the completion of
its resumable restricted-growth simple-20-cycle census at `n = 7`, split
`(10,10)`, collision budget `e_ex + b_ex <= 27`, which stood at 11/15 shards
(798,901,058 nodes, 67,674,177 simple cycles, zero universal words).

The census scope is unchanged: canonical (restricted-growth) restored words of
length 20 whose 20 prefix parity states are distinct. Words with repeated
boundary states (`|P|` in `{17,18,19}`) remain outside this census, exactly as
recorded in the audited package. Nothing here bears on those open splits.

## Audit result: all checked statements reproduce exactly

1. **Author's own checks re-run at the pinned head**:
   `verify.py` → `PASS_F7_L20_VERIFY ... L20=120 L22=126`;
   `independent.py` → `PASS_F7_L20_INDEPENDENT`;
   `test_engine.py` → 14 tests OK.
2. **Independent engine** (`f7_census.c`, C, written from the mathematical
   statement of the scope and the three proved-necessary prunes — multiplicity
   room, self-avoidance justified by `|P| = L = 20`, and the split-identity
   collision budget `45 + 45 - 63 = 27`; exact 128-bit masks):
   reproduces **all 11 completed shard counts exactly**, including the heavy
   shard `0102` at **798,901,031 nodes / 67,674,177 leaves / 0 hits**
   (20.1 s vs ~57 min for the reference Python engine, a ~170x rate
   difference with bitwise-identical counts).
3. **Mid-stream traversal agreement on new territory**: capped probes
   (`max_nodes = 5,000,000`, reference engine vs this engine) agree exactly on
   `0102` (5,000,001 / 418,619 / 0), `0123` (5,000,001 / 483,870 / 0),
   `01230` (5,000,001 / 483,870 / 0) and `01232` (5,000,001 / 450,641 / 0),
   covering the label-3 prefix region that no completed shard exercised.
4. **Auxiliary claims independently re-derived** (own formulation):
   the pinned 20-point cover of `F2^7` indeed satisfies `P + P = F2^7` (all
   128 masks) and has induced-degree histogram
   `[0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,2,2,2,2,3]` — six isolated vertices, so no
   closed walk spans it; the parity fact (restored ⇒ all label counts even ⇒
   even length, hence `L = 19` dead) re-derived and micro-checked at `n = 3`
   (restored words exist only at even lengths).

No discrepancy found in any checked statement of PR2634.

## New result: the (10,10) census is complete — zero universal words

The four remaining shards, run with the same independently written engine:

| Shard | Nodes | Simple 20-cycles | Universal words |
|---|---:|---:|---:|
| 0120 | 951,630,113 | 88,700,116 | 0 |
| 0121 | 552,149,367 | 50,308,509 | 0 |
| 0122 | 4 | 0 | 0 |
| 0123 | 4,002,528,537 | 390,465,512 | 0 |

Combined with the audited 11 shards:

| Census total (15/15 shards) | Value |
|---|---:|
| Nodes | **6,305,209,079** |
| Simple 20-cycles checked | **597,148,314** |
| Universal words | **0** |

**Conclusion (scoped):** no universal restored length-20 word with 20
distinct prefix states exists at `n = 7`. Within the PR943 prefix-walk model
this closes the `(10,10)` split at `L = 20`. Together with PR2542's
length-18 exclusion and the parity fact (odd lengths dead), the only
length-20 cases left open are words with repeated boundary states, splits
`(10,9)`, `(10,8)`, `(9,9)`, `(10,7)` as recorded in PR2634's open questions.
The recorded gap `20 <= f(7) <= 24` is unchanged: this is a finite exclusion
inside one split, not a bound on all length-20 words.

Internal consistency: the depth-5 sub-shards of `0123`
(803,327,055 + 502,126,395 + 413,775,220 + 5 + 2,283,299,882 nodes,
79,211,054 + 47,872,485 + 38,541,037 + 0 + 224,840,936 cycles) equal the
depth-4 totals up to exactly the 20 duplicated ancestor calls
(5 sub-shards x 4 shared prefix nodes), and the cycle counts match exactly.

## Reproduction

Requires a C compiler with `unsigned __int128` (GCC/Clang); no third-party
dependencies. Reference replay of the audited package requires Python 3.12,
standard library only.

```sh
# This package: full 15-shard census (~3 min on Apple Silicon)
cc -O2 -o f7_census research/universal-f7-singleton-l20-census-complete-seedfd938f30/f7_census.c
./f7_census        # prints one SHARD line per shard; hits.txt stays empty

# Cross-validation replay (audited package, at PR2634 head e2f30d93)
python3 -I -B research/universal-f7-singleton-l20-seed06704c39/verify.py
python3 -I -B research/universal-f7-singleton-l20-seed06704c39/independent.py
python3 -I -B research/universal-f7-singleton-l20-seed06704c39/test_engine.py
```

Expected: per-shard `(nodes, leaves, hits)` exactly as in
[AUDIT-RESULT.json](AUDIT-RESULT.json); total 6,305,209,079 nodes,
597,148,314 cycles, 0 universal words. Observed environment: Apple clang
21.0.0, Darwin 25.5.0 arm64, Python 3.12.15.

## Open next questions

1. **Do repeated-state length-20 words (splits `(10,9)`, `(10,8)`, `(9,9)`,
   `(10,7)`) admit a universal word?** This is now the *only* open family at
   `L = 20`; settling it (either way) decides whether the census step-up from
   PR2542 moves to `L = 22`. First step: extend this exact enumeration with
   multiset collision semantics — revisit bookkeeping per boundary state with
   per-split budgets from `lemma_a_table` rows — sharded the same way.
   Blocker: revisit-aware prunes are weaker (self-avoidance is unavailable),
   so per-split node counts will be substantially larger; the budget
   derivation per split must be redone, not copied from the `(10,10)` value.
2. **Is the simple `(11,11)` census at `L = 22` feasible with the same
   method?** First step: derive the `(11,11)` collision budget
   (`C(11,2)+C(11,2)-63 = 47`) and probe one depth-5 shard for its node rate.
   Blocker: expected tree size grows by roughly an order of magnitude over
   `L = 20`; likely needs the shard-parallel run rather than a single process.

## Credit

PR943 model and first exact values: Ross Richardson
(`research/universal-connector-boundary`). Pinned five/six-source record:
Douglas Colkitt (`research/universal-connector-six-source`, PR1185).
Length-18 exclusion and the restricted-growth cycle census design: Aaron Wang
with opencode (PR2542). The audited 11-shard checkpoint, the parity closure
of `L = 19`, the template lemmas, the cover witnesses and the search
campaign: Aaron Wang with opencode (PR2634). This package contributes only
the independent audit and the completion of the remaining four shards;
no result of PR2634 is restated as new here. Apache-2.0.
