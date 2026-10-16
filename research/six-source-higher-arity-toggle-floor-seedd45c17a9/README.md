# Six-source additive-cost floor for high-arity connector toggles

**Scoped negative result; no supplier or new κ.** Extending the six-source universal dirty-connector alphabet with one source-hyperedge operation for every subset of size four through six cannot improve its full 63-mask batch when every source tap is charged. The exact optimistic full-batch Pareto point remains 140 total queries and 142 total additions. The known attaining word uses 14 source calls and 16 source additions. The argument closes the entire arity-4..6 family, including schedules that use more than two output readouts, without enumerating its words.

## Assignment and changed scope

- Cycle 43 seed: `d45c17a9abef1858e6b314d2bb66be28`; track `recursive-interfaces`; task `connector-alphabet-change`; priority revision 4.
- Base: `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`.
- Selected record SHA-256: `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.
- Catalogue SHA-256: `d46eb6d5b3e279428753d770653663fbdf1063e55c255ea073d768f344927ef7`.
- The broad card is refined to a new parametrized operation family, `H_S: z += sum(B_j x_j)` for `4 <= |S| <= 6`, on the fixed six-source, all-63-output instance. It keeps read-only sources, arbitrary dirty connector contents, complete restoration, and separate output readouts. Its most favorable full price is one dispatch plus `|S|` charged source additions; any routing, frame, or implementation cost adds to this bill.

This is a changed connector contract relative to the selector's broader starting suggestions. Earlier work covers the pair-source DUO witness (#2128), a fixed one-TRIO profile (#2146), and the DUO full-batch optimum (#2156). This result derives an all-arity floor for source subsets of size four through six. It neither claims those earlier constructions nor independently replays their searches.

## Exact lower bound

A source word is a closed walk `q_0,...,q_k` in `F2^6`; a hyperedge call on `S` changes `q` by the indicator vector of `S`. Let `P` be the distinct prefix set and let `D(P)={a+b:a,b in P}`. A mask in `D(P)` can be realized with two output readouts. The exact group basis result `r[(C2)^6]=14` (Volodymyr Gavrylkiv, *Bases in Dihedral and Boolean Groups*, Journal of Integer Sequences 20 (2017), Article 17.8.1, Table 3) implies that a prefix set of size at most 13 cannot cover every mask.

The lower bound must also allow outputs with more than two readouts. Each output needs an even number of `A_i` reads to cancel its arbitrary dirty-connector contribution. A nonzero output needs at least two reads; if its mask is missing from `D(P)`, two reads cannot realize it, so it needs at least four. If `M` of the 63 nonzero masks are missing, the total output-read count is `R >= 126 + 2M`.

Now split by the number `k` of source-call dispatches. If `k >= 14`, then `k+R >= 140`. If `k` is 12 or 13, `|P| <= k <= 13`, so the basis-size result forces `M >= 1`; hence `k+R >= k+128 >= 140`. If `k <= 11`, at most `binom(k,2)` nonzero pair differences occur, so `M >= 63-binomial(k,2)`. Thus

```text
k + R >= k + 126 + 2(63 - binomial(k,2)) >= 153   for 0 <= k <= 11.
```

Therefore **every schedule, including those with four or more readouts on some outputs, has at least 140 total queries**. This case split depends on source-prefix geometry, not on whether one source call toggles one, two, or six sources.

For the source-add charge, expand every hyperedge step `S` into `|S|` singleton toggles in any fixed order. The expanded path retains every original boundary, so all original output-readout placements remain valid. It is a singleton source word of length `W=sum |S|`; the pinned exact six-source result `f(6)=16` in `research/universal-connector-six-source` gives `W >= 16`. Also `R >= 126`, hence total additions `W+R >= 142`.

The most favorable complete price is therefore

```text
queries Q >= 140
source additions W >= 16
output readouts R >= 126
total additions W+R >= 142
price >= 140 o + 142 p, for o,p >= 0
```

Here `o` is the fully charged dispatch/entry-exit cost and `p` the per-add cost. Any routing, frame, or implementation surcharge only increases the bill. The 14-step DUO witness from PR #2128 attains `Q=140`, `W=16`, and `R=126`, so it reaches `(140,142)`. Its witness is attributed to that PR and pinned in [EXTERNAL-PINS.json](EXTERNAL-PINS.json).

## Verification

The local verifier checks the cited six-source census receipt, the exact pinned 14-step witness and its all-mask difference coverage, expansion of every six-bit source subset, the complete 63-row dirty-connector schedule, reverse restoration, the all-k query-floor case split, and three failure controls. The six-source census prerequisite was also run locally under CPython 3.14.7; its output is recorded in `RESULT.json`.

From repository root:

```sh
python3 -I -O -B research/six-source-higher-arity-toggle-floor-seedd45c17a9/verify.py
python3 scripts/research_package.py --package research/six-source-higher-arity-toggle-floor-seedd45c17a9 --check-only
python3.12 scripts/research_package.py --package research/six-source-higher-arity-toggle-floor-seedd45c17a9
```

## Limits

This excludes an improvement only for source-hyperedge calls whose fully charged source-add price is at least the sum of their constituent source taps, with the six-source universal dirty-connector contract and 63 separate outputs fixed. It does not cover subadditive physical fusion, mutable sources, new output operations, different target families, supplier placement, or a multiplication exponent. The result is an abstract interface bound, not physical admission into the selected supplier.

## Open next questions

**Question:** Can a concrete selected-supplier interface realize any source-hyperedge of arity at least four with a total cost strictly below its constituent source reads while preserving arbitrary dirty-state restoration? First step: name one existing supplier frame, compile one such hyperedge into literal native operations, and charge its complete route/frame/precision bill. It matters because only a physically realizable subadditive charge escapes the floor proved here. The present six-source abstract connector has no admitted supplier realization, which is the blocker.

## Credit

The exact `f(6)=16` source-word result is predecessor work in `research/universal-connector-six-source`. The 14-call/16-add upper witness is Aaron Wang/Navinor's PR #2128. PR #2156 provides the closely related DUO-domain global optimum and credits Gavrylkiv for the group basis value. PR #2146 tests one fixed six-source TRIO profile. Prepared by Cinna Davis with substantial OpenAI Codex assistance; this package adds the all-arity source-expansion lower bound and full charged interpretation. No independent human review is claimed.
