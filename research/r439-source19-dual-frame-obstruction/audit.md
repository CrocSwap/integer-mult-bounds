# R439 phase-B block F508, source 19: an all-length obstruction

**Verdict.** Under the exact eleven-wire, arbitrary-dirty, reversible-XOR and monotone common-frame model in the request, **no exact implementation of the specified binary map can leave source 19 in a proper subspace of F508**. In fact, all eleven wires must leave the replacement block on F508. Consequently the original single-climb block invoice is minimal for every `0 < a < 1`, and the unchanged continuation plus literal inverse cleanup cannot turn a replacement into a complete paid-frame improvement.

There are two arguments:

1. A favorable **fully charged relaxation**, including an unavoidable carrier split and the source's delayed promotion, already has a strictly larger complete cost than the baseline.
2. A stronger **inverse-column dependency invariant** rules out the proposed low-source endpoint itself, for arbitrary finite circuit length and all rational proper subframes. It permits arbitrary temporary writes to source 19 and arbitrary carrier preparation.

The inverse-column support used below was already present in the predecessor's prefix calculation. The new step in this audit is the all-length invariant, not rediscovery of that support or the already-known forward-row obstruction.

No construction search was needed or performed. No particular finite frame alphabet or gate-length bound is assumed in either proof. The rank-three frame used in a positive test is only a test fixture, not a search restriction.

## 1. Scope, conventions and exact inputs

Write `q = 1-a`, so `0 < q < 1`. Drop only the common positive normalization: a positive rational-subspace rank increment `d` costs `d^q`. Set `0^q = 0` when writing endpoint formulas; zero increments are not billed.

A **block circuit** means any finite sequence of `dst ^= src` gates on the original register set

```text
R = [19,27,35,43,57,65,66,74,89,97,466].
```

Each gate has distinct operands. Both operands move to a common rational frame containing their previous frames. Frames are retained and can only grow by inclusion. Every replacement-block frame lies in `F = F508`. Proactive promotions are allowed and must be paid. There are no new registers, COPY/ERASE operations, or cross-block changes. The low-source condition concerns the replacement block; later inherited promotions are explicitly accounted for.

For an arbitrary independent dirty input column `x`, the block output is `Mx`. Rows, in the stated register order, are bit masks over **F2**:

```text
M = [1,767,509,891,927,943,765,1019,911,254,1914].
```

Bit `j` of row `i` selects input `R[j]`. This specifies the entire linear map, not a zero-initialized or clean-helper specialization. In particular, wire 466 is arbitrary dirty data, not a clean temporary.

The geometric labels live over **Q**, independently of the binary circuit field. Their supplied root coordinates are:

```text
19: (1, 0,-1, 0, 1, 0,-1, 0)
27: (1,-1, 0, 0, 0, 0, 1,-1)
35: (1,-1, 0, 0, 1,-1, 0, 0)
43: (1, 0,-1, 0, 0, 1, 0,-1)
57: (0, 0, 0, 0, 1,-1,-1, 1)
65: (1,-1,-1,-1, 0, 0, 0, 0)
66: (1, 0, 0, 1, 1, 0, 0,-1)
74: (0, 1, 0, 1, 1, 0,-1, 0)
89: (0, 0, 1, 1, 1,-1, 0, 0)
97: (0, 1, 0, 1, 0, 1, 0,-1).
```

`F` is their rational span. The checker independently verifies that

\[
B=(L_{19},L_{27},L_{35},L_{65})
\]

is a basis for `F`. Its ordinary dot-product Gram matrix is

\[
\begin{pmatrix}
4&0&2&2\\
0&4&2&2\\
2&2&4&2\\
2&2&2&4
\end{pmatrix},\qquad \det=64.
\]

Under the stated ham pairing `⟨x,y⟩/2`, the Gram determinant is `64/2^4 = 4`. In either convention the rational rank is four. No reduction modulo two is used to calculate these spans or determinants.

The entry labels `S_i` are exactly:

| Register | Entry frame | Rational spanning roots | Rank |
|---:|---:|---|---:|
| 19 | 152 | 19, 27 | 2 |
| 27 | 156 | 27, 97 | 2 |
| 35 | 159 | 35, 74 | 2 |
| 43 | 508 | all ten roots | 4 |
| 57 | 508 | all ten roots | 4 |
| 65 | 67 | 65 | 1 |
| 66 | 68 | 66 | 1 |
| 74 | 160 | 43, 74 | 2 |
| 89 | 155 | 27, 89 | 2 |
| 97 | 154 | 19, 97 | 2 |
| 466 | 508 | all ten roots | 4 |

There is no `L466`: wire 466 has the entry frame `F`.

The data above were supplied to the GPT-6 Pro research session and cross-checked against the pinned predecessor certificate [S2]. After that session, a separate local replay verified the compressed word SHA256 and Git blob, root coordinates, block frame, entry labels and actual slice against these constants. Section 10 separates this byte binding from the universal argument.

## 2. Start with a favorable, fully charged relaxation

This section deliberately gives a hypothetical low-source implementation the most favorable possible charges consistent with elementary necessary conditions. It does **not** posit a feasible circuit. It includes the unavoidable carrier cost, all other block-wire lower bounds, and any source promotion postponed into the unchanged continuation or cleanup.

### 2.1 Known forward dependency bound and baseline cost

The predecessor's forward invariant is that a wire's current frame contains the entry label of every variable present in its current row, and also its own retained entry label. Thus its exit contains

\[
S_i+\sum_{j:M_{ij}=1}S_j. \tag{1}
\]

For this map, independent exact rank calculations reproduce the exit lower bounds

```text
[2,4,4,4,4,4,4,4,4,4,4].
```

So all ten wires other than 19 must exit at `F`; this is predecessor evidence, not a new claim of discovery.

For any positive increments summing to `D`,

\[
\sum_k d_k^q\ge D^q,\qquad 0<q<1. \tag{2}
\]

Indeed, for `D>0`, each `t_k=d_k/D` lies in `[0,1]` and `t_k^q≥t_k`; sum and multiply by `D^q`. Equality holds only when at most one increment is positive.

The all-F508 baseline has six rank-two climbs, two rank-three climbs and three zero climbs:

\[
C_B(q)=6\,2^q+2\,3^q. \tag{3}
\]

The ten nonsource wires alone have the lower bound

\[
K(q)=5\,2^q+2\,3^q. \tag{4}
\]

This includes both rank-one-entry carriers and all rank-two-entry carriers. Repeated ADDs at an already attained frame carry no extra frame charge.

### 2.2 A low-source circuit must pay for a rank-three first contact

The source column of `M` is not an identity column; for example output 27 depends on input 19. Therefore a circuit implementing `M` cannot leave wire 19 untouched.

At the first gate involving 19, its common operand frame contains `S19 + Sj`, where `j` is the other original wire. This is true whether 19 is the source or the **destination**, and remains true after arbitrary prior carrier preparation or proactive promotions.

The exact joint ranks are:

| Other wire `j` | 27 | 35 | 43 | 57 | 65 | 66 | 74 | 89 | 97 | 466 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `dim(S19+Sj)` | 3 | 4 | 4 | 4 | 3 | 3 | 4 | 3 | 3 | 4 |

No first contact fits in the source's rank-two entry frame. Under the proposed rank-at-most-three restriction, that first common frame therefore has rank three, and source 19 must exit at rank three. It pays exactly one unit of rank growth within the block, costing `1`.

The first carrier belongs to `{27,65,66,89,97}`. Its entry rank `e` is one or two, it must reach rank three at the contact, and (1) subsequently forces it to reach rank four by block exit. Thus that carrier alone incurs, beyond its single-climb baseline:

\[
\delta_e(q)=(3-e)^q+1-(4-e)^q.
\]

In particular,

\[
\delta_2=2-2^q,\qquad
\delta_1=2^q+1-3^q.
\]

Strict concavity at the midpoint of `1` and `3` gives

\[
2\,2^q>1+3^q,
\]

so `δ1>δ2`. A rank-two carrier is therefore the most favorable case; such a first-contact entry exists, e.g. wire 27. Grant that best case and grant every other nonsource wire its single-climb minimum. The block cost in this favorable relaxation is at least

\[
K+1+\delta_2
 =4\,2^q+2\,3^q+3. \tag{5}
\]

All further carrier splitting would only add cost. We intentionally do not require that the favorable carrier choice can realize the target matrix or support all subsequent source interactions.

### 2.3 Charge the delayed source promotion, including cleanup

Let `G` be the first later prescribed frame visited by source 19 after the block. An inherited final promotion is counted as a visit when applicable. If there is no earlier continuation use, literal inverse cleanup supplies a visit: the inverse map cannot omit this essential wire, and that cleanup is at its prescribed common full frame.

In the original word `F⊆G`; let `g=dim G`. The geometry is in `Q^8`, so

\[
4\le g\le8.
\]

The baseline source's first later climb costs `(g-4)^q`. The hypothetical low-source circuit must instead pay at least `(g-3)^q`. Subdividing that later climb cannot improve its cost by (2).

All other wires exit at the original `F` by (1), so their unchanged continuation is identical. After source 19 reaches `G`, its remaining prescribed frame sequence is identical too. Let `C_fixed(q)` include the unchanged prefix, all unaffected wires and inherited COPY charges, nonsource continuation, and the source's continuation after `G`. Those terms are **included and equal**, not discarded as free.

Consequently the complete baseline and favorable relaxed costs obey

\[
\begin{aligned}
C_{\rm old}&=C_{\rm fixed}+6\,2^q+2\,3^q+(g-4)^q,\\
C_{\rm relaxed}&\ge C_{\rm fixed}+4\,2^q+2\,3^q+3+(g-3)^q.
\end{aligned}
\]

Their difference satisfies

\[
C_{\rm relaxed}-C_{\rm old}
\ge 3-2\,2^q+(g-3)^q-(g-4)^q. \tag{6}
\]

For `0<q<1`, the unit increment `t^q-(t-1)^q` decreases with `t≥1`. The most favorable possible delay is therefore `g=8`, yielding

\[
C_{\rm relaxed}-C_{\rm old}
\ge D(q):=3-2\,2^q+5^q-4^q. \tag{7}
\]

This explicitly pays the postponed promotion even when it occurs only in inverse cleanup. No actual first-later-frame ID is needed because (7) covers every possible rank from four through eight.

### 2.4 Exact analytic certificate that the relaxation loses

We prove

\[
D(q)>0\qquad(0<q<1). \tag{8}
\]

Put `t=2^q`, so `1<t<2`, and put `c=log_2(5)`. The integer inequalities

\[
4<5,\qquad 5^5=3125<4096=2^{12}
\]

imply `2<c<12/5`. Define

\[
\phi(t)=3+t^c-t^2-2t.
\]

For `1≤t≤2`,

\[
\phi''(t)=c(c-1)t^{c-2}-2>0.
\]

Thus `φ'` is strictly increasing, but its value at the right endpoint is

\[
\phi'(2)=\frac52c-6<0.
\]

It follows that `φ` is strictly decreasing throughout this interval. Since `φ(2)=0`, we have `φ(t)>0` for `t<2`. Finally `φ(2^q)=D(q)`, proving (8).

For a readable exact instance, at `q=1/2` the lower gap is

\[
D(1/2)=1+\sqrt5-2\sqrt2>0.
\]

The code also encloses (7) by rational intervals at eight rational exponents using integer root calculations. Those finite controls are not the proof of (8); the analytic argument above covers the whole open interval.

**Conclusion of the pre-synthesis relaxation.** Even granting a hypothetical low-source realization optimal carriers everywhere else, its complete paid-frame bill would be strictly larger than the baseline. Thus substantial synthesis is already unwarranted for the requested improvement objective. The next section strengthens this to nonexistence of the low-source realization itself.

## 3. General all-length inverse-column frame invariant

### Theorem

Let `n` arbitrary independent dirty variables start in `n` original wires with rational entry labels `S1,...,Sn`. Consider any finite reversible XOR circuit with retained, inclusion-monotone frames, where every gate raises **both** operands to a common containing frame.

Let `T(t)` be the binary matrix mapping original input values to current wire values, and let `U(t)=T(t)^{-1}`. If `W_i(t)` is wire `i`'s current frame, then at every time

\[
W_i(t)\supseteq
S_i
+\sum_{j:T(t)_{ij}=1}S_j
+\sum_{j:U(t)_{ji}=1}S_j. \tag{9}
\]

The first sum is the familiar forward-row label. The last sum is the **inverse-column** label.

### Proof

Initially `T=U=I` and `W_i=S_i`, so (9) holds. A frame-only promotion preserves it by inclusion.

For a gate `d ^= s`, with `d≠s`, write

\[
E=I+e_d e_s^{\mathsf T}.
\]

Over F2 this matrix is its own inverse. Hence

\[
T'=ET,\qquad U'=(T')^{-1}=UE. \tag{10}
\]

The only changed forward row is

\[
T'_{d,*}=T_{d,*}+T_{s,*}.
\]

The only changed inverse column is

\[
U'_{*,s}=U_{*,s}+U_{*,d}. \tag{11}
\]

Both operand frames are promoted to the same containing frame `K⊇W_d+W_s`. Every surviving dependency in the changed row or column lies in the union of the corresponding old supports; the labels of all of them already lie in `W_d+W_s`. Binary cancellation can delete a dependency but cannot create one outside that union. The retained own labels are also in `K`.

Unchanged rows and columns retain valid containing frames; the nonoperands are unaffected. Thus (9) holds after the gate. Induction proves it for any finite number of gates. ∎

### Why this covers the previously open behavior

No step assumes that the exceptional source is never a destination. When it is a destination, the ordinary row rule updates its forward dependencies; when it is the source operand, the inverse-column rule updates its inverse dependencies. Both labels are retained in its frame throughout.

Carrier preparation, multiple exchanges, cancellation, temporary mixing of dirty inputs, or a later restoration of the source row do not invalidate (10)–(11). Arbitrarily long words are covered by the same induction, with no enumeration of words.

This is **not** an attempt to run the ordinary forward proof backward through descending frames. All of (9)–(11) are evaluated at forward time. That distinction is essential.

The binary coefficients merely select which rational entry subspaces must be included. They are not coefficients in a rational linear combination of root vectors, and the two coefficient fields are never identified.

## 4. Apply the dual invariant to source 19

Exact inversion over F2 gives the following rows in the original register order:

```text
M^-1 = [1,66,709,842,272,288,885,136,583,515,1033].
```

The checker verifies both `M M^-1 = I` and `M^-1 M = I`. Its column indexed by register 19 has mask `1861` and support

```text
[19,35,66,89,97,466].
```

Equivalently, in terms of standard coordinate columns,

\[
M^{-1}e_{19}
=e_{19}+e_{35}+e_{66}+e_{89}+e_{97}+e_{466}. \tag{12}
\]

In particular,

\[
(M^{-1})_{466,19}=1. \tag{13}
\]

Applying the inverse-column part of (9) at the endpoint forces

\[
W_{19}^{\rm exit}\supseteq S_{466}=F. \tag{14}
\]

Every allowed replacement-block frame is contained in `F`, so

\[
W_{19}^{\rm exit}=F. \tag{15}
\]

This contradicts the proposed rank-at-most-three endpoint. With monotone frames, it also contradicts keeping source 19 in any proper rational subframe throughout the block. This covers **all** such subframes, not just root-generated catalogue frames.

The identity row `M[19,*]=e19^T` does not rescue the proposal. It removes forward output dependencies, but does not remove the inverse-column requirement (14).

### Relation to the predecessor's calculation

The predecessor's simple prefix has donor mask `1860 = 1861 XOR 1`, with donors `[35,66,89,97,466]`. That finite donor calculation is inherited evidence and is not presented as new.

What changes the scope is (9): the same inverse column is a frame obligation for **every** legal circuit, not only for a source-star prefix followed by a source-avoiding residual. In particular, neither a prefix factorization nor a source-avoiding residual is required here.

### Exactly which hypotheses the feasibility obstruction uses

For the short contradiction (13)–(15), it is enough that:

- the current linear map is invertible and starts as the identity on the original independent dirty inputs;
- gates are the specified reversible elementary XORs on those wires;
- both operands share a containing frame, with no later frame descent;
- the fixed endpoint has `(M^-1)[466,19]=1`;
- wire 466 enters with label `F`, and source 19 is required to remain in proper subframes of `F`.

The identity source row, the exact other nine geometric labels, and the exponent `a` are not needed for this particular feasibility contradiction. They are needed for the prescribed endpoint, the full invoice comparison, or the first-contact relaxation.

Removing a hypothesis can matter. For example, if only an ADD's destination were promoted, a high-frame `y ^= s` could leave `s` low despite its inverse column containing the initial high-frame wire. That is not legal in the stated model. If all entry labels were changed to a common proper frame, the same eleven-wire target matrix would have an ordinary XOR realization on that frame; the checker includes this changed-interface control and explicitly does not call it an admissible replacement.

## 5. Complete paid-frame optimality, not just low-source nonexistence

Combining the forward and dual bounds gives:

| Register | Forward forced rank | Dual forced rank | Combined forced rank |
|---:|---:|---:|---:|
| 19 | 2 | 4 | 4 |
| 27 | 4 | 4 | 4 |
| 35 | 4 | 4 | 4 |
| 43 | 4 | 4 | 4 |
| 57 | 4 | 4 | 4 |
| 65 | 4 | 2 | 4 |
| 66 | 4 | 4 | 4 |
| 74 | 4 | 3 | 4 |
| 89 | 4 | 4 | 4 |
| 97 | 4 | 4 | 4 |
| 466 | 4 | 4 | 4 |

Every exit frame is exactly `F`, not merely a different rank-four subspace: it is a rank-four subspace contained in the rank-four space `F`.

For wire `i` of entry rank `e_i`, its positive increments therefore sum to `4-e_i`. Equation (2) gives the lower bound `(4-e_i)^q`. Summing over **all eleven wires**, including all carriers, gives

\[
C_{B,\rm new}(q)\ge6\,2^q+2\,3^q=C_{B,\rm old}(q). \tag{16}
\]

Equality is attainable by the stated all-F508 baseline. It is also attained by the independently constructed 45-ADD positive fixture; that longer fixture is a checker control, not a shortening claim.

For `0<q<1`, any wire that splits a forced climb into at least two positive increments pays strictly more than its one-jump lower bound. In particular, a real circuit that visits rank three on source 19 and subsequently reaches its forced rank-four exit pays `1+1 > 2^q` on that wire alone. Scalar ADD count cannot compensate, because the objective here is the retained-frame invoice.

## 6. Unchanged continuation and inverse cleanup

There are two separate bookkeeping issues; neither is left implicit.

**Unchanged forward continuation.** Every replacement-block wire exits on the identical old subspace `F`, and the boundary data map is exactly `M`. No outside wire is touched. The unchanged subsequent gates therefore start from the same frame and data boundary. Every prescribed later frame visit, final promotion, and inherited charge is unchanged. There is no delayed source promotion left to exploit once (15) is imposed.

**Regenerated literal inverse cleanup.** The predecessor verifier specifies the applicable cleanup as the source/helper part of the reversed `A+B` word, performed at a common full cleanup frame [S3]. This block uses only source/helper wires. Replacing a block word by another word with the same `M`, and its corresponding cleanup slice by the literal inverse word, preserves the algebraic cancellation on all dirty inputs.

Every original block wire is essential: it has a nonidentity row or column in `M`. The same is true of `M^-1`. Any realization of either map must touch each such wire; otherwise both its row and column would be identity. Hence both the old and replacement inverse slices visit every one of the eleven wires at their prescribed common cleanup frame. With identical entry frames to that slice, each wire has the same first climb to the cleanup frame, if any; every repeated gate there costs no additional climb. Changing the number or order of gates within the inverse slice cannot reduce that frame charge.

Thus, writing `C_outside` for all charges outside the replacement slice,

\[
C_{\rm complete,new}-C_{\rm complete,old}
=C_{B,\rm new}-C_{B,\rm old}\ge0. \tag{17}
\]

The proof of (17) uses the fixed surrounding interface and prescribed full-frame inverse cleanup. It is not an assertion about arbitrary alternative continuation compilers, changed readouts, new registers, or cross-block rewrites.

For independent arithmetic controls, the checker appends the exact inverse of the positive fixture at synthetic common superspaces of ranks `g=4,5,6,7,8`. It verifies literal restoration and counts exactly eleven increments of rank `g-4` when `g>4`, and none when `g=4`. These are clearly labeled **synthetic continuation fixtures**. They are not new replacement-block operations outside `F`, and they do not claim to reproduce the actual 661-wire continuation.

## 7. Exact checker and positive fixtures

`verify.py` uses only the Python standard library. Checks use explicit exceptions, not Python `assert`, and remain active under `-O`. The mathematical proof is in this document; code checks finite premises, symbolic endpoints, accounting, and controls.

The default run performs:

- Exact rational RREF and an independent Gram-determinant computation for the geometry; all entry, forward, dual, and first-contact ranks.
- Exact binary inversion and both matrix products; the critical inverse column and all eleven combined exit obligations.
- Integer premises for the analytic relaxation lemma and rational interval controls at eight exponents. No floating-point power comparisons are used.
- A deterministic Gaussian constructor of a 45-unit-ADD word for exactly `M`, using only the original eleven wires at `F`. Every prefix is checked against both dependency invariants; all positive frame increments are collected.
- A 47-ADD positive fixture with the prefix `19 ^= 27; 19 ^= 27` at
  `H_test = span_Q(L19,L27,L97)`, followed by the 45-ADD word. The first gate really changes the source row from mask `1` to `3`; the second restores it. Both operands are correctly promoted. The final full dirty map is still exactly `M`.
- All eleven symbolic dirty columns, all 2,048 binary assignments for the positive word and its inverse, the reflected block matrix, and both inverse composition orders.
- Fully charged synthetic inverse-cleanup fixtures and a changed-entry-interface proper-frame positive control.
- Every one of the six elementary oriented ADD updates for every matrix in `GL(3,F2)`: 168 matrices and 1,008 updates. This checks the implementation of the dual update rule; it is not a synthesis search or an all-length proof.

The 45-ADD fixture has block profile `{2:6,3:2}`. The 47-ADD source-destination fixture has `{1:4,2:4,3:2}`. The latter pays for both source and carrier splitting and is intentionally worse. `positive-fixture.json` provides the gate list, its frame, and the exact individual climbs. The constructor embedded in `verify.py` regenerates it without external data or opaque witness files.

## 8. Failure controls

The default run checks thirteen expected rejections:

| Control | What it guards against |
|---|---|
| Proposed rank-two source exit | Passes the old forward-only bound; fails the new dual bound |
| Proposed rank-three source exit | Same distinction for a genuine proper rank-three frame |
| Corrupt critical inverse bit | Rejects an incorrect inverse certificate |
| Singular map | Rejects loss of invertibility |
| Self ADD | Enforces distinct operands and reversibility |
| Extra register | Enforces the original wire alphabet |
| Block frame outside F | Enforces the geometric boundary |
| One-sided operand hosting | Rejects a low common frame for a high-frame source operand |
| Frame descent | Enforces retained monotone frames |
| Truncated positive circuit | Rejects an incorrect dirty endpoint |
| Omitted inverse gate | Rejects incomplete dirty cleanup |
| Omitted carrier climb | Rejects an understated paid histogram |
| Corrupted source bytes | Exercises the strict SHA256 pin checker |

An additional orientation control confirms that the **inverse row** of source 19 only yields rank two, while the **inverse column** yields rank four. Using the wrong orientation would miss the result.

The two low-source exit controls are endpoint-frame assignments, not alleged legal circuits. Their purpose is to exhibit the exact gap between the predecessor's forward rule and the new necessary condition.

## 9. Reproduction and executed tests

From the directory containing these files:

```sh
python3 -I -B verify.py
python3 -I -O -B verify.py
```

To generate a fresh standalone certificate and positive fixture (without the optional source-byte result):

```sh
python3 -I -B verify.py --json fresh-certificate.json --fixture fresh-positive-fixture.json
```

To reproduce the shipped source-bound certificate, include `--word` with the pinned existing word as in Section 10. The certificate records the executing Python version.

The expected first line is:

```text
PASS_R439_F508_SOURCE19_DUAL_BARRIER
```

The Pro research session ran normal and optimized isolated checks with Python 3.13.5. Separate local replay ran both on Python 3.12.14, macOS arm64, with exit status zero and empty stderr (1.302 s and 1.381 s). The local normal/optimized certificates and fixtures were byte-identical. Against the delivered Pro output, the fixture matched byte-for-byte; the certificate and stdout differed only in the Python-version field/line. All thirteen failure controls rejected their intended mutations. A third optimized run with the pinned compressed word passed in 1.391 s; its certificate is the shipped `certificate.json`. These are execution and finite-certificate checks, not independent review of the universal proof. The unchanged verifier SHA256 is `7821c2888b56f411c9ec1d982d73e2afb4de2f16543505a3a3bd6e64d94df3b0`.

**No** synthesis search, complete 661-wire dirty replay by this checker, supplier/native test, independent human mathematical review, or proof-assistant run is claimed. The source-byte adapter was executed locally as described below. The proof's universal quantifiers come from §§2–6, not from the finite controls.

## 10. Source provenance and optional original-word audit

Pinned research context:

```text
Main base:        410026dc5513b87db92ae98571d1d5984c69a983
Predecessor:      PR1368
Predecessor head: 6ae784908c57f3aa5a2165d382b21a40accdf7a6
Geometry/word:   bce54fb3f895cbe5cd4c0eb477c3afeed100190f
Word path:       research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz
Git blob:        85a4499bf9e4911a705d50567a2c2ef6cf23739a
SHA256:          e3e301e62bc2b41dbf1ceac0acf3d35824ebeab1848c5a2142d4577b109da52f
```

The Pro session read the pinned README, certificate, verifier and source manifest for the relevant block, invariants, billing and cleanup contract. Local coordination separately fetched the exact PR1368 head and checked those source bytes. The certificate's block-508 record agrees with the register order, matrix rows, entry ranks/IDs, 37-ADD count and inherited prefix support. `SOURCES.json` records the public predecessor commit, blobs and SHA256 hashes; this external attribution metadata is separate from the generic hook's source validation.

The compressed word was unavailable inside the Pro research session. The later local replay supplied the unchanged repository artifact and freshly verified both its SHA256 and Git blob, matching the pins above. The runtime input remains at its existing repository path; this package does not copy the gzip or import predecessor code.

The default standalone checker reconstructs the explicitly supplied matrix and frames without external data. To repeat the additional source-byte binding, use:

```sh
python3 -I -B verify.py \
  --word /path/to/integer-mult-bounds/research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz
```

The read-only adapter passed locally: SHA256 and Git blob, root coordinates, `F508`, entry labels after `D,A,B[:205]`, the actual 37-ADD `B[205:242]` matrix and profile `{2:6,3:2}`, and literal full-frame cleanup shape all matched. Source 19's first later visit is `C[372]`, frame 1, rank eight. This adapter does **not** run the entire original word's dirty semantics. The registered optimized replay includes `--word` and declares this existing pinned file as a live input; the standalone default remains self-contained.

### Primary source links

- **[S1] Predecessor README, pinned head:**
  <https://github.com/CrocSwap/integer-mult-bounds/blob/6ae784908c57f3aa5a2165d382b21a40accdf7a6/research/r439-bblock-frame-barrier/README.md>
- **[S2] Predecessor certificate, pinned head:**
  <https://github.com/CrocSwap/integer-mult-bounds/blob/6ae784908c57f3aa5a2165d382b21a40accdf7a6/research/r439-bblock-frame-barrier/CERTIFICATE.json>
- **[S3] Predecessor verifier, pinned head:**
  <https://github.com/CrocSwap/integer-mult-bounds/blob/6ae784908c57f3aa5a2165d382b21a40accdf7a6/research/r439-bblock-frame-barrier/verify.py>
- **[S4] Predecessor source manifest, pinned head:**
  <https://github.com/CrocSwap/integer-mult-bounds/blob/6ae784908c57f3aa5a2165d382b21a40accdf7a6/research/r439-bblock-frame-barrier/SOURCES.json>
- **[S5] Underlying pinned compressed word:**
  <https://raw.githubusercontent.com/CrocSwap/integer-mult-bounds/bce54fb3f895cbe5cd4c0eb477c3afeed100190f/research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz>
- **[S6] Predecessor handoff:**
  <https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18911407>
- **[S7] Nearby claim identified in the request:**
  <https://github.com/CrocSwap/integer-mult-bounds/discussions/1163#discussioncomment-18911525>
- **[S8] Main base:**
  <https://github.com/CrocSwap/integer-mult-bounds/tree/410026dc5513b87db92ae98571d1d5984c69a983>

The repository work was coordinated in [Discussion 1470](https://github.com/CrocSwap/integer-mult-bounds/discussions/1470), following the linked handoff and the nearby claim that deferred source 19. The initial claim recorded the overlap coverage and limits. The prepublication refresh on 2026-10-14 at 01:53-01:54 UTC covered 753 open PR bodies and 183 Discussion records with complete pagination and no warnings; it found no new matching inverse-column/source-19 result. Claim1470 had no comments and PR1368 remained at the pinned head. This is metadata overlap coverage, not a global novelty certificate.

## 11. Credit, licensing and remaining limits

Retain predecessor credit to **Arham Tahir**, with substantial **OpenAI Codex assistance**, for the Apache-2.0 `r439-bblock-frame-barrier` package, its forward dependency argument, exact data and prefix calculation. Retain the supplied lineage: **Aaron Wang / PR1015; Ross Richardson / PR923; Sagar Thakrar / PR1062; Sricharan Vagvala / PR967; Gareth Davidson / PR915 and PR926; DreamingOfClouds / PR589; eumemic / PR555 and PR543**. The predecessor also credits Seth Burkart / PR886 and Ian Libanio / PR933.

Prepared by Andrey Mas with substantial GPT-6 Pro assistance through ChatGPT for the mathematical argument and checker. Codex handled source coordination, mechanical packaging and separate local execution. The checker is independently written relative to PR1368 and does not import or redistribute its implementation; its bytes are unchanged from the Pro handoff. This audit's provenance, reproduction and attribution paragraphs were updated during packaging; its mathematical content is unchanged. Apache-2.0. No independent human mathematical review or proof-assistant formalization is claimed.

The result is confined to the fixed block, original wire/interface conditions and paid-frame model above. It does not settle block 509, the already-treated other eight blocks, an enlarged seam, new registers, nonmonotone frame reuse, different operation rules, different targets, or changed continuation compilers. Inherited **H2/K bit-interface, native/hosting, precision/tape, all-size realization and analytic-transfer obligations remain separate**. No physical hosting, supplier adoption, kappa improvement, or selected-frontier change is inferred.
