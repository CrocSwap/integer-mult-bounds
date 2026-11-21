# No profitable equal-mass two-helper exchange at one frozen binary chart

On the exact 680-owner BIT word used by [#7830](https://github.com/CrocSwap/integer-mult-bounds/pull/7830), 3,112 unordered pairs of productive helpers would improve the signed invoice if their destinations could be exchanged at zero paid cost. **None can be exchanged by one chart-local linear correction with the other paid payloads and their responses fixed.** This excludes 1,979,232 chart/pair combinations. **No verified κ gain.**

## Construction being tested

Keep all 2,874 paid packets, all 111 main port pairs and all caller events. Exchange the destinations of two independent productive helpers and relabel the two closing outputs. Their new endpoint pairs must be nested in the actual rational frame atlas. Price only pairs with two positive new grades, the same total grade and a strictly larger smaller grade. For every exponent strictly between zero and one, strict concavity makes the new productive sum larger. These targets would be credited on each of the 36 binary calls. The paid invoice would stay fixed. The test ends before any construction or credit.

## Why a whole chart can be ruled out

Write the two helper indices as $i,j$, and let $t=e_i+e_j$ over the binary field. Before relabeling, swapping the two independent output rows changes the public transfer by $tt^T$. Fix a chart and form the following two spaces.

- The **read space** spans all initial inputs in the chart and all rows ever received there on paid packets.
- The **write space** spans the terminal responses to impulses at every paid send from the chart, together with the public outputs closing there.

At any clock, every local scalar covector factors through the read space. Every public response to a local intervention factors through the write space because an effect exits on a paid send or a public output. An update at a single cut therefore factors as $G L F$, where the rows of $F$ belong to the read space and the columns of $G$ to the write space. The nonzero row and column of $tt^T$ each require $t$ in the corresponding space. Granting **all** arrivals and sends drops chronology and enlarges the feasible spaces. If either membership fails under this relaxation, changing the clock or ordering independent events cannot rescue this edit with the fixed observations and responses.

The check takes residues of $e_i,e_j$ modulo each space. Equal residues are equivalent to membership of their sum. Both memberships must hold at the same chart. The packet-graph implementation and the independent forward/adjoint tape implementation agree on the 3,112 pair identities, every chart rank, and zero matches across all 636 charts. The latter also checks every coefficient of the 680-by-680 public native maps and 3,554 dirty retirements in each orientation. The graph verifier includes a control where granting a missing output direction changes the answer.

An initial temporal screen tried 48 cuts immediately after evenly spaced paid MOVE ordinals (zero-based ordinals `floor(n × 2873 / 47)`, for 0 ≤ n < 48). It found zero matches. The whole-chart proof supersedes that sampling for the declared mechanism. Unequal-mass changes, higher-arity target changes, interventions at two charts and edits that recode the other paid traffic remain open.

## Reproduce

Use CPython 3.12 with assertions enabled. The scientific checks need only the standard library and the three pinned source files in this package.

```sh
python3.12 -IB scripts/research_package.py --package research/bit-helper-exchange-obstruction
```

The outputs are `PASS_PACKET_GRAPH_EXCHANGE_EXCLUSION` and `PASS_LITERAL_TAPE_EXCHANGE_EXCLUSION`. `EXPECTED.json` records the ordered pair-list SHA-256 and all chart rows as [chart, read rank, write rank, number of matches]. `ORIGINS.json` pins every vendored input by repository, commit, source path, Git blob and SHA-256. The canonical word digest is `d3aa4426fa8fe7dc167270d01f2515184f2bff6a82744a14e941c5dd3afca27d`.

The benchmark at the time of the screen was [#7830 at 87fbf4f](https://github.com/Clear1nsight/integer-mult-bounds/tree/87fbf4f7b35b0f18ab12b5767775a9a424cf0b15/research/p104-mixed-rank-supplier), κ ≥ 0.00387992803556 under five premises. Its producer and separate complete application replay were run on their frozen sources. The present package checks only the claimed obstruction.

## Open next questions

Can projection of a helper direction remove enough paid arrivals to fund a direct independent return? Set one helper input to zero, find exact same-chart replacements among available arrivals in each orientation, and debit the entire direct bridge before building. This changes another paid payload, so the chart obstruction above does not settle it.

Clear1nsight supplied the [#7786 native word](https://github.com/CrocSwap/integer-mult-bounds/pull/7786), the #7830 mixed supplier and its independently written literal tape engine. Ali Romman supplied the [#7776 paid-graph extractor and endpoint audit](https://github.com/CrocSwap/integer-mult-bounds/pull/7776). The #7781 helper births and the #6834/#6980/#7001 paired-caller lineage underlie those artifacts. [#7833](https://github.com/CrocSwap/integer-mult-bounds/pull/7833) tests paid ingress repairs at nine specific binary receivers. This contribution tests destination exchange at every chart. OpenAI Codex materially assisted the proof, implementations and replay. Maintainer and independent human review remain open.
