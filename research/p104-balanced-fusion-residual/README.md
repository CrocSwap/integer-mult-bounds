# The balanced fusion leaves a noncancelling caller residual

[Full research paper](manuscript/ARTICLE.md).

The frozen 4+4→8 fusion removes one paid contact from the #8027 binary graph, but its literal normalized word has one public error: **output 130 gains input 38**. All other 629 public rows and all public chart placements match; the changed `630 × 630` map remains invertible. In the original 36-call paired BIT caller, none of the `2^36−1` nonempty subsets of this **same literal word** cancels the error on the constant-binary-field subclass of the source contract. This is a proof by 36 independent error matrices, not a brute-force enumeration. No valid replacement or κ improvement is claimed.

The printed trial `κ = 0.00389046` is numerically reachable **if** seven correct, physically admitted substitutions with the same paid and productive labels existed. The exact word here is not one. The result does not exclude a different reconstruction or coordinated repair with different caller effects.

## Literal fusion and independent full-row replay

The original contacts are `0 → 509` at native clock 7112 and `509 → 1` at 7210, each of grade four. The candidate sends helper 626 directly `0 → 1` at grade eight, substitutes an available hinge field, removes one late ADD, and performs a chart-1 owner SWAP and six explicit ADD repairs. [candidate.py](candidate.py) reconstructs the complete word; its 39,605 instructions are frozen in [ONE-RESIDUAL.json.gz](pinned/ONE-RESIDUAL.json.gz). The sole error is

```
output[130] = native_output[130] XOR input[38]
            = y[19] XOR x[19] XOR x[38].
```

The paid histogram trades two grade-four MOVEs for one grade-eight MOVE; all other ordered MOVE incidences are retained. An independent interpreter checks all 630 symbolic rows, reconstructs the `F₂` transpose independently, confirms the two altered paid endpoints and all public charts, and verifies an omitted final correction corrupts output 87. The changed map has rank 630; invertibility is not equality with the required map. In a separate fixed-history control, changing only inputs 19 and 38 leaves all four chart-544 arrivals unchanged while flipping the desired row 130, so no arbitrary decoder of that fixed history repairs it. See [CANDIDATE-AUDIT.json](CANDIDATE-AUDIT.json).

All 3,433 private CLEARs remain at their original charts and have symbolically nonzero values. Exactly seven clear expressions change: owners `2241, 2242, 2252, 2477, 2898, 3317, 3318`. Full old and new input supports are in [constant_composition.json](constant_composition.json). These are normalized data-deletion records; a physical erasure, owner-lifetime, arbitrary-field adjoint, compiler or paired-caller implementation has not been established. The transposed replay is a matrix check over `F₂`, not a physical reverse execution.

## No cancellation across the 36 literal placements

The pinned paired caller has stages `s=1,…,18` and two lanes, with base `b=0` or `19`. The local defect reads port 38 and changes port 19. On constant binary fields the unchanged caller acts independently on the ports. Prefix and independent reverse-suffix replays derive the same 38-role form `v = e_b + e_(b+s)` for a placement. Its full error matrix from port-38 inputs to port-19 outputs is

```
E_(b,s) = v vᵀ.
```

Errors superpose because the extra shear reads port 38 and only changes port 19. Each `E_(b,s)` has a diagonal at `(b+s,b+s)` occurring in no other placement. For any nonempty selected subset, choose one selected `(b,s)`, set only source `(root,b+s,38)` to one, and all other source fields to zero: output `(root,b+s,19)` is wrong. The 36 matrices consequently have rank 36, and no nonempty subset cancels. A control deliberately duplicates one matrix, drops the rank to 35, and is rejected.

[constant_composition.py](constant_composition.py) checks the local source and literal candidate, all **4,218** independent root variables in forward and reverse passes for each of 36 placements, and four multi-placement controls. The 14,688 unchanged helpers form identity blocks because the exact local graph preserves their endpoint rows. [caller_dual_check.py](caller_dual_check.py) independently derives the 36 prefix/suffix witnesses. This is a counterexample on allowed constant binary address fields, not a proof that a particular top-level integer operand reaches that assignment or a replay of arbitrary address fields. See [CALLER-PROOF.md](CALLER-PROOF.md).

For the inherited 268-factor, floor-15 source, use 267 retained rank-127 factors and one first factor. The exact inequality `4·127^267 > 15^268` retains all of the smallest first-factor target, so the constant-field witness survives the stated truncation. This is a source-service-domain statement; it does not establish physical reverse execution or top-level operand reachability.

## Bounded repair screens

Under a fixed remaining tape, a single linear hinge correction and one linear `0 → c → 544` late rebind at the existing clocks, the 12-field hinge has 4,096 linear codes; 512 restore all top outputs. Testing all 111 rank-one sender charts with free preclock histories finds only chart 21 algebraically capable of the needed late field, and its image is incomparable with chart 544, so the required nested transfer is illegal. A separate low-pivot implementation reproduces the result and exact rational image test. This does not exclude nonlinear, multiple-slot, retimed or other upstream changes. [BALANCED.md](BALANCED.md) and [HINGE-AUDIT.json](HINGE-AUDIT.json) state the contract.

On the frozen defective word, a separate linear fixed-tape screen gives the sender and each terminal their full historical stocks. One source-local recoding at any of the four chart-544 ingress contacts or its existing `0 → 91` feeder fails. For the existing `509 → 0` return, making input 38 recoverable at chart zero conflicts with preserving a required chart-525 output: the same sender coefficient parity must be both one and zero. These are individual-slot results, not an exclusion of coordinated changes. The checker includes 200 small models, exhaustively comparing all 16 perturbations and 16 targets in each; see [SECOND-SLOT.md](SECOND-SLOT.md) and [SECOND-SLOT.txt](SECOND-SLOT.txt).

## Counterfactual whole-caller price and repair budget

The following numbers **assume** valid `4+4→8` substitutions while leaving every other original target, paid label, owner contract and positive supplier unchanged. They price a histogram; they do not install or certify the defective word. At `κ=0.00389046`, the exact local saving is in `[0.021428347033463130, 0.021428347033463131]`.

| Hypothetical substitutions among 36 | Raw target minus paid at trial |
| --- | ---: |
| 6 | about −0.003835034296043386 |
| 7 | about +0.017593312737419744 |
| 36 | about +0.639015376707851 |
| 36 plus one extra grade-one paid contact | about −0.360984623292149 |

The saving is positive per substitution, and a nonzero paid contact of integral grade at least one costs at least the grade-one term. Even the optimistic 36-substitution histogram therefore cannot pay **one additional grade-one or higher contact** at the trial, when no other paid or productive labels change. This leaves free or grade-neutral repairs and changed wider invoices open; it is not a theorem against every reconstruction. Directed intervals and monotonicity checks are in [INVOICE.json](INVOICE.json).

For the seven-substitution **IF** profile, the 268-factor split tariff at `L=2^50` has binary/positive debits `21/10` and directed normalized surplus at least `0.000002108128556528`, exceeding `2/L`. Its six-stage ranks are `(25,000,000, 160,000,000, 1,000,000,000, 6,000,000,000, 36,000,000,000, 224,000,000,000)`; the positive log rank is 1,600,000. The checked signed trial uses ordinary rate `0.0038904998`, gap `10^-14`, positive cap `0.0038904632568359375`, and records **54 strict and four functional gates**. The separate `v=285`, `L=2^47` profile has debits `22/10` and directed surplus at least `0.000002241853533970`, also above `2/L`. The 48-call positive raw margin at the trial is approximately `+8.1314216200`. Both profiles retain all five #8035 all-size premises: all-column native action, owned erasure and restoration, compiler transfer, precision and tape services, and analytic recovery. Those premises and the valid substitutions are not established here; the astronomical production tapes were not executed.

## Source and verification

The original graph is from [#8027](https://github.com/CrocSwap/integer-mult-bounds/pull/8027) at `fb9b6a7b0d27da1cf98430893a3016bf811e2aa4`; its gzip SHA-256 is `74e93daf2b7acf794ffb51f92f03f51556f68126d41ee13a8969bddb4cbe6326`. The candidate gzip SHA-256 is `7fa5589301124788237a569c3c0bbc0783f70efd840b15238300b8a2d5ab1cd7`. The caller and #8041 price reader are pinned in [SOURCES.json](SOURCES.json). The invoice replay restores the 91-member #8030 archive at tree `3a1c001cbf175ae48ee1d56e56e4723eda1c8218`, validates each file and tree ID, and applies the byte-pinned #8035 overlay at `ea776471bf8ed143a0625cf2d7532f65d15eb5f9`; its output was also compared on the later extended machine. The predecessor archive is retained because its actual arithmetic and source readers are needed for offline replay.

[#8043](https://github.com/CrocSwap/integer-mult-bounds/pull/8043), head `ab3680a3e56ff247fef2a76ad9110d571f19ef0d`, contains the earlier discrete-curvature and contact-count work; this package studies the literal candidate, its caller error, bounded repairs and a conditional signed invoice. The local parent `0618e75a22cec54d1651394ef83d088551b7f026` is the separate five-file CI prerequisite on canonical `e54523517d0f03e58352e647c403a5af3e525a57`. Vendored-byte checks do not establish that the unmerged external PR heads are ancestors of this package.

Using Python 3.12 and only the standard library, from the repository root:

```sh
python3.12 -I -B scripts/research_package.py --package research/p104-balanced-fusion-residual --check-only
python3.12 -I -B scripts/research_package.py --package research/p104-balanced-fusion-residual
```

The registered replay authenticates its checked code and bytes; regenerates the literal graph; independently checks its rows, transpose and collision; reproduces both caller proofs and the dependent-matrix mutation; recomputes both hinge screens and the fixed-slot controls; and restores the offline numerical engine to reproduce the raw, 268-factor, 285-factor and signed IF receipt. It also rejects altered source bytes and an actually omitted correction. These AI-assisted computations are evidence for review, not independent human or proof-kernel acceptance.

## Open next questions

- Can a different set of local and later edits remove the cross-port residual while preserving all 630 rows, clear semantics and typed public endpoints? Start from the explicit chart-544 collision and price the complete changed program. No all-input repair is supplied.
- Can a valid, fully physical supplier achieve the favorable counterfactual invoice without adding paid grade? Bind the exact paired caller, source service, all private erasures and five all-size premises, then recompute every signed gate. The printed trial remains conditional and unachieved by this word.

Ali Romman supplied the #8027 graph and physical supplier. Clear1nsight prepared the fusion, caller proof and controls with substantial OpenAI Codex assistance; see [PARENT-NOTICE](PARENT-NOTICE), [NOTICE.md](NOTICE.md), and [LICENSE](LICENSE) for predecessor and pricing credit.
