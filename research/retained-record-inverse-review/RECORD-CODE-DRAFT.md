# Source-aware whole-record inverse audit

## Verdict, source and exposure

Qualified PASS for the fixed source word, valid recipe/data shapes and actual producer/ledger path. The local records and reverse dispatch recover the reached input state; no source implementation defect was established. This is an external written audit of Ali Romman's PR6546, not a new inverse/caller, retention floor, error theorem, inventory or all-column replay.

Exact source head `ff038070b8d122a43993f2b2524154323cc6b4d7`, directory `research/selected-absolute-stochastic-caller/`. Inert objects inspected:

| File | Git blob |
| --- | --- |
| sampler.py | 2f7ba4b7d01213beb2a3b070658617ff992e715e |
| PROOF.md | 178000008b30144cf607dabd0d1759056fd4a644 |
| produce.py | 5ed6163e903da47268a3ca44786126e6e978dff6 |
| ledger.py | 728b2901176f11de2958c0e296061755b7305727 |
| verify.py | aea6fd3df8b1d666cf963ce1e338a0a4074035aa |
| SOURCES.json | dc4e6683f6a58b47654bf93b2117ea31b8255ec6 |

Prior session05 scouting exposed the source PROOF/sampler/body; this role is source-aware, not fresh blind. No current peer or coordinator draft was read before sealing. No source/new scientific program, NumPy import/install, constructor, caller, source-word scan, all-column comparison, test, mutation, census, numerical experiment or kernel was executed. Only inert source and provenance metadata were read. Reading guard/producer code does not rerun their previously reported outcomes.

The source54 retained whole fields,578N residue bits,5952f+18592 seed bits,824 peak fields,22803-event/all-column results, error/score maxima and finite receipts remain author evidence. The6547/6594 recovery floors are not rederived. Error/concentration/precision claims are outside this audit.

## 1. Actual source-to-caller preconditions

`SOURCES.json` pins the canonical selected WORD.json.gz at Git22f9ab02d1b73ea0aa4b07ce445a14cc2602c760, SHA2567834725d9e34ee846a9ccc615221ea81e0201613938afa185d2eda0c9a6c232f, and the two native compiler/oracle inputs. This note read the binding, not the binary word or those predecessor program bodies.

`produce.main` loads that word, compiles its actual MOVE edge endpoints from nine-axis frames, requires recipe rank1..8, constructs/checks the fixed-size recipe matrices and writes JSON recipes. `verify.run` hashes its pinned inputs, loads the same selected word, runs that producer, then calls `ledger.analyze(word,bound['ranks'])` BEFORE `execute`. The relevant actual ledger gates are:

- MOVE matches old frame and owned flag, then updates the frame;
- INIT requires an unused owned label; CLEAR requires its live frame, then closes it;
- scalar q is nonzero, has power-of-two denominator and matches the target frame;
- noninteger SCALE has numerator±1; an integer SCALE is permitted by the guard;
- ADD/COPY source differs from target and has the same frame;
- selected COPY has coefficient1 and the prescribed owned/ideal-row premise;
- final live-owned set is empty and final frames/ideal endpoint are checked.

These guard implications bind the inverse's key hypotheses to the source's actual call path. No new22803-event validation is claimed. The fixed word/recipes and callback remain unmodified during the call. The callback supplies genuine in-range seeds and has no interfering side effects.

The theorem's input representation is a mapping of exactly the intended public labels to lists of N=512^f Gaussian INTEGER pairs, with common N and positive integer f. Current full-caller fixture construction in `verify.run` is explicit Python integers in lists of tuples, width1; the larger tensor fixture is a native call, not a complete all-width caller execution. The all-width conclusion is a composition argument under those shapes, not an assertion that the entire caller was run at every f.

`execute` is not a hostile-program/NumPy/shape admission API. For example its scalar ADD uses ordinary zip, and equal list lengths are an invariant, not independently checked at that line. Equal N holds initially by the theorem; INIT creates N, COPY preserves N, scalar operations preserve N, and native checks N, so this invariant closes on the declared path. A mismatched packet is outside that proof. Self-COPY would in fact be recoverable by the old-value record, although the selected ledger forbids it; ADD's distinct source is genuinely needed by the displayed subtract-inverse.

## 2. Pair and native inverse on arbitrary integer magnitudes

`sampler.pair`27–44 computes sum s and difference d. The correction vector c is a deterministic function of conserved s and the retained sign. When parity needs correction it is a signed unit on the odd sum component; otherwise it is zero. Subtracting c, applying i (or-i in inverse), then adding c keeps d in the parity class required for integer halves. The explicit even-numerator gate checks that property.

Writing R for multiplication by i, its difference map is `d'=R(d-c)+c`. The output sum remains s, so the inverse recomputes the SAME c from that sum/sign and uses `R^-1(d'-c)+c=d`. This is exact for every Gaussian integer input and either valid sign, without a fairness or size assumption. A changed inverse sign generally changes c and is not the same inverse.

`route`47–60 builds a phase-Z4 monomial permutation and checks its destination permutation. The actual nine-bit recipe domain comes from the source compiler, not arbitrary row widths. `monomial`63–76 applies that permutation independently on f nine-bit digits and adds their phase exponents; the inverse reads the same destinations and negates those phases. This is the literal tensor monomial inverse, with all global phases retained.

`native`79–92 checks positive integer f, N and seed count. Forward composition is right monomial, ordered pair layers, left monomial. Inverse starts with left inverse, reverses the layer INDEX order while retaining each original seeds[j], and ends with right inverse. Each layer consists of disjoint coordinate pairs and has the exact pair inverse. Therefore the composition reverses exactly for any valid retained signs and any f; this does not re-establish the recipe's intended source operator by an all-column comparison.

The sampler uses Python arbitrary-precision integers/lists, not NumPy fixed-width payload arrays. No fixed-int64 all-width payload-overflow claim is needed. NumPy int64 appears in the separate fixed512-coordinate producer comparison. Its range checks/unchanged oracle outcomes are inherited verification, not extended here to arbitrary f. Feeding NumPy scalars to the permissive helpers can change arithmetic semantics and is not the certified representation.

## 3. Signed quantization, ADD and SCALE records

For q=p/D in lowest terms with D positive, `quantized`95–98 computes `y=floor((p*x+u)/D)` in Python integers and checks a genuine in-range seed. The same u is used for every real/imaginary component in that stage; no independence across components is needed for exact inversion.

ADD's forward increment depends only on its distinct preserved source, coefficient and seed. After later instructions have been undone, that source has its exact forward-time value. Recomputing and subtracting the SAME increment reverses ADD; no per-component residue is needed. A self-ADD would not have that preserved-source invariant and cannot be silently included in the theorem.

For noninteger SCALE, let `r=(p*x+u) mod D`. Euclidean quotient/remainder give `p*x+u=D*y+r`, including negative x and p, because D>0. The actual source restriction p=±1 therefore gives exactly `x=p*(D*y+r-u)`. `pack_remainders`101–113 stores the real/imaginary residues in their sequential little-endian bit fields; `restore_division`116–133 reads the same order, checks length and unused high padding, and uses that identity.

Crucially bits=`D.bit_length()-1` is log2(D) only for power-of-two D. The pack/restore helpers do not independently check that condition; it is an explicit source proof premise and actual preceding ledger gate. They do check abs(p)=1 for fractional division. No promise for arbitrary denominators such as3 follows from their permissive call signatures.

For integer SCALE, u=0 and rounding is exact multiplication by nonzero p. Reverse first checks exact divisibility, then divides. Negative p is safe: a divisible integer's Python floor quotient is its exact quotient. The selected proof states signed powers of two, but the local inverse only needs a nonzero integer; the ledger forbids zero. The sampler alone is not a validator of every arbitrary integer coefficient/program.

## 4. COPY/CLEAR/INIT, reused labels and record aliasing

Every forward instruction appends its own record in chronological order, independent of reused field labels. COPY keeps the ACTUAL old destination list then installs a new source list, not merely its ideal zero value. CLEAR keeps the whole actual old field and removes the label. INIT requires that label absent and creates the all-zero N-vector. Forward COPY coefficient1 is checked locally as well as in the ledger.

Saved old lists are not later mutated through aliases in this execution path. COPY, ADD and quantized SCALE assign new outer lists. Monomial makes a new list before native pair updates; the Gaussian pairs are immutable integer tuples in the actual caller. INIT's repeated zero tuple is immutable. Initial/output snapshots also copy their outer field lists. Consequently storing `record=fields[r]` preserves the old numerical value without requiring a deep copy of mutable payload cells. External concurrent mutation or different component representations are outside the call contract.

After undoing all later instructions, the state is exactly the output of the current forward instruction. Reverse COPY checks its current equality with the restored source and reinstates its old destination. Reverse CLEAR requires the label absent and restores its saved value. Reverse INIT checks zero and removes the field. If a label was cleared, reused by a later INIT, and cleared again, the later lifetime is undone first; the earlier CLEAR then restores the correct earlier list. Records are indexed by event j, so reuse does not replace an earlier record under one label key.

This is a descending induction over the fixed word. The native/scalar inverses establish its local steps; COPY/CLEAR/INIT establish its ownership steps. It concludes exact recovery of the supplied initial mapping, as the final equality guard checks. `tape[j]=None` releases the stored slot only after its value is bound to the current local record; this does not change the record used for that inverse step.

## 5. What invertibility does and does not mean

The augmented forward endpoint plus its valid retained records determines the original input. Exact inversion holds for arbitrary valid supplied seed values; freshness/unbiasedness is a separate premise for the source's error theorem. The deterministic test callback is therefore not a randomness certificate. Later forward stages cannot infer fresh conditional randomness from replaying a retained seed.

The implementation restores fields and returns a separately copied output snapshot. It does not return a physical full-register permutation, restore every seed as fresh random tape, justify erasing those records for free or admit a reversible fixed-tape implementation. Setting Python record slots to None and releasing managed objects is not itself reversible hardware cleanup. In particular this audit does not call the returned initial fields alone an injective map of all original randomness; seeds/records are the information used by the inverse.

Arbitrary correlations among public inputs are allowed by the pointwise integer identities. They do not make output/record/input statistically independent. Arbitrary ambient physical fields and tape heads are not modeled by this indexed Python reference, so no physical spectator/owner return claim is fabricated from its dictionary equality.

## 6. Written weakening controls — UNEXECUTED

1. **Lost division residue:** at q=1/2,u=0, inputs0 and1 both round to0. Their residues distinguish them. Omitting the record destroys injectivity; this is already a source control theme, not a new observed result.
2. **Wrong signed division convention:** for x=1,p=-1,D=2,u=0, floor gives y=-1,r=1 and the source formula recovers1. Truncating that quotient to0 with the same residue instead recovers-1. Signed floor and nonnegative remainder must be paired.
3. **Unsupported scalar domain:** denominator3 is outside the dyadic contract and its residues need not fit bit_length(D)-1 bits. Fractional numerator3 is rejected by the source division-record guard. Integer zero is forbidden by the preceding ledger. None is a counterexample to the selected valid caller.
4. **Self-ADD:** x←x+x followed by subtracting the increment recomputed from changed x does not recover a general x. The actual ledger's source!=target gate is necessary for the shown ADD inverse. This does not allege that the selected word contains such an instruction.
5. **Discard old COPY/CLEAR value:** ideal-zero or owned labels can hold numerical error. Overwriting their actual old values without a record loses information; a final copied value or a public ideal identity does not reconstruct it for free. Event-indexed records are also needed across reused-label lifetimes.
6. **Wrong seed/order:** replacing a pair sign or scalar seed on reversal changes the quantizer/center; reversing a composed native without reversing its layer order requires an extra commutation identity not used here. Exact-grid examples can hide such errors, so the all-integer local inverse argument is the relevant obligation.
7. **Shape/dtype weakening:** scalar zip can truncate unequal field lengths, and fixed-width numerical scalar types can overflow. The theorem uses common N and Python integers; the actual initial builder and operation invariants supply them. No hostile packet validator is claimed.
8. **Freshness/physical overclaim:** recovering integer fields after consuming retained records does not supply a fresh entropy reservoir, record-erasure implementation, full-state hardware permutation, physical tape bound or the old fast-child tariff. These require different contracts.

No control was run and no source finite count, corruption outcome or error constant was newly certified.

## Conclusion and credit

The actual producer/ledger path supplies the crucial dyadic, nonzero, fractional-numerator, distinct-operand, frame and ownership preconditions. The literal sampler then has a complete compositional reached-state inverse under the stated shapes and immutable Python integer representation. No new large NumPy/source-word replay is required for this written implication, and none was performed. This is not arbitrary-program/API validation or a new full selected-caller numerical execution.

Credit Ali Romman6546 and6532/6526/6509, source native/compiler and rounding lineage; DreamingOfClouds6030 selected word; Cinna Davis4088/2226 representations; Nick Petalas6418/6438 ensemble/reuse work; zxv6066 stochastic-shear/restored-randomness warning; all original notices.6547/6594 retain their distinct recovery-floor results. Native all-columns, complete compiler/physical/stock/tape/precision/analytic/outer, accelerated child price, human/kernel acceptance and all five selected assumptions remain. No κ/frontier/adoption change or merge follows.
