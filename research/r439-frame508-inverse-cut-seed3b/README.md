# R439 frame 508: inverse-column cut forces the exceptional source to rank four

**Scoped exact obstruction; no new selected κ.** For the pinned 11-wire linear map at R439 frame 508, register 19 must visit the full rank-four block frame in any monotone same-wire implementation whose operation frames stay inside that block frame. The result allows arbitrary ADD sequences, arbitrary proper intermediate frames, and arbitrary circuit length. It closes the source-19 exception left by the predecessor's dependency-span result. It does not settle frame 509/source 22 or enlarged interfaces.

The R439 scalar simplification reduces ADDs while retaining the paid profile. The proposed change was to keep source 19 in a proper subframe and relay its information through other registers, thereby changing the child histogram. The exact inverse column blocks every such relay in the fixed 11-wire frame-508 interface.

## Pinned object and exact witness

The cycle accepted seed `3b2676afb1d8667edc131585f741d4b0`, track `incumbent-optimization`, task `scalar-to-moment`, priority revision 3, catalogue SHA-256 `6686ad58f1fbdbc87134a78901b60fd53a20d3984355e91defbbebc9e9fa8075`, and base commit `0b1cccf86e2f5132ed286a26ef0a681a495740ea`. The selected-record SHA-256 is `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.

The verifier checks the R439 source manifest and reconstructs its exact composition from the pinned helper-star word and PR1015 block inputs. The 21-ADD frame-508 block has 11 wires and exact binary matrix rows:

```text
[1, 767, 509, 891, 927, 943, 765, 1019, 911, 254, 1914]
```

Rows and columns use the sorted register order `[19, 27, 35, 43, 57, 65, 66, 74, 89, 97, 466]`. Exact GF(2) inversion gives

```text
support(M^-1 e_19) = {19, 35, 66, 89, 97, 466}.
```

In the stated register order the inverse-column bit vector `t` has bitmask integer `1861`; direct multiplication gives `M t = e_19` over `F_2`.

Register 466 enters this block already at its full frame `F`; its entry-frame rank is four. The predecessor's exact rational root-span data gives entry rank two for source 19, rank four as the required output span for the other ten rows, and rank two for source 19's identity row. Thus register 466 cannot belong to any proper subframe's eligible low-wire set, but its coordinate is required in the inverse-column support.

## Cut and factorization argument

Assume a same-wire circuit keeps register 19 below `F` throughout. Let `H` be the largest frame on its path. Then `H` is a proper subframe of `F`, and every operation touching register 19 has a frame contained in `H`.

Partition operations into those whose frames are contained in `H` and those whose frames are not. A gate in the latter class cannot touch register 19. If such a gate promotes another register outside `H`, that register cannot participate in any later `H`-contained gate: monotone frame growth would make the later gate illegal. Therefore every outside-`H` gate commutes past all later `H`-contained gates, whose wire supports are disjoint. Repeating these swaps gives a matrix factorization

```text
M = Q P,
```

where `P` consists only of operations in `H` and acts only on wires whose entry frames are contained in `H`; `Q` does not touch register 19. Hence `Q^-1 e_19 = e_19` and

```text
M^-1 e_19 = P^-1 Q^-1 e_19 = P^-1 e_19.
```

The right side has support only on wires eligible for the `H`-phase. It cannot contain register 466, whose entry frame is `F`. This contradicts the exact inverse-column calculation. Register 19 must therefore visit `F`.

The other ten output rows already force their exit frames to `F` by dependency spans. The inverse-column cut now forces the eleventh. If a wire enters at rank `e` and reaches rank four through positive integer climbs `d_1,...,d_m`, then for `q=1-a` with `0<q<1`,

```text
sum(d_i^q) >= (sum d_i)^q = (4-e)^q.
```

The existing direct climb attains this lower bound. Splitting a climb cannot lower the paid moment. Frame 508's local direct-climb histogram is `{2: 6, 3: 2}`; the three wires already at rank four incur no local climb. The unchanged downstream itinerary and all other supplier costs are outside this local obstruction. The selected bit supplier is nonbinding, and this result makes no κ or supplier-adoption claim.

## Optimistic cost and stopping point

For source 19 alone, staying in a rank-three subframe would replace the existing local rank-two climb and next rank-four climb by rank-one and rank-five climbs. Its hypothetical moment delta is `1^q + 5^q - 2^q - 4^q < 0` for `0<q<1`; a direct jump from its rank-two entry to the final rank-eight frame would be an even more favorable source-only relaxation. These are only ceilings: every carrier and every restoration must be charged. The inverse-column cut proves the fixed-interface circuit required by this relaxation does not exist, so the construction attempt stops without accepting an unpriced relay.

## Reproduction

From the repository root, run the pinned scalar positive control and this package:

```sh
python3 -B research/r439-bsection-stars-seed01/verify.py
python3 -I -O -B research/r439-frame508-inverse-cut-seed3b/verify.py
python3 -I -O -B research/r439-frame508-inverse-cut-seed3b/test_verify.py
```

Expected first line: `PASS_R439_BSECTION_STARS ... no_new_kappa`. The new verifier emits `PASS_R439_FRAME508_INVERSE_CUT support=19,35,66,89,97,466 donor=466 full_frame=4 climbs=6x2+2x3 no_new_kappa` and writes [CERTIFICATE.json](CERTIFICATE.json). The controls include an exact low-wire shear that the lemma accepts, removal of the full-frame-donor premise, and a singular-map rejection. `SOURCES.json` pins the selected record, current task catalogue, R439 builder and inputs, and the prior exact block certificate.

## Scope and remaining obligations

This result assumes the same 11 block wires, the exact frame-508 matrix, monotone frames contained in `F`, and ordinary XOR additions. It does not cover added wires, COPY/ERASE changes, cross-block seams, operation frames outside `F`, a different scalar word, native hosting, precision/tape admission, all-size realization, or analytic transfer. No selected record or frozen source was changed.

### Open next questions

- Does the same exact inverse-column cut settle frame 509's exceptional source 22? This is the remaining exception in the predecessor's ten-block result. Reconstruct its matrix and check whether `M^-1 e_22` contains a wire entering at the full frame; the separate block and source pins are the blocker here.
- Can extra wires or a cross-block seam evade this cut while reducing the fully charged profile? Pick one named interface and price all new climbs, restoration, and boundary costs before synthesis; this package supplies no favorable budget for those extensions.

## Coordination and credit

The refined claim is [Discussion #1163](https://github.com/CrocSwap/integer-mult-bounds/discussions/1163#discussioncomment-18920682). The final pre-claim overlap refresh covered 442 open PRs and 405 Discussions with complete pagination; the exact `frame 508 / source 19 / rank-three` query returned no public matches. The existing local `research/r439-bblock-frame-barrier` result is treated as predecessor evidence, not as novelty proof. The nearby #1695 claim concerns a five-helper basis change in D and is a different object.

Credit the R439/source lineage: DreamingOfClouds (PR589), eumemic (PR555/543), Sricharan Vagvala (PR967), Aaron Wang (PR1015), Ross Richardson (PR923), and the frame-barrier work of Arham Tahir. Prepared by OpenAI Codex with substantial Codex assistance; no subagents or independent human review. Apache-2.0.
