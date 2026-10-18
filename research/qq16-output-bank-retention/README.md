# Capture QQ16 early records in their eventual output banks

This is a conditional resource improvement to [PR2540](https://github.com/CrocSwap/integer-mult-bounds/pull/2540)'s
complete local native decoder. Capture its sixteen early X1 records directly
in the eventual selected X output banks. Hold those banks unchanged through
B1 and consume the records in place. This removes **sixteen separate owned
full-cover banks, sixteen unit ADDs and thirty-two CLEARs** from the literal
decoder. Its scalar allowance decreases **17,472 → 17,280**. All native child,
wrapper and cover-map events remain identical, in the same order.

The contract changes in one place: the sixteen selected X output banks must
be exclusively available at the early capture cut, and retained through B1.
There are still sixteen retained values. Their retention and movement are
explicit physical obligations. This is neither a new information bound nor
a global storage minimum, admitted supplier or improved κ.

## Exact construction and proof

The direct source is ywz65's PR2540 at
`630d557af5088f66b45c447969cee9576600e50b`. Its immutable
[literal word](predecessor/WORD.json), [proof](predecessor/PROOF.md) and
[receipt](predecessor/RESULT.json) are retained with Git blob and SHA-256
pins in [SOURCES.json](SOURCES.json). Its logical and native dependencies are
PR2511 `f40e74a27f7c8781feea06a1571dc99ed5d9a004` and
PR2512 `851dd3486a2d0549b51e85978a65ccb4eec619c0`.

Let V=A∪T be the source's sixteen selected ports. E_p denotes the physical
X1_p value after F0, in frame F_L. All owned initial contents may be arbitrary
and discarded by charged CLEARs. In the source program, for each p∈V:

1. Before B1, clear R_p in F_L and add X1_p to R_p.
2. After B1, clear Z_p in F_L, add R_p to Z_p, and apply the rank-eight
   F_E1 stage to Z_p, obtaining its F_U1 frame.
3. Run the complete decoder suffix. It does not read or write R.
4. Clear all sixteen R_p banks at retirement.

The new [WORD.json](WORD.json) replaces step 1's R_p by Z_p, removes step 2's
CLEAR and ADD, and removes step 4. It keeps every stage and the entire suffix.
The retained banks lie outside the inherited B1 field namespace; B1 must act
as the identity on them, exactly as on the predecessor's separate R banks.

**Simulation lemma.** For every payload dimension and arbitrary input,
output and workspace contents satisfying the ownership/retention contract,
the new word has the same 224 output values and frames as the old word,
and restores the same 224 current borrowed fields and local scratch.

**Proof.** Immediately after the early capture, new Z_p and old R_p both
equal E_p in F_L. B1 preserves those respective owned banks. In the old
post-B1 prefix, each clear/copy sets Z_p to E_p; in the new prefix it already
has that value and frame. The same rank-eight stage therefore produces the
same value and F_U1 frame on each Z_p. Operations on distinct selected banks
do not interfere. After all sixteen stages, every field used by the common
suffix agrees, including the untouched current borrowed fields and every
unselected output's arbitrary initial contents. The old R fields are the only
unmatched storage, and the suffix has no access to them. Identical ordered
operations preserve agreement through every subsequent event, including both
private owner sweeps and every CLEAR. The removed final R clears affect no
output or borrowed field. The old selected Z dirt was discarded before its
first read; discarding it at capture instead is authorized by exclusive early
ownership. This proves the claim without commuting any native maps. ∎

Consequently, **conditional on PR2540's decoder/native theorems**, the new
word returns the original 112 X and 112 Y arrays in the same common F_U1
frame. It does not return the original pre-F0 physical frames. The early value
is consumed in Z; a final clear of Z would destroy a required output. There
is no residual R resource to retire. Source restoration and the two private
scratch bodies are literally unchanged.

The checker authenticates the exact 32-event capture, 48-event copy/stage
prefix and 16-event retirement before rewriting. It verifies the remaining
**2,366 events** are identical. This is also a direct proof of frame legality
relative to the predecessor: the suffix starts in the same frame state, not
merely with the same ranks.

## Complete added local invoice

The inherited F0/B1 calls retain their own costs. The history marker in either
word denotes B1; it is not an added free gate. The two local owner bodies
remain separate, with peak sixteen owned local scratch arrays.

| Resource | PR2540 literal allocation | Coalesced word |
|---|---:|---:|
| Owned full-cover bank identities, including all final outputs | 240 | 224 |
| Values retained through B1 | 16 | 16 |
| Separate early banks in addition to final outputs | 16 | 0 |
| Peak owned local scratch arrays per owner | 16 | 16 |
| Positive rank-one / rank-eight children | 224 / 16 | 224 / 16 |
| Native rank mass | 352 | 352 |
| Native monomial wrappers | 480 | 480 |
| Full-cover maps | 208 | 208 |
| Unit / quarter ADDs | 856 / 832 | 840 / 832 |
| CLEARs | 320 | 288 |
| Real scalar primitive allowance | 17,472 | 17,280 |

The scalar prices are the pinned `research/joint-query/verify_scalar.py`
prices: unit ADD 8, quarter ADD 12, CLEAR 2. The complete delta is
`16*8 + 32*2 = 192`; the new allowance is `840*8 + 832*12 + 288*2 = 17280`.
Early capture still costs sixteen ADDs and sixteen CLEARs. The removed
operations are the later copy/clear and the separate R retirement. No child,
frame change or cover map is removed or declared free.

The bank counts are distinct owned full-cover bank identities used by these
literal words. They are not a lower bound on simultaneous live information
or optimal physical memory. A local owner-private array is not counted as a
full-cover bank. Physical tariffs may depend on placement and timing, so the
smaller local invoice alone does not prove lower total runtime.

## Verification and its limits

The new interpreter is code-disjoint from the predecessor. It uses exact
rational coefficients and formal noncommuting operator words on sixteen
early plus 224 current physical input symbols. Adjacent inverse operators
cancel; distinct operators never commute. It checks both entire words,
all 224 output expressions, both 112-output checkpoints, arbitrary owned
dirt elimination, borrowed physical-source restoration, and scratch cleanup.
All **448 native events** agree literally, including roles and orientations.

This deliberately proves equivalence for an even freer operator model. It
does **not** independently prove that a native map preserves F_U1 or that
PR2540's logical decoder returns the original inputs. The coarse frame checker
uses those predecessor operation contracts; the simulation lemma transports
their legality. The unmodified PR2540 registered suite was also replayed at
the exact head above and passed, including its native checks and six test
groups. That is reproduction of the author's evidence, not an independent
native proof or maintainer review.

Fifteen semantic controls reject wrong capture time/source/sign/frame,
missing capture clearing or upgrade, borrowed aliasing, destructive post-B1
clearing or retirement, wrong map/ordering, missing Y restoration, wrong
F0-inverse sign, surviving output dirt and private scratch leakage. Six
artifact tests check a read-only Git-free export, source and live-price
corruption, changed candidate word, type-sensitive receipt corruption, and
refusal to overwrite a receipt. The receipt contains all checks and invoices;
default replay does not rewrite it.

From the repository root, standard-library Python 3.12:

```sh
python3 -I -B scripts/research_package.py --package research/qq16-output-bank-retention
python3 -I -B scripts/research_package.py --package research/qq16-output-bank-retention --check-only
```

The mathematical replay prints:

```text
PASS_QQ16_OUTPUT_BANK_RETENTION banks=240->224 scalar=17472->17280 native_mass=352 outputs=224 borrowed=224 controls=15 no_new_kappa
```

The registered command additionally runs six artifact tests and ends with
`PASS_REGISTERED_RESEARCH_PACKAGE ... outcome=completed`. Metadata/pin
success alone is not mathematical acceptance. No Lean or selected full cold
replay was run. The selected construction is unchanged.

## Task and overlap

Base main is `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, priority revision 4.
The claim is in [Discussion #2617](https://github.com/CrocSwap/integer-mult-bounds/discussions/2617).
The chooser selected recursive interfaces; task `joint-query-controller`,
scope key `0e34adbc1dd119161c3a`. [TASK.json](TASK.json) declares the changed
scope: take PR2540's concrete lifetime handoff instead of claiming a complete
global controller. This removes an intermediate allocation/copy, not the
sixteen retained observations whose fixed-interface need is established by
PR2511. PR2512/2524 address native L2 frames; PR2480 addresses a different
fixed-observation retention floor. Neither is being re-proved here.

## Open next questions

Can an actual caller reserve the sixteen selected Z banks before B1 with
favorable complete retention, movement, precision and consumer costs? Start
by assigning these exact output lifetimes to actual owners and streams and
compare the two schedules under the same tariffs. Global physical allocation,
child/output hosting and all-size admission remain blockers.

Can the sixteen owner-local scratch lifetimes use not-yet-produced Y output
slices? First establish the required owner-sweep access contract and inspect
future W writes. Scalar lifetime compatibility alone does not identify a
private local array with a full-cover bank. This package retains the original
scratch allocation and makes no claim about that extension.

## Credit

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.

Credit ywz65 for PR2540's complete native word, PR2511's logical decoder and
PR2512/2492/2468's native methods; Ross Richardson for PR2480; Sagar Thakrar
for PR2470; starship-s for PR2443; Ali Romman for QQ16; and the retained
supplier/geometry lineage. The copied predecessor artifacts retain their
original credit and Apache-2.0 license. Register coalescing is a standard
technique; the contribution is its exact chronological application and
verification at this decoder interface. No independent human review is claimed.
