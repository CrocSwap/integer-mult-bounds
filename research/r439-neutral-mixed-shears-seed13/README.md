# Two individually neutral R439 moves save two ADDs together

**Finite bit-circuit construction and sharp restricted-neighborhood bound;
no new kappa.** On Sricharan Vagvala's frozen PR967 word, one restored target
XOR and one restored helper XOR each have zero complete saving separately.
Together they save two ADDs: **11,783 to 11,781**, with preparation and
restoration paid. Two is the largest possible saving for any one-target,
one-helper pair whose two individual savings are nonpositive.

This is evidence that strict individually-improving moves can miss a useful
mixed move. PR967 itself is not a one-sided local optimum. This package
claims neither the best known R439 count nor an unrestricted circuit optimum;
PR1122/1188/1208 already describe substantially shorter words in other classes.

## The exact word and invoice

Use zero-based local target and helper indices. After the frozen PR967
helper and target preparations, insert at frame zero:

```text
helper[215] ^= helper[52]    # physical register 437 ^= 274
target[3]   ^= target[99]    # physical register 114 ^= 210
```

Replace the middle matrix M by T M H, where the new target map is
`T = I + e_3 e_99^T` and the helper map is `H = I + e_215 e_52^T`.
Thus row 3 changes by row 99 and column 52 changes by column 215, using the
already transformed matrix. Restore the target and helper with the same two
gates in reverse order before the parent's remaining restoration.

Both T and H square to I over F2. For arbitrary dirty targets y and helpers h,
the middle update and restoration give

```text
(y,h) -> (T y,H h)
      -> (T y + (T M H) H h,H h)
      -> (y + M h,h).
```

This is a uniform binary linear identity. It makes no claim that the positive
integer transfer matrices are equal; their complete bounds are replayed.

| Complete local quantity | PR967 | Mixed word |
|---|---:|---:|
| Helper preparation/restoration, each | 221 | 222 |
| Target preparation/restoration, each | 306 | 307 |
| Middle target ADDs | 4,509 | 4,503 |
| D ADDs | 5,563 | 5,561 |
| Other ADDs | 6,220 | 6,220 |
| All ADDs | 11,783 | 11,781 |
| Forward positive maximum F | 72,847 | 72,847 |
| Reverse positive maximum B | 10,394,084 | 10,394,084 |
| Paid rank mass | 5,129 | 5,129 |

The complete invoice is `222 + 307 + 4503 + 307 + 222 + 6220 = 11781`.
Each unilateral word has 11,783 ADDs and also passes both precision guards.
No source access, helper, COPY, restoration or recursive child is deleted
without charge. The 2,911 MOVEs, nine COPY/ERASE pairs, all ordered frame
paths and paid histogram `{1:1323, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:19}`
are unchanged. The sufficient strict inherited tests give

```text
64 F^3 B^2 = 2672929057893220568931365420032 < 2^104
2^18 F^5 B^4 = 6276870480677531528435239117197771736166837152483102425088 < 2^192.
```

## Why two is a sharp bound in this class

Let `w` denote the number of ones in a binary matrix. For distinct target
indices a,b and distinct helper indices d,s, define complete unilateral
savings, including each gate and its restoration, by

```text
gT = w(M) - w(T M) - 2
gH = w(M) - w(M H) - 2.
```

Write `x=M[a,s]`, `y=M[b,s]`, `z=M[a,d]`, `t=M[b,d]`. Away from row a and
column s the two changes are independent. Subtracting their separate weight
changes from the joint change leaves exactly

```text
delta = (x XOR y) + (x XOR z) - (x XOR y XOR z XOR t) - x
gJoint = gT + gH + delta.
```

The 16 binary quadruples give `-2 <= delta <= 2`. In particular `delta=2`
requires `(x,y,z,t)=(0,1,1,0)`. Therefore, when `gT<=0` and `gH<=0`, every
pair has `gJoint<=2`. If `gT+gH<=-2`, it cannot improve the bill at all.
For the displayed witness both individual gains are zero and the four
entries are `(0,1,1,0)`, attaining two. Since this witness also passes the
complete precision tests, the sharp optimum in the **declared fixed
one-target/one-helper nonpositive-unilateral class** is 11,781 ADDs.
This does not include profitable unilateral moves, longer words, a different
starting basis, changing A/B/C, or a different frame or COPY schedule.
The parent's 221 helper and 306 target preparation gates are frozen literal
subwords: wrappers are not fused with them or cancelled across their boundaries.

## Completed domain and stopping rule

OS-random assignment seed **13** selected the bit-supplier track. The three
candidate tasks and the pre-experiment claim are recorded in [TASK.json](TASK.json)
and [Discussion 1418](https://github.com/CrocSwap/integer-mult-bounds/discussions/1418).
The seed fixes nomination order through SHA256 of ASCII `13:a:b:d:s`; it
does not establish novelty or partition the work into disjoint shards.

All **12,210** directed target moves and **192,282** directed helper moves
are scored. There are **2,334,050,706** pairs with nonpositive unilateral
savings. The proved interaction bound excludes **2,333,917,483** from strict
improvement. The remaining **133,223** pairs are evaluated explicitly:
**85** save one ADD and **six** save two. This is complete support coverage
by a bound plus enumeration, not literal enumeration of 2.3 billion matrices.

Nominees are ordered by descending joint gain, then the seeded digest, then
their indices. Exactly the first **32 of 91** receive full precision and
dirty-state replay; **eight** pass precision. The first nominee has a correct
endpoint but exceeds the 192-bit bound. The second is the selected witness.
No further descent, restart, retuning or composition was performed. Precision
classification of all 91 is not claimed and is unnecessary for the attained
two-ADD optimum.

## Reproduce and verification scope

From the repository root, using Python 3.12 and the standard library:

```sh
python3.12 scripts/research_package.py --package research/r439-neutral-mixed-shears-seed13
```

Expected output includes

```text
PASS_R439_NEUTRAL_MIXED_SHEARS ADDs=11783->11781 positive=91 trials=32 admitted=8 columns=661 controls=18 no_new_kappa
PASS_REGISTERED_RESEARCH_PACKAGE research/r439-neutral-mixed-shears-seed13 outcome=completed
```

`search.py` uses packed bits. `verify.py` imports no search code: it rebuilds
PR967 from the original PR589 D matrix, PR915 target recipe and PR967 helper
recipe using explicit sets; prices the helper move on changed columns;
and reconstructs each candidate in the opposite row/column order. It checks
all 661 arbitrary input columns, both complete orientations, semantic D,
COPY cleanliness and matching ERASE values for every one of the 32 nominees.
The unchanged source geometry checker and record exporter verify the final
candidate and the unchanged paid schedule. These are separate implementations,
not independent human review or proof-assistant verification.

Eighteen rejection controls cover each omitted wrapper, wrong directions,
missing middle correction, uncharged wrappers, missing interaction terms,
strict precision equality, an endpoint-correct precision overflow, source
inventory/hash errors and invalid receipt encodings. An endpoint-neutral XOR
pair is accepted and charged two ADDs. Default commands compare every decoded
artifact/receipt field. `search.py --write` and `verify.py --write-receipt`
explicitly regenerate only this package's artifacts. Gzip container bytes are
not used to judge regenerated mathematical equality.

The inherited syntactic **H2** and literal **K_equals_D** predicates still
fail; their checks are unchanged. Semantic D equality and H1/H3/H4/H5 pass.
Native multistage replay, changed whole-hosted emission, full supplier
invoices and outer assembly have **not** been performed. All-size/compiler,
common-label/mutable-source, hosting, precision/tape and analytic obligations
remain. No supplier adoption, multiplication-runtime improvement or new
kappa follows from this local circuit result.

## Sources, overlap and credit

Exact base: `cd91ac8e2652bfee6bf09da3b8724253bcf78f5f`.
[SOURCES.json](SOURCES.json) pins every consumed repository file by SHA256 and
Git blob. The selected record and catalogue are historical provenance, not
moving runtime inputs. The selected conditional result at the base is PR1094,
kappa `0.001672660197076918`, with unchanged PR589 bits and binding complex
supplier. Its source-binding baseline passed; its full cold replay was not run.

Sricharan Vagvala (@theon199), PR967
`c6caa79e6655d83780a3b70a1d658313126fb0b3`, supplied the frozen helper-star word.
Gareth Davidson (@bitplane) supplied PR915's target basis and PR926's two-sided
construction. Scott Woolsey Biggart's PR733 is an earlier two-sided mechanism
precedent. @woklerx's PR1040/1047 supply the adjacent one-target/one-helper
searches; they do not claim this mixed nonpositive-unilateral census. Sagar
Thakrar's concurrent PR1400 composes profitable helper shears on PR1047;
its twelve-step saving is not imported here. Other relevant adjacent work
includes Ross Richardson's PR965 and the shorter PR1122/1188/1208 circuits.
No priority is claimed for basis changes or binary XOR synthesis.

Predecessor reconstruction and literal-evaluator patterns adapt @woklerx's
[PR1040 verifier](../r439-target-retune-seed14/verify.py), under Apache-2.0
with its substantial Codex-assistance disclosure. The mixed census, interaction
bound, joint constructor and additional controls are supplied here.

DreamingOfClouds' PR589 tunes eumemic's PR555/543 supplier. The unchanged
geometry checker is eumemic's; the exporter is Dylan Crow's. Their source
notices, the [PR967 attribution](../r439-helper-stars-seed19/NOTICE.md), and the
retained E8, native, semantic-D and hosting lineage remain in place.
The repository's `upstream/`, selected frontier and frozen inputs are untouched.

Prepared by **Hanson Sun (@bbMisk)** with substantial **OpenAI Codex assistance**
in mathematics, implementation, verification and writing. New material is
under the repository's **Apache-2.0** license.

## Open next questions

Would a bounded mixed search on a pinned newer word find useful neutral-move
interactions? Recompute that word's middle matrix and complete invoice first;
the present two-ADD gain cannot be assumed additive to another construction.

Can the semantic D endpoint be admitted by the complete hosted bit interface?
The next check would bind the changed chronological cuts to actual emitted
hosting operations. The inherited H2/K gap and missing native/whole-hosted
replay prevent treating this local identity as provider admission. Structured
questions and blockers are in [TASK.json](TASK.json).
