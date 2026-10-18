<!-- SPDX-License-Identifier: Apache-2.0 -->
# A projected helper three-cycle has exact raw-identity XOR cost 13

**For CrocSwap/integer-mult-bounds, Discussion 1503. Prepared 2026-10-14.**

## The quantified result

**Theorem.** For every finite integer `k >= 3`, let `z0,...,z(k-1),y` be independently arbitrary dirty registers over `F2`. An allowed gate is exactly one scalar XOR `r_d += r_s`, with distinct existing registers, at unit cost. Let `R(w)` be the complete raw linear map, and let `P(w)` be the map obtained by **deleting the gates with destination `y` and replaying the remaining gates in order**.

Among words satisfying

```
R(w) = I,
P(w): (z0,z1,z2,z3,...,z(k-1),y)
       -> (z1,z2,z0,z3,...,z(k-1),y),
```

the exact minimum length is **13**. The same attaining identity works over every `F2`-module; the lower bound is already forced by formal independent `F2` inputs.

The lower bound is **computer-assisted**: a written, dimension-independent reduction to five registers, followed by an exhaustive radius-six paired-state calculation. It is not merely a four- or five-register optimum extrapolated to extra helpers. No extra-helper gap remains. It is not a proof-assistant formalization.

## 1. A literal attaining word

Write `a=z0`, `b=z1`, `c=z2`. Execute these gates chronologically:

```text
 1. a += b
 2. a += c
 3. b += a
 4. c += y
 5. y += b       [deleted only in the projected replay]
 6. b += y
 7. c += b
 8. a += c
 9. y += a       [deleted only in the projected replay]
10. b += y
11. y += b       [deleted only in the projected replay]
12. b += c
13. a += b
```

All additional helpers are untouched. There are no free operations or implicit restorations. Destination counts are `a:4, b:4, c:2, y:3`.

For formal input values `(A,B,C,Y)`, the two executions are as follows. Addition in the table is XOR. In particular, `Y` is **not** assumed zero.

| After step | Raw `(a,b,c,y)` | Projected `(a,b,c,y)` |
|---:|---|---|
| 0 | `(A,B,C,Y)` | `(A,B,C,Y)` |
| 1 | `(A+B,B,C,Y)` | `(A+B,B,C,Y)` |
| 2 | `(A+B+C,B,C,Y)` | `(A+B+C,B,C,Y)` |
| 3 | `(A+B+C,A+C,C,Y)` | `(A+B+C,A+C,C,Y)` |
| 4 | `(A+B+C,A+C,C+Y,Y)` | `(A+B+C,A+C,C+Y,Y)` |
| 5 | `(A+B+C,A+C,C+Y,A+C+Y)` | `(A+B+C,A+C,C+Y,Y)` |
| 6 | `(A+B+C,Y,C+Y,A+C+Y)` | `(A+B+C,A+C+Y,C+Y,Y)` |
| 7 | `(A+B+C,Y,C,A+C+Y)` | `(A+B+C,A+C+Y,A,Y)` |
| 8 | `(A+B,Y,C,A+C+Y)` | `(B+C,A+C+Y,A,Y)` |
| 9 | `(A+B,Y,C,B+C+Y)` | `(B+C,A+C+Y,A,Y)` |
| 10 | `(A+B,B+C,C,B+C+Y)` | `(B+C,A+C,A,Y)` |
| 11 | `(A+B,B+C,C,Y)` | `(B+C,A+C,A,Y)` |
| 12 | `(A+B,B,C,Y)` | `(B+C,C,A,Y)` |
| 13 | `(A,B,C,Y)` | `(B,C,A,Y)` |

This proves the upper bound uniformly in the number of idle dirty helpers. The checker also executes all 16 Boolean assignments independently, rather than relying solely on this table.

## 2. A target-write rank bound

**Lemma.** Suppose a raw identity word has one target and contains `m > 0` target-destination gates. Then

```
rank(I - P(w)) <= m - 1.
```

If `m=0`, then `P(w)=R(w)=I`.

**Proof.** Track the full matrices `R_t` and `P_t` of the raw and projected executions after each prefix, both starting at `I`. Put `D_t=R_t-P_t`; in characteristic two this is also their sum.

Let `v_i` be the full raw donor row immediately before the `i`th target write. It is a row vector of coefficients of **all** initial registers, not a particular register value.

At a retained gate with matrix `T`, both executions apply the same row operation, so `D` changes to `T D`. Its rows remain in the span of the old rows. At target write `i`, only the raw target row changes, and

```
D_new = D_old + e_y v_i.
```

Consequently every row of the final difference lies in `span(v_1,...,v_m)`. Meanwhile, the raw target row changes only at these writes. Its exact restoration gives

```
e_y + v_1 + ... + v_m = e_y,
so v_1 + ... + v_m = 0.
```

These `m` vectors therefore span a space of dimension at most `m-1`. At the endpoint `D=I-P(w)`, proving the lemma. No assumption is made about the donors being distinct or about how other registers were used. ∎

For the requested three-cycle, the nonzero rows of `I-P` are

```
e0+e1, e1+e2, e2+e0.
```

The first two are independent and the third is their sum. Thus the defect rank is exactly two in every dimension. **At least three target writes are necessary.**

## 3. Why arbitrarily many extra dirty helpers reduce to five registers

First recall the write-count observation from Gareth Davidson/@bitplane's pinned PR1420 proof [1, §3]. Every register written by a raw identity word must be written at least twice. Indeed, if a row were written exactly once, that write would add a nonzero donor row: every raw prefix is invertible. Since the destination row is never written again, it cannot return to its initial row.

Suppose, toward a contradiction, that a successful word has length `L <= 12`. Let `h` be the number of helpers that are written at least once. All three cycled helpers must be written, and the rank lemma supplies at least three target writes. Therefore

```
L >= 2h + 3,
h <= 4.
```

Only the three specified helpers, at most one additional helper, and the target can be written. This does **not** yet bound the number of source-only registers; the next argument eliminates those reads legitimately.

Let `S` be the set of written registers. It includes `z0,z1,z2,y`. Every register outside `S` has its initial row `e_j` at every prefix in **both** executions. Restrict each row in `S` to coefficients of the initial inputs indexed by `S`.

* A gate with both endpoints in `S` induces exactly the same XOR on these restricted rows.
* A gate with donor outside `S` adds the restriction of `e_j`, which is zero. It therefore induces the identity on the restricted rows.
* There are no gates with destination outside `S`, by definition.

By induction over the chronological gates, delete every gate whose source is outside `S`. The resulting word on `S` realizes exactly the restrictions of both endpoint maps. The raw endpoint is `I_S`; the projected endpoint cycles the three specified helpers and fixes the possible fourth written helper and the target. Projection still deletes precisely the target-destination gates, so this induction applies equally to the projected replay.

This is **coefficient restriction**, not an operational assumption that unused dirty inputs start at zero. Arbitrary outside-input contributions may have entered the full active rows temporarily; the induction establishes precisely why they cannot affect the retained-input coefficients. The new program itself consists only of legal XORs on independently arbitrary inputs indexed by `S`.

Its length is no greater than `L`. Relabel the possible fourth helper as `z3` and the target as register 4. When only three helpers are written, adjoin an idle arbitrary dirty helper `z3`. This padding is solely an embedding into a fixed search instance, not an allocation operation used by the word. A hypothetical short word in **any** finite dimension has now produced a word of length at most twelve on exactly

```
(z0,z1,z2,z3,y).
```

Accordingly, excluding this one five-register case suffices for the universal lower bound.

## 4. Complete finite exclusion of lengths at most twelve

### 4.1 The paired-state graph

Use states `(R,P)` with both matrices represented in full. The start is `E=(I,I)` and the required endpoint is

```
G = (I,C5),
C5 rows, as binary masks: (2,4,1,8,16).
```

For each of the 20 ordered distinct-register pairs `(d,s)`, the transition is

```
(R,P) -> (T_ds R, T_ds P)     if d != y,
(R,P) -> (T_ds R, P)          if d == y.
```

Every generator is an involution. The last chronological gate multiplies on the left. No helper block of the raw matrix is used as a substitute for `P`.

Let `B6` be the complete ball of radius six around `E`. A word of length at most twelve reaches `G` **if and only if**

```
B6 intersects B6 G,
```

where the second set is a **right** translate.

For the forward implication, split such a word into a prefix and suffix, each of length at most six. Let their paired endpoints be `b` and `v`; then `G=v b`. Reversing the suffix realizes `v^(-1)` in at most six gates. Hence `b=v^(-1) G` is in the intersection. Conversely, if `b=a G` with `a,b` in `B6`, then `G=a^(-1)b`; execute a word for `b` followed by the reversed word for `a`, using at most twelve gates. This argument also covers all shorter lengths, without padding by hypothetical free gates.

Right multiplication by `G` leaves `R` unchanged and replaces `P` by `P C5`. For a row of `P`, this changes its first three entries from `(p0,p1,p2)` to `(p2,p0,p1)`; other entries stay fixed. This is the specified orientation `z0<-z1, z1<-z2, z2<-z0`.

### 4.2 The enumeration and its complete termination

The supplied verifier enumerates every paired state through distance six. Every state at distance zero through five is expanded under **all 20** gates. There is no pruning by register use, cancellation, symmetry, presumed normal form, or desired endpoint. States at distance six do not need expansion to construct `B6`.

Both representations give these exact shortest-distance layers:

| Distance | New states |
|---:|---:|
| 0 | 1 |
| 1 | 20 |
| 2 | 260 |
| 3 | 2,670 |
| 4 | 22,988 |
| 5 | 174,676 |
| 6 | 1,221,368 |
| **Total** | **1,421,983** |

Each engine expands exactly **200,615 vertices** and **4,012,300 directed gate transitions**. Every one of the 1,421,983 right-translated states is tested for membership in the ball. The intersection has **zero states**.

This is a complete **bounded-radius** search, not a claim to have enumerated the full five-register paired group. Complete termination here means completion of all layers and transitions needed for the radius-six ball and all translate-membership tests.

### 4.3 Independently represented cross-check

The first engine stores two row-major binary matrices. The second stores, for each matrix, the literal output bit-vector for each of the five basis inputs: a column-major representation. It updates the destination bit in every input image whose source bit is one, rather than extracting and XORing matrix rows.

The second ball is generated separately. The verifier then transposes **every** first-engine state and checks exact membership in the second-engine ball. Equal cardinalities and the bijective encoding conversion give exact equality of the represented balls, not merely matching counts or hashes. The two engines also compute the right translate separately: row-entry permutation versus basis-image block permutation. Both intersection counts are zero.

For diagnostic reproducibility, the SHA-256 of the sorted row-major packed states, each serialized as a little-endian unsigned 64-bit integer, is

```text
6908a7c0d961c0d45d3d13784110accedf576171906acb69e0145481d727ef67
```

For this encoding, a matrix is `sum(row[i] << (5*i))`; a pair is `raw | (projected << 25)`. The hash and `certificate.json` are receipts, **not substitutes for the exhaustive calculation**. No stored search frontier or opaque witness file is needed.

The finite exclusion, combined with §3, proves the lower bound thirteen for every finite `k>=3`. Section 1 attains it. ∎

## 5. Reproduction, executed checks, and failure controls

All essential checks are explicit exceptions and survive Python optimization. No third-party packages or public checkout are required. From the extracted directory run:

```sh
python3 -I -B verify.py
python3 -I -O -B verify.py
```

Both commands run **all** semantic controls, both complete searches, the exact cross-representation comparison, and both empty-intersection checks. If the adjacent `certificate.json` exists, the recomputed result is compared against it. To write a fresh receipt after all checks:

```sh
python3 -I -B verify.py --receipt fresh-certificate.json
```

The code uses Python 3.10+ features; the registered replay uses Python 3.12. **Locally executed:** full normal and optimized `-O` runs on CPython 3.12.14, macOS 26.5.1 arm64, passed in 5.596 and 5.721 seconds. Peak resident memory was 337,051,648 and 332,972,032 bytes (about 321 and 318 MiB). Both outputs byte-match `certificate.json`; timings are observations, not promises. A separate optimized process changed the final witness gate `(0,1)` to `(0,2)` in memory, preserving a legal length-thirteen word, and was rejected with `thirteen-gate witness is incorrect`. All original files remained unchanged. See `REPLAY.json` for exact arguments, outputs and hashes. An AST check found no Python `assert` statements. These local results supersede reliance on research-session runtime self-reports.

The controls include:

* **Arbitrary dirty inputs and known positives.** All 16 assignments for the thirteen-gate word; separate literal checks of PR1420's credited five-gate elementary loop, six-gate sole-target loop, and seven-gate SWAP witness. The attaining word is also checked on every basis input in dimensions 4, 5, 6, 18 and 65, including all extra dirty helper columns. These tests corroborate, rather than replace, the uniform embedding argument.
* **Projection versus the raw block, and a falsely clean target.** The attaining word has raw helper block `I`, but projected helper block the three-cycle. Appending `a+=y` to it gives an invalid candidate that passes both endpoint tests on **every** assignment with initial `y=0`, but fails on a dirty target input. The verifier detects this false positive.
* **Missing restoration and orientation.** Deleting step 11 leaves a twelve-gate word with the **correct projected cycle** and all raw helper rows restored, but raw target output `Y+B+C`, not `Y`. This gate cannot be omitted from the cost. Reversing the thirteen-gate word gives the inverse cycle, not the requested orientation. Invalid self-XORs and out-of-range endpoints are rejected.
* **Noncommuting translation.** A separate GPT-6 Pro review supplied the reachable one-gate fixture `T=T_01`, with row masks `(3,2,4,8,16)`. The final checker tests right multiplication against `TC=(6,4,1,8,16)` and distinguishes it from `CT=(2,4,3,8,16)`, in both row and column representations. An identity-only check does not distinguish multiplication side. The complete registered optimized calculation passed after adding this control, preserving the certificate and state hash.

The two search engines were written in the same research session. Their different representations and exact set comparison are implementation cross-checks, not a claim of independent human review. The formal rank/restriction arguments are written mathematics, not machine-checked formal proofs. Standard trust in the executable interpreter and the displayed exhaustive algorithm is the computational component of the result.

The separate Pro review corroborated the all-dimension reduction and the meet-in-the-middle equivalence, conditional on the finite nonintersection premise. It did not receive or audit the search source and did not reproduce the five-wire ball. That premise is supplied by the separately recorded local replay, not by the review.

## 6. Credit, provenance, and scope

Gareth Davidson/@bitplane's PR1420 [1–3] supplies the prior all-dimensional joint-range theorem, the optimal five- and six-gate elementary loops, constructors, and the cited write-count observation. Its complete paired-state censuses cover `(k,q)=(1,1),(1,2),(2,1)`, not `(3,1)` or the five-register ball computed here. Its seven-gate SWAP witness is retained as a credited test, not presented as new.

The all-extra-helper SWAP result in Discussion 1476 [4] is a **separate finding**. The present three-cycle lower bound does not depend on its lower bound or repeat its census. @woklerx's PR1105 [5] is the earlier raw-feedback lineage; the additional lineage acknowledgments in the pinned PR1420 README are retained by reference. No prior elementary optimum, range theorem, or SWAP result is claimed as this contribution.

This artifact addresses only the scalar XOR model in the question and the scoped claim in Discussion 1503 [6], within the general projected-defect handoff [7]. No claims are made about rational signed alphabets, free scalar mixing, address-group operations, restored-permutation circuits with different raw endpoints, frames, hosting, selected suppliers, `kappa`, or an integer-multiplication theorem. The pinned predecessor files were read and byte-checked against their exact Git commit; this package does **not** replay the predecessor’s complete package or the selected supplier. Related coordination and the separate SWAP finding are linked below. The recorded overlap check does not establish comprehensive novelty.

Prepared by Andrey Mas with substantial **GPT-6 Pro assistance through ChatGPT** for mathematical research and checker authorship. Codex performed coordination, execution audit, mechanical packaging and separate local replay. This is AI-assisted work, not independent human review. **Apache-2.0**; see `LICENSE`.

### References

[1] Gareth Davidson/@bitplane, PR1420, pinned head `d19a944897714f2ecae72720b7dafc3e256f2f8d`, mathematical commit `dc6ba012c92470ea830e3b0ff2dab28fbd8126d8`, `PROOF.md`:
<https://raw.githubusercontent.com/CrocSwap/integer-mult-bounds/d19a944897714f2ecae72720b7dafc3e256f2f8d/research/projected-cleanup-fibers/PROOF.md>

[2] Pinned README, including general-defect handoff and retained credits:
<https://raw.githubusercontent.com/CrocSwap/integer-mult-bounds/d19a944897714f2ecae72720b7dafc3e256f2f8d/research/projected-cleanup-fibers/README.md>

[3] Pinned source directory, including the inspected `algebra.py`, `independent.py`, and `EXPECTED.json`:
<https://github.com/CrocSwap/integer-mult-bounds/tree/d19a944897714f2ecae72720b7dafc3e256f2f8d/research/projected-cleanup-fibers>

[4] Separate helper-SWAP finding, as identified in the research handoff:
<https://github.com/CrocSwap/integer-mult-bounds/discussions/1476#discussioncomment-18913057>

[5] @woklerx, PR1105, head `20a960b545f4b0ade4f26922ef686bd5eaf275f4`:
<https://github.com/CrocSwap/integer-mult-bounds/pull/1105>

[6] Scoped three-cycle claim:
<https://github.com/CrocSwap/integer-mult-bounds/discussions/1503>

[7] General projected-defect handoff:
<https://github.com/CrocSwap/integer-mult-bounds/discussions/1396>
