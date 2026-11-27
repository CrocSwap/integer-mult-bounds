# Batch contraction for self-repairing Fourier templates

Status: **partial/enabling; proposed theorem with proof, pending independent review**. No new complete tape overhead bound.

Source pin: `openai/math@3344da59991ed94f9ba711217b29c1d760badfa6`.
Uses Fourier `build/repair.tex` (`lem:hermite-repair`), `kernel.tex` (product-of-queries identity and shared routing), and `binary.tex` (`prop:binary-template`). All paths lie under `preprints/The-logarithmic-exponent-of-finite-Fourier-transforms-November-24-2026/`.

## 1. Different recursion variable

The published finite template chooses a binomial window of width $O(\sqrt{m\log m})$ to make the exceptional fraction $O(m^{-3})$. It computes each full spectral conversion with $A$ one-axis calls. This construction instead permits a **constant** exceptional fraction and recurses on the number of independent rows, holding transform length fixed. It terminates the additional recursion explicitly.

The binary kernel's target and its diagonalizing Walsh transform are equivalent by input/output monomial maps. This closure is essential; arbitrary spectral decomposition alone is insufficient.

## 2. Constant-tail predictor

Give every shift $\beta\in\{0,1\}^m$ equal row multiplicity. At each frequency the shifted count $c$ has exactly the $\operatorname{Bin}(m,1/2)$ distribution across rows. Set

$$
B=\lceil\sqrt{2m}\rceil,\quad u=\lfloor m/2-B\rfloor,\quad v=\lceil m/2+B\rceil.
$$

Then Hoeffding gives

$$
\Pr[c\notin[u,v]]\le2e^{-2B^2/m}\le2e^{-4}<1/16.
$$

The strict inequality follows from $e^4>1+4+8+64/6+256/24>32$. The source integral interpolation on this window has degree $D=v-u\le2\sqrt{2m}+3$. The source matrix-root construction uses the least power of two $b\ge\max(2,D)$, hence $b<2\max(2,D)$. Four predictor applications suffice for binary Hermite repair. Thus the non-spectral part has $O(\sqrt m)$ pencil stages.

Duplicate the finite batch to make its width $W$ divisible by 16. Set the permitted error count to $s=W/16$, even when actual exceptional sets are smaller. The source Vandermonde lemma applies with this inflated budget. Both full-conversion phases have $h=2s=W/8$ rows. Every original row holds an independent input; no input occupancy is inferred from zeros.

## 3. Finite batch-contraction theorem

Fix an array size and target invertible linear map $U$. Suppose an exact finite repair program on $W$ independent rows:

1. Uses $aW$ smaller-axis calls outside its two full-transform phases, plus finitely many ordinary row operations.
2. Has two sequential phases, each containing $W/8$ applications of $U$ or known input/output monomial equivalents of $U$. The second may depend on the first.
3. Has a direct fallback for $U$ costing $A$ smaller-axis calls per row.

The bill $aW$ includes all predictor applications and every non-spectral smaller-axis call; $aW$ is an integer. For each integer $r\ge0$, there is an exact finite program on $W_r=W8^r$ independent rows with

$$
\frac{\sigma_r}{W_r}\le a\sum_{d=0}^{r-1}4^{-d}+A4^{-r}\le\frac43a+A4^{-r}.\tag{BC}
$$

All remaining operations are finite compositions of supplied row operations and monomial maps. Uniformity in a spatial parameter is inherited from the supplied programs.

### Proof

At depth 0 use the direct fallback on $W$ rows. For depth $r>0$, run the repair on batches of $W$ among the $W_r$ rows through its first conversion phase. Collect pending check rows in a fixed order. Their count is $W_r/8=W_{r-1}$. Apply the depth $r-1$ program to these rows and return them to their parent repair batches. Perform the spectral tables, then run the second conversion phase by the same procedure, and complete each repair.

The induction accepts arbitrary child inputs. Linear combinations and correlations among check rows therefore do not affect correctness. Conversion phases occur in their actual dependency order. No simultaneous execution is assumed.

Writing $C_r$ for calls gives $C_r\le aW_r+2C_{r-1}$ and $C_0=AW$. Divide by $W_r$ and use $W_{r-1}/W_r=1/8$. At depth $d$, the $2^d$ child calls have total row mass $W_r/4^d$. The tree is finite and direct fallback handles its leaves. This proves correctness, call count and uniformity by induction. No padding is required. QED.

For phase fraction $q=1/b$ with integer $b>2$, replace $8$ by $b$ and $1/4$ by $2/b$. This note selects $1/8$ to make divisibility explicit.

## 4. Binary Fourier application

Fix the finite routing parameters of the source, with arity $A=2(m+D_{\rm route}-1)$. For even slot width $f$, put $U=2^{-Af/2}D_2^{\otimes Af}$. The source product of queries has spectral multiplier $(-1)^{\sum_c X_c\cdot Z_c}$ and satisfies

$$
F=M_{\rm out}\,U\,M_{\rm in},
$$

where the $M$ maps are prescribed signs and a half-address interchange. Hence a repair program for $F$ computes $U$ after inverse monomial maps at its boundaries. Forward and inverse spectral conversions are both $U$, since normalized binary Walsh is self-inverse. The closure premise is thus proved from the source identity, without assuming a new fast transform.

Run the constant-tail predictor and repair independently at each source routing label. Total base width includes all labels. Both spectral phases still contain one eighth of the total rows, so regrouping is exact.

Let $R(m)$ bound calls per row in a routed pencil. Source equation `eq:kernel-pencil-cost` gives

$$
R(m)=C_{2,L}D_{\rm route}\big((1+\log q)^L+m q^{-(L-\lfloor L/2\rfloor)}\big).
$$

The new non-spectral bill is $a=O(\sqrt m\,R(m))$. Therefore

$$
\frac{\sigma_r}{W_r}\le O(\sqrt m\,R(m))+A4^{-r}.\tag{BC-F}
$$

If $D_{\rm route}=o(m)$ and $r=\lceil\tfrac14\log_2m\rceil$, then

$$
W_r\le8Wm^{3/4},\qquad \frac{\sigma_r}{W_r}=O\big(\sqrt m(R(m)+1)\big).\tag{BC-F2}
$$

The source one-shot calculation has $O(\sqrt{m\log m}\,R(m))+O(Am^{-3})$ at comparable fixed routing parameters. This removes the $\sqrt{\log m}$ factor from that **finite-template call estimate**. It does not prove a new final transform exponent or tape overhead envelope.

### Extension descent and full rate

Construct the base repair over the source's finite free cyclotomic extension, and unroll using that same extension throughout. Recursive reuse needs no new coefficients. After unrolling, expand every row in a basis over $\mathbb Z[1/2]$. Since the target has base coefficients and the program is correct on arbitrary extension-valued input, every basis component carries an independent input and receives its own transform. Expansion multiplies width and calls by the same rank and preserves their ratio. Pointwise scalar operations become fixed dyadic row matrices.

## 5. Expenses and limits

For fixed $m,L,q,r$, this is a finite binary template with the source's smaller-axis semantics. Row rewirings, pointwise passes and spatial reindexings remain physical operations; they are not free on tapes.

In the added recursion, child numerical volume is one eighth of its parent. Depth-first execution parks parent data and runs one child at a time. Parked volumes sum to at most $8V/7$, times the finite base workspace constant. This proves linear volume for **fixed parameters**, not a common parameter-independent space constant.

With fixed parameters, child transforms are unitary and every finite row map has bounded norm independent of$f$. The unrolled template therefore has a finite per-level norm bound and admits the source polynomial-gain argument when iterated in spatial arity. Those constants can grow with $m,r,W$; their growth is not bounded here.

A complete growing-parameter tape theorem still must pay for predictor generation, Clifford dimension, coefficient lengths, cyclotomic rank, tables, row movement, column reindexings, local passes, descriptors, batch filling thresholds, precision, norms, scalar preparation, carry recovery, a common visited-cell cap and parameter selection/scheduling. The factor $R(m)$ remains. A fixed excess above $\sqrt A$ compounds through spatial recursion. No endpoint or poly-$\log\log n$ tape bound follows yet.

## 7. Reading and provenance

Read in full: Fourier `intro.tex`, `repair.tex`, `kernel.tex`, `binary.tex`; tape `walsh.tex`; community `AGENTS.md`, `CONTRIBUTING.md`. Fourier `layers.tex` was partly inspected but is not used. No Lean build or complete paper audit is claimed by this route.

New contribution: finite batch-contraction composition, constant-tail application and its cost/space accounting. The predictor, Hermite repair, shared routing, monomial identity and extension linearization are from the pinned OpenAI source and its credited predecessors. Substantial AI assistance: ChatGPT research agent under @CubeJerry's direction.


## 8. Finite exact verification

Run from the repository root:

```sh
python -B research/moonshot-overhead-program/routes/route-b/verify_batch_contraction.py
```

The script uses exact integer arithmetic modulo 257 and a normalized
256-point binary Walsh transform. Its toy repair has four sign queries,
16 independent input rows, the exact parity predictor
$1-2(c-2)^2$ on counts 1,2,3, and two exceptional rows at every frequency.
Thus its phase fraction is 1/4, testing the general $b=4$ theorem rather
than the asymptotic proof's chosen $b=8$.

Checks cover the normalized monomial closure, all 4096 shift/frequency
prediction cases, one- and two-level unrollings on respectively 64 and
256 independent random rows (16384 and 65536 entries), the exact recursion
row-mass ledger, and a negative control discarding correction. The latter
mismatches 16328 entries and is rejected. An exact rational ledger separately
checks the $b=8$ geometric formula at depths 0 through 11.

The predictor is evaluated using direct Walsh transforms in this verifier.
The test therefore verifies the repair identity and recursive composition,
not Clifford realization, routing cost, asymptotics, norms or tape time.
The random arrays are reproducible finite examples, not an exhaustive
verification of arbitrary inputs; the all-input statement is proved above.
Results are recorded in `verification-results.json`.

## 9. Local-operation invoice (independent review addition)

Let the non-spectral part of the supplied base program use at most $bV$
ordinary row arithmetic operations on data volume $V$, with its fixed-width
row tables applied blockwise. Applying those same tables separately to
base batches, never replacing them with a dense global $W_r\times W_r$
table, gives

$$
B_r(V)\le bV+2B_{r-1}(V/8).
$$

Thus all internal non-spectral ordinary operations total at most
$(4/3)bV$, plus leaf work. The same bound applies to any additional operation
whose cost is bounded by a fixed constant times its current volume. This
is an arithmetic/local-row invoice. A physical operation is covered only
when its actual tape implementation has the stated linear-volume bound;
spatial permutations are not declared linear merely by being row maps.

Independent agent review: Route C checked the mathematical note and found
its two-phase recurrence, dependency order, exact divisibility, normalized
binary monomial closure and single-extension descent sound. The reviewer
suggested the blockwise local-operation invoice above. This is independent
AI review, not formal-kernel or human certification.
