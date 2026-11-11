# Whole-word bound on coupled BIT chart relabeling

On the retained BIT word, a single adjacent nested chart pair cannot
support the fixed target κ = 10018846261809/2500000000000000. The
proof checks all 897 eligible pairs, with no unresolved pair. The exact
conditional κ change is 0% (**NO VERIFIED GAIN**).

## Scope and bound

Fix the scalar order, logical lifetimes, public starting and final
charts, every chart outside the active pair, and the complete caller
bill. For one active pair, relabel any shared ADD contact at either
chart, with the same label for both operands. The same relaxation
applies to owned INIT and CLEAR. A physical SWAP carries the contact
history of its logical role. Consecutive contacts on a role either
share a chart or use one direct transition between strictly nested
charts, charged at the dimension difference in either direction. The
upper bound grants zero incremental setup, scalar work, routing,
phase, ownership, restoration, precision and tape costs.

The replay reconstructs 32,581 vertices, 62,474 role contact edges
and all 2,871 original paid MOVEs. The 897 distinct eligible pairs are
exactly the adjacent nested pairs occurring among those MOVEs.
For each pair, every variable contact has two possible labels. An
edge with two variable endpoints has zero cost for equal labels and
the rank-one tariff for unequal labels. An edge to a fixed endpoint
contributes a unary cost or forbids an incompatible label. Subtracting
the smaller of the two unary costs and adding it to a constant gives
a nonnegative source/sink capacity model. Each flow certificate has
the same value as its cut. This proves the minimum paid lower bound
over all simultaneous choices within that pair. Each cut witness
uses the original labels. The full invoice has 107,352 paid jobs,
19,950 productive fields and rank surplus 1,506. It is priced as
productive minus paid moments with rank tariff r^(1−κ). The verifier
encloses log(r) by a finite atanh series with geometric tail and the
exponential by alternating Taylor bounds. It rounds lower and upper
tariffs outward on the 10⁻⁴⁹ grid. Comparing upper old tariffs with
lower new tariffs leaves at most
`837/1250000000000000000000000000000000000000000000000` raw
savings across the complete 36-copy invoice from interval rounding.
The best whole-invoice net upper is exactly
`-150259748047868384659982093203238820648182213478633/2500000000000000000000000000000000000000000000000`
(approximately −60.10389921914735).

The initial independent-edge bound retained all 897 pairs. The
first exact solver hit its 90-second cap. A 16-pair Dinic retry and
an 881-pair continuation then exhausted the scope. The retained
certificate verifies the exhaustive result without an optimizer.
No physical instance or changed BIT supplier was built.

## Replay

From a clean repository checkout, with CPython 3.12 and assertions:

```sh
python3.12 -B scripts/research_package.py --package research/bit-coupled-chart-bound
```

The two live inputs are the word and invoice under
`research/paired-query-only-bit` at canonical commit
`e54523517d0f03e58352e647c403a5af3e525a57`. The
[source manifest](SOURCES.json) pins both paths, Git blobs and SHA-256
digests. For a verified Git-free export, run from the extracted root:

```sh
python3.12 -I -B research/bit-coupled-chart-bound/verify.py --root .
```

The independent checker rebuilds the literal logical lifetimes,
uses rational Gaussian elimination for nesting, reconstructs the
full 36-copy signed invoice, and checks every directed cut/flow
certificate. It tests altered source bytes and a forged flow.
Expected output and the SHA-256 digest of the decompressed certificate
are in [AUDIT.json](AUDIT.json). The certificates use exact integer
capacities at the directed tariff grid declared in the verifier.

## Open next questions

Can simultaneous choices among three or more chart labels change the
paid profile? First bound a specified multichart component with each
shared ADD contact and endpoint charged once. A target-clearing bound
would need an exact arbitrary-input action and fully charged replay.
Additional intermediate moves, new chart stock, changes to contact
order or lifetimes, and caller changes are outside this proof. Pairwise
bounds cannot be added for overlapping changes.

## Credit

[#6726](https://github.com/CrocSwap/integer-mult-bounds/pull/6726)
supplies the native BIT word and
[#7001](https://github.com/CrocSwap/integer-mult-bounds/pull/7001)
supplies the paired caller and retained signed invoice. The original
attribution and license remain with those files.
[#7289](https://github.com/CrocSwap/integer-mult-bounds/pull/7289)
bounds balanced changes to ingress destinations at fixed clocks.
[#7293](https://github.com/CrocSwap/integer-mult-bounds/pull/7293)
fixes the original charts and tests the available destination span.
This proof couples chart changes across both ADD operands and charges
each contact edge once. [#7277](https://github.com/CrocSwap/integer-mult-bounds/pull/7277)
is the separately reproduced complete conditional comparator used in
this campaign. The campaign's Round 30 complex flow audit supplied the
certificate algorithm.
OpenAI Codex and subagents materially assisted the proof, implementation,
independent audit and packaging. Apache-2.0.
