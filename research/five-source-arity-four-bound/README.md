# Five-source arity-four connector bound

**Scoped negative result; no supplier or kappa change.** Add one operation
family to the five-source paired-readout connector: a call

```text
Q_r: z += sum_{j != r} B_j x_j       (r in {0,1,2,3,4})
```

Each `Q_r` is one dispatched connector event, and its four source-map additions
are charged individually. The original singleton `B_j` source calls and
`A_i: y_i += A_i z` readouts remain available. Sources and coefficients are
read-only, `z` is arbitrary dirty state restored at the end, outputs are
unobserved until completion, and each of the 31 nonzero output masks is
required. No new frame, copy, extra connector, direct product call or free
arithmetic is included.

Under the explicit uniform ledger of one unit per event dispatch and one unit
per source-map or output-map addition, **every schedule that uses at least one
arity-four call costs at least 149 units**. The unchanged alphabet has exact
minimum 74 unit-price complete queries from the pinned predecessor; under this
ledger that is 148 units. Thus this charged extension cannot improve the
five-source all-mask batch. This is a bound on the stated local ledger, not on
every implementation cost model or a complete multiplication supplier.

## Proof

Project the source-side events of a schedule to vectors in `F_2^5`. A singleton
event has weight one; `Q_r` has vector `11111 XOR e_r`, of weight four. Let
`k=s+m` be the number of source events, where `m` is the number of `Q` events,
and let `W=s+4m=k+3m` count their constituent source-map additions. Restoration
for arbitrary dirty connector state and independent source terms forces each
source's total multiplicity to be even, so `W` is even.

Let `P` be the set of distinct source-prefix vectors at event boundaries and
`D={p XOR q : p,q in P}`. A pair of output readouts realizes only a mask in
`D`. Every nonzero output row needs an even positive number of readouts. If a
mask is missing from `D`, its row needs at least four readouts. If `M` of the
31 nonzero masks are missing, the total output-readout count is therefore at
least `62+2M`. Since a closed `k`-event path has at most `k` distinct
prefixes, `|D \\ {0}| <= choose(k,2)`, hence
`M >= max(0,31-choose(k,2))`.

The charged total is

```text
C = (k dispatches + W source additions) + 2 R output-readout units
  >= 124 + 2k + 3m + 4M.
```

The only delicate case is `m=1, k=9`. Here `W=12`, and the exact finite
census below gives `|D| <= 26`, so `M >= 6` and `C >= 169`. For `m=1` and
`k>=11`, parity gives odd `k`, so `C >= 124+2*11+3 = 149`. For `m=2`, `W`
even forces even `k`; the pair-count bound gives `k>=10`, so `C>=150`. For
`m>=3, k>=9` gives `C>=151`. For `k<=8`, `M>=31-choose(k,2)` gives `C>=155`
already at the weakest case `k=8,m=1`, with smaller `k` or larger `m` only
increasing the bound. Therefore every schedule using the new family costs
at least 149.

For `m=1,k=9`, rotate the closed event cycle so the arity-four event is last;
this translates all prefix vectors and preserves their pairwise differences.
Relabel the five sources so that event toggles `01111`. The eight singleton
events before it must then have XOR `01111`. The verifier exhausts all 23,184
such ordered words, computes every pairwise prefix difference, and finds a
maximum `D` size of 26 (including zero). The first maximizing word is
`01020434`; its missing nonzero masks are `01010, 01011, 10010, 10011, 11010,
11011`. Its histogram and ordered-census SHA-256 are pinned by the verifier.
A positive control checks the predecessor's twelve-singleton path and obtains
all 32 masks.

The call's implementation charge is explicit: four constituent source-map
additions plus its own dispatch. Any routing, frame, program-storage or
additional scratch cost is outside this ledger and cannot be treated as free
in a physical caller. A fused implementation that performs fewer than four
charged additions would be a different premise.

## Reproduce

From the repository root:

```sh
python3 -I -O -B research/five-source-arity-four-bound/verify.py
python3 scripts/research_package.py --package research/five-source-arity-four-bound --check-only
```

The first card control was also run from the pinned base:

```sh
python3 -B research/universal-connector-boundary/verify.py
```

## Scope and overlap

The broad card is refined to the five-source arity-four family. Pair-source
and trio extensions, connector frames, and the original all-singleton word
have separate retained results. Open PR [#2249](https://github.com/CrocSwap/integer-mult-bounds/pull/2249)
claims a charged arity-four-through-six floor for six sources; this result is
the five-source complement case. Open PR [#3586](https://github.com/CrocSwap/integer-mult-bounds/pull/3586)
claims a one-source/one-output direct product call, which is a different
operation boundary. These open PR claims were not independently verified here.
The contemporaneous PR and handoff overlap check is retained in
[OVERLAP.json](OVERLAP.json); it is not a novelty certificate.

The exact selected result at the base remains the maintainer-reviewed
conditional finite construction `κ = 836330098538459/500000000000000000`
(`0.001672660197076918`), reproduced by `make frontier1094-verify`. This work
does not depend on that cold replay and did not rerun it. The selected record,
review and source manifest were inspected; their exact paths and certificate
binding are recorded in the session handoff.

## Open next questions

Does this family improve the complete bill for a concrete five-source caller
with nonuniform source-map and dispatch costs? The answer could change which
four-source subset is worth fusing. First bind a real caller's five source
tariffs and word-storage/dispatch costs, then enumerate only the surviving
prefix profiles. No such eligible caller or implementation contract is
identified here; without one, further tariff optimization is not justified.

## Credit

This scope is based on Ross Richardson's five-source universal connector
boundary (#943/#934 lineage) and Cinna Davis's six-source high-arity connector
floor (#2249). Their source claims and limits are preserved above. Prepared by
OpenAI Codex (macbook-09) with substantial AI assistance. No independent human
review, proof-assistant check, hosted CI pass, supplier admission or new kappa
is claimed. New package content is Apache-2.0.
