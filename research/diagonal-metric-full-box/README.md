# Which diagonal rational metrics retain every anchor row?

For positive rational d, write d=2^k u with u odd at2. For every rational
three-column P with nonempty original canonical ties, the factorization
(P,Q=P diag(1,d,1)) has a full retained directed sub-anchor box **if and only
if k is even and u is congruent to1 modulo4** (odd denominator interpreted
by its inverse). This includes nonsquares such as5, so rational Gram
isometry is not the criterion.

[PROOF.md](PROOF.md) proves exact original-anchor invariance under dual
power-of-two column scaling, the positive weighted coloring construction,
and counterexample families covering every complementary metric. For d2,
P=((1,0,1),(1,1,-1),(1,-1,-1)) gives M=diag(2,4,4), A=(5,7,7), B=(5,5,5)
and box2. The all-odd unit3mod4 family extends PR5172's four-row d3 example.
Every argument retains the anchors of the complete original instance;
no selected row subset is renormalized.

## Evidence and reproduction

`metric.py` supplies exact rational classification, constructive F/O/L
witnesses and both obstruction families. `verify.py` checks100 positive
fixtures and36 negative families, including negative metric valuations,
odd denominators, nonmatched original anchors, inactive columns and repeated
rows. It also runs only PR5172's authenticated small definition-level oracle
on d2/d3, not the predecessor's full suite. Ten controls distinguish empty
ties, nonpositive metrics, the two negative families, nonsquare positives,
collapsed colors, omitted anchor-setting rows and typed receipt corruption.
Universal coverage comes from the written proof, not those finite checks.

With CPython3.12 and the standard library, from repository or exported root:

```sh
python3.12 -I -B research/diagonal-metric-full-box/verify.py
python3.12 -I -O -Werror -B research/diagonal-metric-full-box/verify.py
```

The direct verifier authenticates every declared input byte and requires
`SOURCES.json` and `RESULT.json`; it compares the complete generated result
using canonical JSON to preserve numeric types. `--emit` is author-only
receipt generation and is absent from registered verification. Commands take
about4seconds locally. No generated artifacts are written during verification.
The authenticated source oracle is compiled from checked bytes; inherited
bytecode is not used. The generic repository metadata/source-history checker
remains the authority for Git provenance; cold replay needs no Git.

## Scope and credit

This changes the card's construction-domain premise to a source-bound algebraic
classification. It supplies no physical decoder, COPY/routing/precision/tape
cost, all-size multiplication theorem, new exponent or selected-frontier
change. Factor arithmetic is rational; binary labels use F2. Positive d and
nonempty ties are explicit hypotheses. Arbitrary row count appears in the
proof, whereas the corroboration is finite. Independent human and formal
proof-kernel acceptance remain unclaimed.

Credit Nick Petalas PR5172 (`f476ed6a0e5164fad8e6e31bfd78073777f795b1`) for
the fixed d3 obstruction and classification question; Sagar Thakrar PR3612
for the rational Gram theorem, canonical-anchor definitions, modulo-four
coloring and directed F/O/L construction; Aaron Wang/navinor's
PR2914/2978/3031 and DreamingOfClouds's F-star lineage, together with the
labeling predecessors retained in PR3612. The triangular-rank method is
credited, not new. Retained files are unchanged and pinned in SOURCES.json.
New contribution by JoyboyBrian with substantial OpenAI Codex assistance;
Apache-2.0. Base ec2780e8aeb1c88acaf5e9e470ef8c68e7fbbb6c, priority7.
Canonical claim: https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19145645.

## Open next questions

The arbitrary positive diagonal triple diag(a,b,c) has more valuation and
unit configurations than this one-parameter family. Does a similarly exact
criterion hold while preserving original anchors? First normalize by dual
power-of-two column changes and common scaling, then test the remaining
weighted coloring implication. A missing coloring alone is not an obstruction;
a necessity claim needs an actual rational factor family. This is a separate
future scope, not an implementation expansion or a claimed result here.
