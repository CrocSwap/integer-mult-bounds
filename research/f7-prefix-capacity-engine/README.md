# Opt-in matching capacity in the corrected word-census engine

**Scoped maintained-engine integration and bounded runtime decision; no new kappa.** This source-bound successor applies Ali Romman's PR5001 completion predicate inside Nick Petalas's maintained union-support census, which descends from Nicholas Stone's parity-corrected census. Frozen predecessor packages and receipts remain unchanged. The selected conditional `60403/20000000` is not a result of this task.

## Caller and change

The existing engine is not globally a simple-walk census: it admits repeated prefix vertices when the target Hamming-weight split permits them. Its exact target `S=T=L/2` is a simple-walk caller. At time `d`, a simple prefix has one distinct vertex at each time `0,...,d`. For a proposed nonclosing vertex at time `d+1`, the existing `ns + rem_even[d] >= S` and `nt + rem_odd[d] >= T` tests count every still-available position of the corresponding time parity. A repeated vertex fails its parity's inequality immediately, because it contributes no new distinct vertex while consuming one of the exactly `L/2` positions. By induction, every recursive prefix reached in this target split is simple. The final edge `q_L=0` is already handled separately and adds no prefix vertex.

`--prefix-capacity` requests the new predicate. It becomes active only for `N>=2`, even `4<=L<=2^N`, and `S=T=L/2`. Other target splits retain the original repeat-aware traversal with the predicate bypassed; JSON distinguishes requested and enabled. The optional predicate runs after the existing cheap multiplicity test and before extending the prefix. Each coordinate omission uses the actual classes of the functional with every coefficient one except the omitted coordinate, and accepts any final functional split admitted by PR5001. The Hamming-weight target split is never substituted for those functional splits. At `r=0` the predicate checks the closing edge directly; otherwise `crossing+r+1` includes that edge.

`vendor/union_census.c` is the exact existing engine at the pinned base, and `census.c` is its maintained successor entry point. `DELTA.diff` records every change. The default remains off; existing traversal, output file creation, shard/cap behavior, scientific report fields and hit format are retained. JSON adds requested/enabled status and a capacity-prune counter. The new source does not reinterpret the predecessor's `all_restored_leaves` or budget semantics.

## Exact evidence

`RESULT.json` records five complete small domains, each with all budgets disabled and with the unchanged default budgets. A temporary instrument at the real restored-leaf boundary compares full word `Counter`s for the pinned engine, successor off and successor on. Universal hit `Counter`s and scientific counts agree too. Default-off reports also agree in every non-timing predecessor field. The separately implemented firing census in `vendor/firing_census.c` supplies an independent complete simple restored-word multiset, filtered to the corrected engine's all-label scope. It is not used as a replacement engine or imported receipt.

| Domain | All restored leaves | Universal hits | No-budget nodes off / on | Default nodes off / on |
| --- | ---: | ---: | ---: | ---: |
| `n=2,L=4` | 1 | 1 | 5 / 5 | 5 / 5 |
| `n=3,L=6` | 4 | 4 | 16 / 16 | 16 / 16 |
| `n=4,L=8` | 27 | 22 | 91 / 91 | 81 / 81 |
| `n=4,L=10` | 110 | 110 | 566 / 534 | 566 / 534 |
| `n=5,L=12` | 3,381 | 828 | 17,360 / 16,765 | 8,401 / 8,278 |

The first PR5001 strict fixture, `010210`, omitted coordinate 0, remains rejected by the C kernel. In this actual engine it is already rejected by the earlier multiplicity/all-label test, illustrating why a theorem-level strict gain need not become an engine gain. The kernel agrees with PR5001's exact outer split set on all 436 prefix/omission pairs at `(4,8)`. Positive descendant completions reject three deliberate semantic mutations: the wrong omitted-coordinate functional (`010201`, omit 0), dropping the final edge from the crossing bound (`010201`, omit 1), and forcing a fixed half split (`010213`, omit 1). Both preserving and crossing closures pass. The source's unbalanced functional-completion control `0102132`, omit 1, lies in the checked prefix family. A repeat-capable weight target `(4,3)` retains all 18 restored leaves and bypasses capacity.

## Runtime decision

`TIMINGS.json` is local process-inclusive wall-time evidence: five samples per setting, fresh exclusive report/hit files, no leaf instrumentation, compilation excluded, no-budget complete searches. Samples were globally serialized on macOS 27.0.1 arm64, CPython 3.12.14, Apple clang 21.0.0, `-O2 -Wall -Wextra -Werror -std=c11`. The `(5,12)` median rose from **4.30 ms to 6.44 ms (1.50x)** despite 3.43% fewer nodes. The other medians are roughly 2–3 ms and dominated by process startup; their ratios do not establish a speedup. The bounded decision is to **retain opt-in status**. These short samples neither predict a seven-label production runtime nor justify another census.

## Reproduce

A C11 compiler supporting `unsigned __int128` and CPython 3.12 are required. The direct verifier needs no Git or network; the registered metadata checker uses repository history.

```sh
python3.12 -I -W error -B research/f7-prefix-capacity-engine/verify.py
python3.12 -I -W error -O -B research/f7-prefix-capacity-engine/verify.py
python3.12 -B scripts/research_package.py --package research/f7-prefix-capacity-engine --check-only
cc -O2 -Wall -Wextra -Werror -std=c11 -DN=5 -DL=12 research/f7-prefix-capacity-engine/census.c -o /tmp/census-capacity
# Choose new output paths; existing paths are never overwritten.
/tmp/census-capacity 6,6 --prefix-capacity --no-budgets --hits /tmp/new-capacity.hits --json /tmp/new-capacity.json
```

Expected direct marker: `PASS_F7_PREFIX_CAPACITY_ENGINE`. `--emit-receipt` prints regenerated deterministic evidence; ordinary replay compares it without modifying the receipt. `--timings` prints new local timing evidence, which is deliberately not a CI performance threshold. Each subprocess has an eight-second timeout and registered commands have a thirty-second bound. No seven-label run, full historical suite, Lean build, formal proof-kernel review or selected cold replay was performed.

The new check's observable contract is exact restored/accepted leaf multiplicity and report preservation at the real engine boundary. Credible regressions are an incorrect functional, omitted closing edge, or fixed-half substitution, each witnessed by a lost valid completion. PR5001's theorem tests do not exercise this engine or its split gate, so this package owns that integration boundary. Temporary instrumentation and a same-translation-unit kernel probe need no production export, injection option or test-only flag.

## Open next questions

1. Can an incrementally maintained version make the predicate worthwhile in a named larger simple-split shard? First profile the per-prefix work under a separately budgeted experiment; avoid default enablement from node reduction alone. No larger runtime evidence is supplied here.
2. A repeat-capable target cannot directly call PR5001. A different sound repeat-aware capacity theorem would be required before expanding the gate; the current implementation deliberately bypasses those calls.

## Sources and credit

Base: `f259dabc7d70e0db8d6d36bfda888f008bbfecc1`, priority revision 7. `SOURCES.json` pins the exact public bytes, paths and retained exports; PR5001 head `fe3226ea4e36469f43c6b116c5b98cc221a9b1af` is already an ancestor of this base. The union engine was introduced at `e09a08b5f85e648be373bece1b6ea1265d5ea8fa`; its unchanged source export preserves the full notices. The package's only external executable input is PR5001's `verify.py`, used only for its existing split function, not its historical traversal or proof replay.

Prepared for JoyboyBrian with substantial OpenAI Codex assistance. Credit: Ali Romman (PR5001/PR4992), Nick Petalas (PR4894 matching balance, union-support census), Mihir Srivastava (PR4907 handoff), Ross Richardson (PR943 singleton-prefix model), Nicholas Stone (PR2973 parity correction), Aaron Wang/opencode (retained word census), and Ryanson Jonathan with Claude Code assistance (independent firing census). New work and retained source are Apache-2.0. No independent human review, universal obstruction, complete multiplication theorem or new kappa is claimed.
