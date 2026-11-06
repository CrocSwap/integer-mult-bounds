# Negative-coefficient half on a fixed marked tape

**Scoped all-width construction with exact finite corroboration; no new kappa.** A fixed 65-row table per direction computes and reverses the negative stochastic half for every W≥2 in at most6W+2 local transitions per direction, with no additional clean working cells under the stated uniform six-glyph layout. The bound is attained by x=-1,u=1. The new part is the local negator/composed table and its complete invoice; signed-half arithmetic and negative-input support retain predecessor credit.

## Exact local target

For every signed W-bit input x, W>=2, write x=2q+p with p in{0,1}. With a stationary read-only resident coin u, the exact [6092](https://github.com/CrocSwap/integer-mult-bounds/pull/6092) convention is

```text
S(-x,2,u) = -q-pu = -S(x,2,1-u).
forward: (x,P0,u) -> (S(-x,2,u),Pp,u).
```

The original parity p is retained for inversion. The coin's value is unchanged; interpreting its complementary branch in finite control is not a fresh draw or coin write. Both heads return, exterior cells remain unchanged, and the compiled direction is retained. Control exits at a fixed declared return label; that need not equal its entry label and does not supply a free repeated-call reset. A complete inverse image and all signed extrema must be included, rather than treating arbitrary malformed tapes as valid arithmetic inputs.

Use exactly the existing six work glyphs `0,1,P0,P1,S0,S1`. The canonical little-endian work layout is `P0 b0 ... b_(W-2) S(b_(W-1))`. It uses W value cells, one initially clean parity cell that becomes retained, and one resident coin cell. **No additional clean working cells** does not mean no supplied clean bit: the initial P0 cell is explicitly counted. Marker installation, layout conversion and coin acquisition/delivery remain caller premises.

The private negator phase uses the existing P1 glyph as a temporary tag inside a value cell. That uses the alphabet's existing symbol capacity; it is not a free binary-native encoding or a promise that marker glyphs are immutable/location-typed. The tag must be distinguished by phase/reachability, preserve the actual parity cell and be removed before the source positive component's canonical handoff. [PROOF.md](PROOF.md) supplies the all-width range, inverse-image, local-injectivity and phase-join proof; [TABLE.json](TABLE.json) is the literal program.

## Fixed table and observed evidence

The new negator has16 structural rules,32rows after coin expansion, and exactly2W+1 transitions on every canonical W-bit value/parity/coin input. Two copies combine with the credited33-row positive forward/inverse components, using control-level coin reinterpretation and zero-extra-step phase joins:65rows per direction,130total. The negative program costs4W+2 if pu=0 and4W+2k+4 otherwise, where k is the first zero of floor(x/2), capped at W-1. Its exact worst case is6W+2 per direction. No globally optimal leading constant is claimed.

The first actual literal replay passed on CPython3.12.14 in2.442seconds with21.22MiB peak resident memory, empty stderr and all15package hashes unchanged. These measurements check its budget, not a measured speedup against an old checker. The standard-library verifier needs no runtime Git, network, subprocess or install; registered normal/O caps are120seconds.

- All16,376signed input/coin cases at widths2..12 pass forward/inverse endpoint, exact-time, parity, head/control, canonical payload and frame checks:1,540,004transitions.
- All32,752standalone negator value/parity/coin cases, including signed minimum under modular negation, pass both applications and exact2W+1time:1,507,296transitions.
- The complete2,032inverse boundary points through width8 give1,016accepted images and1,016rejected nonimages; accepted points also pass forward-after-inverse. This suite executes86,934transitions.
- Another424forward/inverse calls at translated origins and selected boundary widths through4096 pass, with1,285,904transitions. The finite exterior pattern is explicitly recorded; arbitrary-exterior correctness rests on the written no-excursion proof.
- Eight intended-reason faults pass, including same-coin misuse, minimum-input pre-negation overflow, omitted phase, unreleased tag, local-direction/collision failures, removed inverse sign guard and a locally injective payload-preserving exterior excursion.

The non-mutant suites execute4,420,138transitions, including1,513,050credited source-derived positive-component transitions. Controls separately record42positive-phase transitions, including mutant-added/modified rows; that is not an exact original-row membership count. The older6092unary program and original6801checker are not executed. The single authorized candidate-data emission and original unexecuted checker drafts are retained externally. Final normal/O, registered, export/publication and hosted-CI checks are separate delivery observations recorded in the PR/handoff after completion.

```sh
python3.12 -I -B research/linear-negative-half-tape/verify.py
python3.12 -I -O -B research/linear-negative-half-tape/verify.py
python3.12 -B scripts/research_package.py --package research/linear-negative-half-tape
```

All-width claims require the written invariant/range/inverse-image/local-reversibility argument, not merely a larger finite test. The entry/return control handshake and compiled direction are part of the interface; a repeated-call controller is not supplied by relabeling a halt state.

The source6801positive `TABLE.json` is **transition program data**. Its source-derived rows, after namespace and read-coin substitution, execute as a credited component in the new negative word. The actual source file is retained unchanged. Neither the original6801checker nor the older6092unary program is run. Source6801's published positive case counts remain its prior evidence; the new observations above concern this negative endpoint and standalone negator.

## Task and credit

[TASK.json](TASK.json) retains the exact original `joint-query-controller` card, with explicit CHANGED/partial scope: local negative arithmetic, not a QQ16 or active-injection schedule or complete supplier bill. [SOURCES.json](SOURCES.json) pins only canonical catalogue/selected provenance. Root-owned [SOURCE-PINS.json](SOURCE-PINS.json) retains four exact6092/6801prose/table objects; runtime inputs are package-local, so external `VERIFY.inputs` is empty.

Credit zxv6092/6066for both-sign arithmetic, residue/coin ABI and the charged W-clean/O(W²)-program baseline; Nick Petalas6801for the positive fixed table/layout, its all-signed-input proof and explicit negative-table question; JoyboyBrian6095for its distinct literal baseline interpreter; AAAmirinu6244for the different reached-coin interface; Nick Petalas6026, Ali Romman5599 and retained stochastic/native lineage. Shifts, ripple/two's-complement arithmetic and local machine criteria are classical. See [CREDITS.md](CREDITS.md), [NOTICE](NOTICE) and [LICENSE](LICENSE).

Root/scouts saw provisional recipes and actual positive table data during earlier verification, before this round's claim; no transition, constructor or verifier was executed at that stage. Subsequent work is source-aware, with substantial OpenAI Codex assistance, not blind discovery, independent human review, proof-kernel or independent-end-to-end acceptance. The advance claim is [19445915](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19445915).

## Limits

Stop after one checked fixed table and its all-width local contract. No broader family/search is reserved. A table for signed inputs is not new; the claimed delta must be the charged negative coefficient under this exact no-extra-clean layout. Native binary encoding/MOVE, reached precision, layout/marker conversion, resident coin freshness/delivery, repeated-call sequencing, actual caller and full supplier invoice remain unprovided. All five selected assumptions remain; no supplier admission, kappa or frontier change follows.

## Open next questions

1. **Bind one actual reached negative-half caller.** Establish finite signed width, marker/layout conversion, retained-parity ownership, resident coin identity/freshness/delivery and return-control sequencing, then charge the complete local/native bill. Those producer/consumer contracts are missing; the historical6092sites are not a current caller admission.
2. **Price the physical representation and composition.** Give a legal binary/native encoding for all six glyphs and every transition, supplied parity preparation, both head returns and any repeated-call controller. Only then compare complete matched supplier costs. The local6W+2bound is not that invoice or an optimality theorem.
