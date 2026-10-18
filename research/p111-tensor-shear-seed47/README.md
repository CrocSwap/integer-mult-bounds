# P111 two-factor decoder: elementary shears cannot reduce pairing cost

**Scoped finite negative result. No new kappa or physical supplier.**

For the actual 111-line geometry in the selected PR589 word, this package constructs its rank-nine binary label decoder from the literal Gram matrix. It then checks every one of the **6,480 ordered elementary GL(81, F2) shears** of the resulting two-factor product basis. None lowers its pairing-rank sum below **3,969 = 63 squared**. The baseline attains that value. This is a one-step neighbourhood result, not an optimum over arbitrary GL(81, F2), several shears, changed decoder matrices, or physical delivery programs.

The copied-information functional is the sum, over scalar totals, of the rational rank of the source-label/reader-label pairing matrix. The cost of implementing preparation, source access, frame changes, copies, restoration and recursive children is not supplied. Granting these additional expenses zero does not make any tested shear improve this functional. No outer assembly or kappa improvement is claimed.

## Reproduce

From this repository root, Python 3.10+ and standard library only:

```sh
python -I -B research/p111-tensor-shear-seed47/verify.py
```

Expected final output:

```text
PASS_P111_TENSOR_SHEARS ordered=6480 cost=3969 direct=17 controls=7 no_new_kappa
```

The verifier checks the immutable selected word hash, exact rational ranks of all 511 nonzero code supports, all 12,321 depth-one decoder coefficients, all 6,480 ordered shears and both changed totals per shear. Seventeen cases also use a separate direct port-pair row constructor over the 111-by-111 universe; it stops when a nonsingular 49-row minor is established, rather than computing every row. The modular prime is checked. Nonzero modular minors certify rational lower bounds. Claims do not rely on floating-point rank estimates.

CERTIFICATE.json records the complete-domain digest, source and reader codewords, span dimensions, cost lower-bound histogram, direct checks and controls. Full default replay compares every receipt field canonically, rejecting duplicate keys, nonfinite JSON and bool/integer substitutions. SOURCES.json has an exact mandatory input inventory. The mutable current selection is not a replay dependency.

## Exact model and proof

Let x_0,...,x_110 be the literal integer eight-dimensional vectors in PR589; each has squared norm four and every dot product is even. Define B_ij=(1+x_i dot x_j/2) modulo two. Binary elimination verifies rank(B)=9. All 511 nonzero words in its column space are enumerated. Their rational physical support-span dimensions are exactly nine of dimension seven and 502 of dimension eight. The nine dimension-seven words are an independent reader basis v_0,...,v_8. Unique binary coordinates give source words u_t with B=sum_t v_t u_t^T. Every source-reader pairing has rational rank seven, independently certified by a nonzero modular minor and its seven-column upper bound.

In B tensor B, the 81 terms have source words u_i tensor u_j, reader words v_i tensor v_j and pairing rank 7 times 7=49. For distinct terms a and b, the tested elementary shear replaces u_a by u_a+u_b and v_b by v_b+v_a over F2. The two cross terms cancel, so the decoder remains exactly B tensor B. The checker exhausts all 16 assignments to the four symbolic source/reader bits, and rejects omission of the dual update.

Only totals a and b change. For each, the constructor divides first-factor and second-factor ports into four categories according to membership in the two original supports. The XOR tensor support is the union of category rectangles satisfying a_0 b_0+a_1 b_1=1 over F2. For each rectangle, the span of its tensor label rows is the tensor product of the two local spans. Replacing local category rows by an exact rational basis therefore leaves the resulting pairing row space unchanged. Projection against a basis of the fixed opposite support also leaves the pairing rank unchanged. All resulting matrix entries are integers.

For each of the 12,960 changed terms, modular elimination over the checked prime 65,521 produces rank at least 49. A nonzero 49-minor modulo a prime is a nonzero rational minor. The unchanged 79 terms each cost 49; hence each tested shear costs at least 79 times 49+49+49=3,969. Some source spans have dimension eight, so the receipt deliberately records **lower bounds**, not unsupported exact ranks for every changed term. This is a completed finite certificate, not a failed heuristic search.

## Attribution and overlap

PR620 (Joel Pulikkan / GamingPuzzled) reported the depth-one P111 floor and basis approach. PR757 (Russell Seligmann / rseligm2) and PR761 (Cody Harris / VibeCodyH) supplied solver-free depth-one pairing-floor proofs and source-order corrections. No priority for the value 63 is claimed. PR631 (Chi Zhao / vectorsss) proves much broader one-factor puncture obstructions. PR765 (@Mister-Meeseeks) proves a full-unit, unpunctured tensor theorem with cost 72^d and explicitly excludes punctures. Our fixed, punctured, two-factor elementary-shear census neither reproves that theorem nor extends it to arbitrary tensor recoding.

The selected source retains DreamingOfClouds' PR589 transport tuning, eumemic's PR555/493 bit supplier and the earlier E8/paired-cube lineage. PR966/971/979 concern prescribed star-target deletion thresholds; PR968 concerns complex frame-pair decoders; PR845 concerns one added complex total. None is this bit tensor-shear class. Recent PR998 concerns complex projections and PR993 incident-safe frame dimensions. References and observed scopes are recorded in OVERLAP.json.

Exact base: 8bddbee377e2f3ce1f1247196c4b290d55767d20. Assignment seed47 selects this structural-decoder round and the extra direct-check pivot term47; it is not evidence of novelty. Selected kappa at the base is 0.001661960547713947 (PR942), unchanged. Native C++ replay, selected supplier cold replay, repository-wide make verify, hosted CI and proof-assistant checking were not run; none is needed for this isolated standard-library matrix census. Inherited physical/compiler/hosting/precision/tape and analytic obligations remain open.

Prepared for **@woklerx** with substantial **OpenAI Codex assistance** in research, proof, implementation and verification. The separate matrix constructors are not independent human review. Apache-2.0.
