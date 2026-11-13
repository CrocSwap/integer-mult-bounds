# Integer shifts need four cubic-repair queries at 82 odd-S arities; general frames give twenty new three-query arities

**Scoped proof with a complete finite classification and exact certificates;
no new κ.** Prepared by ahrazzle with substantial AI assistance. Apache-2.0.

This addresses Open next question 1 of Nick Petalas's
[PR6653](https://github.com/CrocSwap/integer-mult-bounds/pull/6653): do
`r = 15, 22, 24, 30, 31, ...` admit three dyadic queries? It also
answers, for one restricted alphabet, the restricted-family question in
apoursh's [PR7479](https://github.com/CrocSwap/integer-mult-bounds/pull/7479)
(Open next question 2). The setting is PR6200's fixed cubic reader. All `r`
children `y += a^3; a += b` are retained, and the arbitrary incoming sources
must be restored exactly to the eager endpoint `(Y + rA^3, A, B)`.

## Results

**A. The integer-shift alphabet needs four queries at 82 of the 99 odd-S arities up to 200.**
The integer-shift alphabet is PR6653's certificate alphabet with no reads of
`b`: only `a += k*b` with integer `k`, and only `y += q*a^3` with dyadic `q`.
Let `S = r(r-1)/2` be odd, and let three integer nodes satisfy PR6653's node
equation. Three lemmas then reduce the problem to a finite computation:

- In shifted coordinates `w = 6c - (2r-1)`, a mod-8 argument shows that
  exactly one node has the other parity.
- That node's weight must be a nonzero integer, which bounds the smaller gap
  below `2S`.
- The node equation factors as `(w_0+3x)(w_0+x+4y) = 3x^2 - M`, so each gap
  has finitely many partners.

Running the finite search over all 99 odd-S arities `3 <= r <= 200` gives:

| | arities |
|---|---|
| three integer-shift queries exist (34 node sets) | 3, 6, 7, 11, 19, 26, 27, 42, 50, 51, 62, 90, 91, 98, 114, 155, 162 |
| impossible; four suffice (certificate each) | the other 82, including **15, 22, 30, 31**, 34, 39, 43, 58 |

Every solvable arity is already in PR6653's classes or certificates. So
PR6653's bounded integer-direction search failed at 15, 22, 30 and 31 for a
structural reason, not because its window was too small. The exact
integer-shift minimum at those 82 arities is **four**.

This is a statement about the integer-shift alphabet only. 44 of the 82
arities already have three-query repairs in the general alphabet, for
example through PR6212's `b^3` query or PR6215's original-b family. For
the other 38, any three-query repair must query `b`, write `b`, or use a
non-integer shift.

**B. Twenty new three-query arities.** At

```text
48, 49, 57, 60, 69, 84, 88, 96, 105, 112, 120, 121, 124, 132, 133, 148, 169, 177, 184, 192
```

three dyadic queries repair the reader exactly in the general-frame contract
of [PR6212](https://github.com/CrocSwap/integer-mult-bounds/pull/6212) and
[PR7475](https://github.com/CrocSwap/integer-mult-bounds/pull/7475). Each
certificate has a literal program built from integer determinant-one shears.
With PR6212's lower bound, three is the exact minimum. None of these arities
is in:

- PR6653's prior-class table or its 17 certificates;
- PR7475 (`r = 24`);
- [PR7478](https://github.com/CrocSwap/integer-mult-bounds/pull/7478)'s Pell family.

Two of the rows are non-monic at 84, 105, 121, 132 and 148. The
certificates at 124, 169, 177 and 184 are integer-shift certificates whose
nodes lie outside PR6653's search window. Example, `r = 57`:

```text
D_57 = -(209/512)(5A-4B)^3 + (11039/512)(A+12B)^3 + (7543/256)(A+44B)^3
```

| r | rows `(u,v)` of `uA+vB` | weights | shears |
|---:|---|---|---:|
| 48 | (13,184) (1,-40) (1,24) | -47/1024, -1081/512, 105421/1024 | 8 |
| 49 | (5,-1217) (1,-141) (1,115) | 245/16384, -118139/16384, 43757/8192 | 8 |
| 57 | (5,-4) (1,12) (1,44) | -209/512, 11039/512, 7543/256 | 6 |
| 60 | (5,242) (1,-6) (1,74) | 295/1024, -4307/128, -2419/1024 | 8 |
| 69 | (31,963) (1,-35) (1,29) | 1955/65536, -523549/65536, -1803683/2048 | 8 |
| 84 | (11,-1235) (1,295) (7,2193) | -17513/2097152, 557345/8192, -348019/2097152 | 12 |
| 88 | (5,272) (1,-16) (1,36) | 29/32, -1073/32, -319/4 | 8 |
| 96 | (5,-208) (1,-48) (1,80) | -95/64, 36005/256, 11495/256 | 8 |
| 105 | (13,1396) (1,68) (7,-36) | 1001/262144, 4046315/65536, -53599/262144 | 12 |
| 112 | (19,-120) (1,56) (1,88) | -11/1024, 2933/128, 51985/1024 | 8 |
| 120 | (5,2781) (1,-263) (1,761) | 149345/1048576, -11044985/1048576, -1905785/262144 | 6 |
| 121 | (37,5067) (1,47) (7,73) | 605/2097152, 2424235/16384, -994015/2097152 | 12 |
| 124 | (1,259) (1,-765) (1,-253) | 4195571/262144, 291059/262144, -2243315/131072 | 4 |
| 132 | (19,-20806) (1,670) (7,-9390) | -9229/4194304, 201427/32768, 109385/4194304 | 10 |
| 133 | (11,1106) (1,-10) (1,102) | 77/512, -41459/512, -15257/128 | 8 |
| 148 | (19,-635) (1,-249) (11,1357) | -705257/67108864, 9538193/8388608, 3577049/67108864 | 14 |
| 169 | (1,340) (1,-52) (1,204) | -169/16, -31265/512, 36673/512 | 4 |
| 177 | (1,-2765) (1,-2253) (1,1331) | 2024231/262144, -431585/32768, 1428449/262144 | 4 |
| 184 | (1,84) (1,-160) (1,64) | 3013/4, -253/32, -23851/32 | 4 |
| 192 | (7,160) (1,96) (1,608) | -47177/65536, 2018297/8192, 35335/65536 | 6 |

Here `D_r = sum_i (A+iB)^3 - rA^3 = sum_j q_j (u_j A + v_j B)^3`. The programs
subtract these terms. Shear counts are explicit upper bounds, not
minimality claims.

After this package, the arities `r <= 200` with no known three-query
repair in any alphabet are:

- the 38 odd-S arities listed in `CERTIFICATES.json`, starting with 15, 22,
  30, 31, 34, 39, 43, 58;
- the even-S arities 40, 61, 141, 165, 168, 193 and 196.

[PROOF.md](PROOF.md) has the contract, lemmas and theorems.
[CERTIFICATES.json](CERTIFICATES.json) records all 34 node sets, 17
three-query, 82 four-query and 20 general-frame certificates, with their
literal programs.

## Evidence and reproduction

From the repository root, with CPython 3.12 and the standard library only:

```sh
python3.12 -B scripts/research_package.py --package research/cubic-odd-s-shift-floor
python3.12 -I -W error -B research/cubic-odd-s-shift-floor/verify.py
python3.12 -I -W error -B research/cubic-odd-s-shift-floor/independent_check.py
python3.12 -I -W error -B research/cubic-odd-s-shift-floor/build.py --check
```

The registered manifest runs both checkers twice, normally and under `-O`,
plus the byte-for-byte regeneration. Each check is explicit, so it stays
active under `-O`. Local times were about 60 s, 85 s and 95 s. The expected
markers are `PASS_CUBIC_ODD_S_SHIFT_FLOOR` and
`PASS_CUBIC_ODD_S_SHIFT_FLOOR_INDEPENDENT`.

- [verify.py](verify.py)
  - Authenticates the four pinned predecessor files and checks four textual
    anchors. These are PR6653's alphabet and substitution, PR6212's two-query
    and four-query statements, and PR6653's uncovered-arity list. It also
    rejects two in-memory byte mutations.
  - Reruns the complete search for Theorem A from scratch. It factors
    `3x^2 - M` for every odd gap `|x| < 2S` with a quadratic sieve and
    enumerates divisors.
  - Checks every certificate by exact coefficient comparison and weight-ring
    and contract checks. It recomputes the weights of integer nodes by
    Gaussian elimination.
  - Executes every program symbolically over all `r` retained children, and
    on dirty rational inputs.
  - Runs nine rejection controls. Among them, at `r = 12` the same search
    misses PR6653's same-parity certificate `(-21,-5,11)`, which shows that
    the odd-S parity lemma is load-bearing.
- [independent_check.py](independent_check.py)
  - Imports neither of the other scripts.
  - Takes the other route of PROOF.md's Remark: it enumerates the larger gap
    over divisors of `S(3x^2 - M)`, solves the node quadratic, and finds
    square roots by Cipolla's method.
  - Checks identities by evaluating both sides at six non-proportional
    points, summing the left side child by child.
  - Runs programs in its own interpreter, recomputes the predecessor
    arities, and rejects five mutations.
- [build.py](build.py)
  - Regenerates `CERTIFICATES.json`. The four-query certificates are the
    lexicographically first integer nodes in `[-12, 12]`.
  - Compiles the twenty general-frame rows into integer-shear programs.

The twenty general-frame rows and weights were found by an external search
that is not included. Acceptance replays only the exact certificates and
does not depend on that search. Theorem A, by contrast, is a complete
classification: its search is the proof, and both checkers run it in full.
The two checkers are separate AI-assisted implementations. Independent
human or proof-kernel review is not claimed.

## Scope and coordination

[TASK.json](TASK.json) keeps the original `joint-query-controller` card. It
declares a **changed** scope: a source-restoration and coefficient side
question, the same family as PR7475, PR7478 and PR7479, not a priced
supplier.

- Physical event prices, precision, routing and caller invoices remain
  unknown.
- Three queries need not be cheaper than `r` eager restoration shears.
- The selected result and its five framework assumptions are unchanged.

Canonical main was `e54523517d0f03e58352e647c403a5af3e525a57` on entry and
again before submission. Overlap checks:

- Every open PR head from #7480 through #7538 was fetched, along with the
  ledger's cubic PRs (#6200 through #6797) and PR7475, PR7478 and PR7479.
- The only concurrent cubic-reader work found is Nick Petalas's
  [PR7506](https://github.com/CrocSwap/integer-mult-bounds/pull/7506). It
  shows that any three-query repair at `r = 15`, in any frame, needs two rows
  of height above 64. That result and Theorem A are complementary: PR7506
  bounds all frames at one arity, while Theorem A excludes integer shifts of
  every size at 82 arities.
- `scripts/find_overlap.py --offline` found only the local cubic packages
  already cited.

These checks are leads, not a novelty certificate.

## Open next questions

1. **General frames at the 38 open odd-S arities, starting with r = 15.**
   - *Why it matters:* this is the remaining three-versus-four question.
     Theorem A shows that any such repair must leave the integer-shift
     alphabet.
   - *First step:* extend Lemma 3 to primitive rows with even `u` (dyadic
     shifts), where the mod-8 argument changes. Then combine it with
     PR7506's height bound.
   - *Blocker:* with non-monic rows, the weight that Lemma 4 makes integral
     need not be integral.
2. **Even-S arities 40, 61, 141, 165, 168, 193, 196.**
   - *Why it matters:* these are the only even-S arities `r <= 200` still
     open after this package.
   - *Local evidence (not packaged):* a C search found no three-query
     dyadic certificate with two integer nodes `|c| <= 12000` and the third
     row forced by the node equation, of any denominator.
   - *First step:* search two non-monic rows. Alternatively, test the
     squareness condition of the node equation for local obstructions.
   - *Blocker:* even `S` has no parity lemma, so no finite reduction is
     known.
3. **Prices.**
   - *Why it matters:* the four-shear integer programs at 124, 169, 177 and
     184 and the six-shear programs at 57, 120 and 192 are the cheapest
     candidates against `r` eager shears.
   - *First step:* price their weighted queries and shears under one pinned
     backend, using PR7475's event inequality.
   - *Blocker:* unpriced coefficient preparation, precision, routing and
     caller work.

These questions are also recorded in [TASK.json](TASK.json).

## Attribution

- Nick Petalas: PR6200 supplies the reader, defect and rational comparison,
  and PR6653 the node lemma, integer-shift alphabet, shifted coordinates and
  the open question.
- apoursh:
  - PR6212: the dyadic lower bound and general-frame contract;
  - PR6215: the original-b family;
  - PR7475: the `r = 24` general frame;
  - PR7478: the Pell family;
  - PR7479: local solubility.
- AAAmirinu's PR6246 and CubeJerry's PR6250 supply the power-of-two
  families.

Their results are cited and pinned, not re-proved, except where this
package re-checks a statement. The proofs, search, certificates and
checkers here were prepared with substantial AI assistance, as recorded in
TASK.json.
