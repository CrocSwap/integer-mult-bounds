# Interleaved R439 mini-nodes: 32 fewer XORs, with an exact class minimum

**Finite bit-circuit construction; no new kappa.** The four phase-A mini-nodes
of DreamingOfClouds' reviewed PR589 word cost 55 binary XORs. Reading external
operands at several intermediate destination bases reduces that cost to 39.
Rebuilding the literal reverse cleanup saves another 16: the complete native
word costs **24,305 -> 24,273 XORs**. This is **12 fewer XORs than PR728's
24,285**, on the same original word.

The exact base is `66849e1475c930fd7732b1a0067ffee7e1e95f60`. PR589's reviewed
head is `a5afc8c6169ea61ba7c51dfd3cade02cc7b13b46`, preserved in
[`e8-bit-p111-tuned`](../e8-bit-p111-tuned/tune/README.md). The selected frontier
at this base remains PR626 with PR543, conditional kappa
`51110230636731/31250000000000000 = 0.001635527380375392`, and is complex-bound.
R439 is a reviewed alternative bit supplier, not the bit word selected there.

## Reproduce

From the repository root, with standard-library Python 3.11 or later:

```sh
python3 -I -B research/p111-interleaved-mini-nodes/verify.py
```

Expected final line:

```text
PASS_P111_INTERLEAVED_MINI_NODES states=866 minima=13,9,9,8 ADDs=24305->24273 saved=32 extra_vs_PR728=12 columns=661 controls=8 no_new_kappa
```

The command checks the committed finite-distance certificate independently
of the search implementation, all 4,096 local Boolean inputs, all 661 symbolic
dirty-input columns of the complete word, every frame path, and the original
PR555/589 geometry and H1-H5 interface checker. It uses the original exporter
to check the complete native bill and exact positive-prefix bounds. By default
temporary artifacts are removed; `--out /path/to/new-directory` retains both
words, their exported records and the receipt. Existing output directories
are refused. Mathematical checks also run with Python `-O`.

To rediscover the certificate, or run the unchanged C++ checkers:

```sh
python3 -I -B research/p111-interleaved-mini-nodes/search.py --check
# Additionally needs a C++17 compiler and Boost headers:
python3 -I -B research/p111-interleaved-mini-nodes/native.py
```

The native command freshly compiles and replays both words at 5, 9 and 11
stages (883, 1,327 and 1,549 formal columns), checks chronological native
legality and all 96 stock bridge-omission controls across both words. Those
omission controls are the predecessor checkers' bank-level controls, following
the full actual-word replay. `CXX` and `BOOST_INCLUDE` select the compiler and
headers. The supplied harness was exercised on Linux; it needs GNU's
`bits/stdc++.h` for the unchanged legality checker. Expected final line:

```text
PASS_P111_INTERLEAVED_NATIVE both_words=2 stages=5,9,11 bridge_controls=96 ADDs=24305->24273
```

`CERTIFICATE.json` contains source SHA256 pins, exact predecessor heads, every
graph state/distance and all four literal replacement circuits. `EXPECTED.json`
and `NATIVE.json` are checked field for field; only elapsed time and the native
output-path spelling are excluded from deterministic native comparison.
Regenerated words are identified by canonical JSON, not gzip container bytes.
`search.py --write NEW_FILE` regenerates a certificate without overwriting one.

## What changes

| Frame | Destinations | Original XORs | PR728 single-layer minimum | Interleaved minimum |
|---|---|---:|---:|---:|
| 506 | 349, 340, 241 | 20 | 14 | **13** |
| 507 | 360, 381 | 11 | 11 | **9** |
| 508 | 385, 368 | 11 | 11 | **9** |
| 509 | 444, 413 | 13 | 9 | **8** |
| Total before cleanup | | 55 | 43 | **39** |

PR728, by Sagar Thakrar, is pinned at
`d454ae19fdd474b4dfa7bd2c28bbe5b0996365fb`. Its preparation/injection/recombination
class permits all external reads at one destination basis. We independently
recompute its 186-candidate minima, then enlarge the class by allowing reads
between any successive destination additions. The predecessor's savings and
its identification of these mini-nodes are credited, not claimed as new here.
No PR728 code or data is needed to run this package.

For example, let `a = r385`, `b = r368` at frame 508. The original two gates are

```text
a += r43 + r57 + r297 + r416 + r433 + r466 + r467
b += r365 + a + r433 + r466
```

Interleaving the reads gives the same map on *every* input, including dirty
`a` and `b`, in nine XORs:

```text
a += r43 + r57 + r297 + r416 + r467    # 5 XORs
b += a                              # 1 XOR
a += r433 + r466                    # 2 XORs
b += r365                           # 1 XOR
```

The external registers remain unchanged. All operations remain at the same
rank-four frame. The three-destination frame 506 needs a five-transvection
destination path and eight external reads; its complete circuit is in the
certificate. The other destination costs are 2, 1 and 1. Each external operand
is read exactly once in all four attaining circuits, although the optimality
search also permits repeated reads.

## Exact finite-class optimality argument

Fix the original destination registers `y` and the external registers `x` of
one mini-node. Its required map is

```text
y_out = L y_in + B x_in,     x_out = x_in       over F2.
```

The class consists of arbitrary-length sequences of binary XORs `y_d += y_s`
and `y_d += x_j` on these same registers, at this one frame. There are no extra
registers, no external writes, no cross-node sharing and no frame changes.
Multi-source gates are priced by their number of binary XORs. This includes
PR728's whole single-layer class, not just its reported witnesses.

Read a circuit backwards. Let `C` be the destination-to-output map of the
suffix already read; initially `C = I`, and at completion `C = L`. Prepending
`y_d += y_s` changes `C` to `C E_ds`: column `s` receives column `d`. An
external injection into destination `d` contributes precisely column `d` of
the current `C` to its external input's output column.

For a destination path, let `S` be the union of its exposed nonzero columns.
The smallest number of injections for a desired column `b` is

```text
ell_S(b) = min {|Q| : Q is a subset of S and XOR(Q) = b}.
```

Repeated occurrences of the same pattern cancel in pairs, so a subset
suffices even when repeated external reads are allowed. Conversely, any such
subset is realizable: inject that external register at an occurrence of each
chosen column. Different external inputs can be handled independently because
they are read-only and the circuit is linear. Thus the exact total cost of a
destination path is its length plus `sum_j ell_S(B[:,j])`.

The state `(C,S)` is therefore sufficient. Its edges prepend one destination
transvection and union in the new exposed columns. Breadth-first search from
`(I, columns(I))` exhausts **7 states for k=2 and 859 for k=3**. The full state
graphs are shared by the nodes; there is no heuristic pruning or depth limit.
Every circuit in the class induces a path in this finite graph, regardless of
its original length. Minimize

```text
distance((I, columns(I)), (L,S)) + sum_j ell_S(B[:,j])
```

over all reachable terminal states. This gives 13, 9, 9 and 8. At frame 506,
the four terminal states have `(destination cost, total cost)` equal to
`(3,17), (4,14), (4,16), (5,13)`. Each two-destination node has one terminal
state; its attaining cost is also the elementary lower bound of one read per
nonzero external column plus the shortest destination transformation.

The verifier does not import the search engine. It checks matrices and graph
transitions using row coordinates, and injection prices by enumerating all
subsets rather than the generator's vector BFS. It checks **5,168 directed
edges** for closure and distance-potential inequalities. The initial distance
is zero; every other state has a predecessor at distance one less. Edge
inequalities give a lower bound on every possible path, while these
predecessors give attainment. This certifies the exact distance table and
prevents missing states from concealing a cheaper route. The literal circuits
independently attain the resulting lower bounds.

This is a finite-class proof with an executable certificate, not a formal
Lean proof, nor an optimality theorem for arbitrary supplier circuits.
External writes with restoration, extra work registers, cross-node circuits,
other frames and other puncture patterns are outside the class.

## Complete cost and interface

| Native work | Original | Replacement |
|---|---:|---:|
| D, compensation | 18,085 | 18,085 |
| A | 2,130 | 2,114 |
| Scatter | 527 | 527 |
| B | 934 | 934 |
| C, literal reverse cleanup | 2,629 | 2,613 |
| Total binary XORs | **24,305** | **24,273** |
| Exported records, including non-ADD events | 27,234 | 27,202 |

No helpers, external source-access reads, basis changes or restoration gates
are omitted from this bill. The same 439 dirty helpers and 111 live ports are
used. Each of the 661 complete frame paths is identical, so all native climbs
and their source-access cost are retained. The nine retained copies/erasures
each have rank seven. The non-ADD event inventories agree, and the paid profile
is `{1:1323, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:19}`, of rank mass 5,129.
The local change creates no new recursive child or new bank obligation.

Replacing a node by its identical full dirty-input map preserves the raw
operator and dirt compensation. Rebuilding C from all non-target A/B gates
preserves literal H4. The original H1-H5 checks and U/J/K/C conclusions pass
without normalization or a weakened interface. The exact forward positive
bound remains 49,347; reverse decreases 1,113,070 -> 1,111,946. The native
payload `64 F^3 B^2` remains 93 bits, below the existing `2^104` cap (B is the
reverse positive bound here, not the helper count).

The package rejects eight controls: incomplete graph; inflated distance;
unpaid gate; F2-neutral external writes outside the class; omitted cleanup;
omitted injection even with matched reverse cleanup; illegal frame descent;
and stale cleanup under literal H4. Stale original cleanup is deliberately
also checked as a **positive scalar control**: it restores the same endpoint
but is not the literal reversal of the changed word.

## Scope, provenance and handoff

The assignment seed **17** comes from OS randomness. It selects a bit-supplier
track, rotates the four-node processing order and determines equal-distance
path tie order. Both reachable graphs and all four nodes are exhausted; the
optimum is not a seed-dependent failed search. The local claim records three
candidates, overlap checks and the stopping rule. There was no pinned sprint
coordination issue, so no reservation issue was opened.

Neither `upstream/`, existing supplier sources, the selected certificate nor
the review ledger is changed. The existing whole-owner hosted program,
recursive coefficient invoice and outer assembly have **not** been regenerated
for this replacement. Identical native profiles alone are not a substitute
for those integration checks. No new bit exponent, kappa, global circuit
optimum, practical runtime improvement or complete multiplication theorem is
claimed. All-size compilation, common-label/mutable-basis realization,
whole-owner hosting, normalized residuals, precision/tape and analytic transfer
remain inherited obligations. No remote CI or Lean run is claimed.

Credit: eumemic's PR555/543/493 construction and checker; DreamingOfClouds'
PR589 transports, PR545 punctured unit and PR510 nine-stage chain; Sagar
Thakrar's PR728 mini-node factorization; Dylan Crow's format/exporter/checkers;
DaysSky's bridged stages and hosting; Zhihao Chen's PR425 interface and PR386
geometry; Chafik Boukhalfa's PR472 realization and compiler lineage; Jacob
Sussman's E8 unit, and the cumulative predecessors in the retained
[supplier notice](../e8-bit-p111-tuned/NOTICE.md). R420 circuit PRs 670, 674,
681, 688, 694, 708, 713, 748 and 754 are related concurrent work; their code is
not imported and their savings are not added to this construction.

Prepared for **Ryan Haines (@Ryan-Haines)** with substantial **OpenAI Codex
assistance** in research, proofs, implementation, verification and writing.
Apache-2.0, under the repository license. No independent human review or
delegated-agent review is claimed. See `VALIDATION.json` for executed checks
and environment, and `CLAIM.md` for the final handoff link.
