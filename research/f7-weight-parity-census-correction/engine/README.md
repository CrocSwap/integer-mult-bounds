# Corrected Hamming-weight parity census

This directory repairs the collision-group mismatch in the frozen predecessor
engines `audit-f7/f7_census.c` and `session2/agent-a/f7_census_revisit.c`.
Those sources are unchanged. The predecessors' fixed collision budgets were
proved for Hamming-weight parity but applied to coordinate bit 0 by default.
Consequently their zero-hit result did not establish completeness. This
implementation uses Hamming-weight parity throughout.

The implementation retains Nicholas Stone's restricted-growth restored-word
scope and prefix-walk model, building on the PR2634 work credited to Ross
Richardson and Aaron Wang/opencode. Implementation and review involved
substantial OpenAI Codex assistance.

## Scope and correctness argument

A restored word of even length L uses each of N labels a positive even number
of times. Its prefix walk is `q_0=0`, `q_{i+1}=q_i XOR (1<<word[i])`, with
`q_L=0`. The distinct prefix states `q_0,...,q_{L-1}` form P; the word is
universal exactly when `P+P` is every N-bit mask. E/O partition P by Hamming
weight parity, which is also time-index parity. A run targets an exact split
`(|E|,|O|)=(s,t)` and permits revisits. Restricted-growth label sequences
choose exactly one representative of each coordinate-relabeling orbit.
Universality and the split are invariant under this relabeling.

For a universal word, all `2^(N-1)-1` nonzero even masks must occur in EE or
OO. With separate supports for the two families, the total excess therefore
satisfies

```
(C(s,2)-|supp EE|) + (C(t,2)-|supp OO|)
    <= C(s,2)+C(t,2)-(2^(N-1)-1).
```

All `2^(N-1)` odd masks must occur in EO, so its excess equals
`s*t-2^(N-1)`. Both excesses are nondecreasing as new distinct states are
added. Within an addition the XORs with existing distinct states are distinct,
because translation is injective. Counting their intersection with the old
support gives the exact added excess. A revisit changes neither pairs nor
excesses. Exceeding either final necessary budget is thus a sound subtree
prune. Negative necessary budgets prove the split impossible and skip it.

The remaining prunes are also necessary: insufficient remaining positions to
make current odd multiplicities even and introduce missing labels twice;
per-label multiplicity at most `L-2*(N-1)`; distinct-set size upper bounds;
and inability to reach the requested sizes with remaining slots. The final
step admits only `q_L=0` and does not add another prefix state. A leaf checks
closure, all N labels introduced, even multiplicities, and the exact split.
Universality then checks the union `EE | OO | EO | {0}` covers all masks.

## Results and count semantics

`SUMMARIES.json` records the final source hash, compiler/environment, commands,
and six complete run receipts. All five required L20 splits and the L18 (9,9)
repair run finished with zero hits. Every run enabled both proved necessary
budgets. The independent validator's evidence is maintained separately by
its owner; the small oracle here is auxiliary evidence only.

`candidate_restored_leaves` counts restored leaves surviving the enabled
budget prunes. It is **not** the count of all restored words at that split.
All six production runs have zero such leaves because the necessary budgets
already eliminate every branch before a restored leaf. Prune counters count
rejected edges, not the number of restored descendants removed.
`all_restored_leaves` is null when any budget is enabled or a run aborts. With
`--no-budgets` and `complete=true`, it is the exact restored-word count in the
requested canonical split/shards. A zero-hit completed sound-pruned run is a
complete exclusion of universality even though it does not count all restored
leaves.

The implementation's node count is one per entered recursive call. It omits
nonclosing final steps, unlike the reference engine, and enables the additional
odd budget. Its node counts therefore need not reproduce predecessor counts.

## Replay

From this directory, choose a new output directory (output files are created
exclusively and existing files are never overwritten):

```sh
cc -O3 -Wall -Wextra -Werror -std=c11 -DN=7 -DL=20 corrected_census.c -o census_l20
mkdir replay
./census_l20 10,10 --hits replay/l20_10_10.hits --json replay/l20_10_10.json
./census_l20 10,9  --hits replay/l20_10_9.hits  --json replay/l20_10_9.json
./census_l20 10,8  --hits replay/l20_10_8.hits  --json replay/l20_10_8.json
./census_l20 9,9   --hits replay/l20_9_9.hits   --json replay/l20_9_9.json
./census_l20 10,7  --hits replay/l20_10_7.hits  --json replay/l20_10_7.json
cc -O3 -Wall -Wextra -Werror -std=c11 -DN=7 -DL=18 corrected_census.c -o census_l18
./census_l18 9,9 --hits replay/l18_9_9.hits --json replay/l18_9_9.json
python3 verify_gates.py
```

Compile-time support is restricted to `1<=N<=7` and even `2<=L<=20`, keeping
masks and all full-search counters within their exact types. Runtime CLI:

```
census s,t --hits PATH [--json PATH] [--cap N]
       [--no-budgets|--no-even-budget|--no-odd-budget] [PREFIX[:CAP]...]
```

With no prefix the empty-prefix run covers the entire canonical scope. `-`
also means empty prefix. Explicit prefixes must be canonical restricted-growth
sequences over the compiled label set. Overlapping prefixes are rejected to
prevent double counting. A global cap applies independently to each shard;
a positive per-prefix cap overrides it. Zero means unlimited. Cap exhaustion
sets `aborted=true`, `complete=false`, and exits 2 without claiming the remaining
shards complete. Input and output-I/O errors exit 1. Accept a run as complete
only when the process exits 0 and the JSON says `complete=true`.

The auxiliary `verify_gates.py` brute-forces all full words for n3L6, n3L8,
and n4L8, then independently canonicalizes and recomputes prefix coverage.
For every ordered split it compares exact hit sets with both default budgets
and with budgets off, and compares all restored leaves with budgets off.
Its recorded totals are respectively restored/universal `15/10`, `210/182`,
and `105/26`. It uses Python assertions, so run it normally, without `-O`.

## Open next questions

- Independently replay this corrected package with the separately implemented
  validator and retain its full source/output evidence before treating the
  exclusions as a reviewed computation.
- Maintain the distinction between these finite word exclusions and the full
  multiplication theorem. The parent package supplies the split reduction,
  padding argument, and the statement of resulting bounds.
