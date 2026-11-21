# P104 decoder prices: a 2-adic subset bound

Status: paper proof with exact finite controls. The new deduction below is not
Lean-checked, and it does not prove the general decoder wall, a network or word
wall, or any kappa improvement. The pinned #7852 base for every source below is
`41beda1d6435760dc99e38bd7e65f36798aad212`.

## The operation being bounded

For each of 104 ports take the 9-bit label `q[t]` from upstream
`LinP104Base.lean`, with `Q[t,s] = parity(q[t] & q[s])`. Every label has odd
weight, so `Q[t,t]=1`. A finite rational decoder has coefficient columns
`W[:,k], U[:,k]` and must satisfy, exactly,

```
Q[t,s] * sum_k W[t,k] * U[s,k] = 1 if t=s, otherwise 0.
```

Let `D_k = {t: W[t,k] != 0}` and `G_k = {s: U[s,k] != 0}`. Its decoder mass
is `C = sum_k rank_F2(Q[D_k,G_k])`. This is the **binary pairing rank** of
each support rectangle, not the rational rank of an E8 signed Gram matrix.
`DecoderWall.lean` names this `rowPrice`/`mass`; its `pairing_rank_add_le`
relates an individual price to a frame climb under that theorem's additional
frame hypotheses. It is not itself the K17 weighted signed caller invoice.

The #7852 C2 theorem additionally assumes half-integer terms represented as
`w/2, v` with integer `w,v`, both linear mod 4 in a common lift of 8-bit
labels. The later 1001-cube DRAT claim assumes the *tight B-linear*
half-integer class, including one side restricted to values 0, ±1 and the
Z16 reduction. The PR explicitly excludes loose vectors and arbitrary
decoders. We did not replay its DRAT proofs or prove the paper class reduction.

## Bound for a larger coverage union

For a fixed valid decoder and a fixed finite set of rows, define the 2-adic
valuation `v2(0)=+infinity`. At any port define

```
alpha_t = min_k v2(W[t,k]),  beta_t = min_k v2(U[t,k]).
```

These minima are finite for a valid decoder. Call a port **locally integral**
if `alpha_t + beta_t >= 0`. For integer row exponents `lambda[k]`, one may
first change each row by the *exact*, support-preserving gauge

```
W[t,k] <- 2^lambda[k] W[t,k],
U[t,k] <- 2^(-lambda[k]) U[t,k].
```

**Claim.** If there is a subset `S` of ports which are all locally integral
after one such common choice of row gauges, then `C >= |S|`. Consequently,
any decoder with at least 56 such ports satisfies `C >= 56`; arbitrary entries
and ports outside `S` are allowed. This applies to nonlinear rational rows and
to denominators of any 2-adic order. It covers cases outside the previously
stated C1/C2 and tight-B-linear half-integer classes; it does not contain all of
those classes. Their union is therefore a strict extension of the coverage,
not a replacement for the existing stronger E8-specific theorems.

**Proof.** Work with the row-gauged decoder. For each `t in S`, put
`d_t=2^alpha_t`, `W'[t,k]=W[t,k]/d_t`, `U'[t,k]=d_t U[t,k]`. Both are rational
2-adic integers by the local-integrality condition. When `Q[t,s]=1`, their
pairing is `(d_s/d_t)` times the original one: it is 1 on the diagonal and 0
off it. Restrict to `S` and reduce every coefficient mod 2 (the denominator is
odd). With `A_k = diag(W'[:,k]) Q[S,S] diag(U'[:,k])` over F2, we obtain
`sum_k A_k = I_|S|`. Therefore

```
|S| = rank(I) <= sum_k rank(A_k)
    <= sum_k rank(Q[D_k intersect S, G_k intersect S])
    <= sum_k rank(Q[D_k,G_k]) = C.
```

Nonzero rational scaling preserves the supports, and restricting a matrix does
not raise its rank. This is the existing reducible-decoder rank argument
(`DecoderWall.mass_ge_card_of_reduction`), applied after the stated restrictions
and conjugations. It in fact works for every binary pattern with unit diagonal;
P104-specific geometry is not used in the proof. It does not assume
`Wall56`. The new reduction is given here as a mathematical proof, not a new
kernel certificate.

## Exact feasibility for a specified subset

For each `t in S` and each pair of rows `a,b` with nonzero `W[t,a]` and
`U[t,b]`, create a directed edge `a -> b` with integer weight
`v2(W[t,a]) + v2(U[t,b])`. The condition on row exponents is exactly

```
lambda[b] - lambda[a] <= v2(W[t,a]) + v2(U[t,b]) for every such edge.
```

These difference constraints admit integer exponents if and only if their
graph has no negative directed cycle. `probe.py` uses Bellman-Ford to test a
**given** subset and verifies the returned gauge against the exact rational
decoder. It does not claim to find a maximum feasible subset, solve the
general price-minimization problem, or certify unsatisfiability below price 56.
An individually negative diagonal contribution `v2(W[t,k] U[t,k]) < 0` is a
negative self-loop: that port cannot be included under any row gauge. This
obstruction concerns the displayed factorization; arbitrary row mixing may
change the factorization.

## Checked cases and important limitation

`probe.py` parses the pinned labels and 8-row E8 non-vacuity example; validates
all 10,816 pattern cells against the upstream 8-coordinate form; checks the
exact rational live-pattern identity, binary prices by two separate elimination
implementations, valuations, selected gauges, and the reduced identity and
rank chain. It uses Python fractions throughout. The examples are:

* 24 disjoint live pairs and 56 singleton ports. On each pair take the two
  columns of `A=[[1,1],[1,5]]` as W and the two columns of
  `A^(-T)=(1/4)*[[5,-1],[-1,1]]` as U. Each Q block is all ones; each row
  costs 1. The example has 104 rows, total mass 104, exactly 48 ports with
  negative self-loops under every row gauge, and 56 other ports. Its first
  pair has actual `-1/4` and `+1/4` live-cell terms that cancel; its W row is
  not a linear mod-2 function of the 8-bit P104 label. The selected-subset
  rank chain is exactly `56 <= 56 <= 56 <= 104`. Changing one coefficient is
  detected on both a diagonal and a live off-diagonal cell.
* Add a cancelling pair on another port. Now 49 ports are intrinsically bad
  and exactly 55 can be included. Mass is 106; this is **not** a counterexample
  to 56, only a checked boundary where this subset proof yields at most 55.
* A separate 25-pair example has only 54 raw locally integral ports, but the
  checked reciprocal row gauges make all 104 locally integral. Its mass and
  the resulting lower bound are both 104. Thus the gauge step enlarges the
  raw subset screen and preserves its actual price.
* The pinned `LinP104FreeInstBase` E8 decoder has 8 rows and costs 69 in this
  exact replay; 87 ports contain a negative self-loop. No row gauge can include
  those ports, so this method can use at most 17 for this particular
  factorization. It therefore does not subsume C2 or resolve the hard
  E8-shaped examples. The README's statement that an E8 decoder attains 56
  need not refer to this particular displayed basis; no claim about other
  choices is made here.

## Reproduction and provenance

```
cd .
python3 -I -B probe.py > results.json
git hash-object LinP104Base.lean DecoderWall.lean LinP104Free.lean LinP104FreeInstBase.lean README-upstream.md
```

Expected blob IDs, in order: `a95511ccdf40413fe91583870a41467bd004baf8`,
`5469e2f9ada727cd4216aa729b27434f3a243cd5`,
`5735da4e0a91bfb0745b6fd24a7bd039c772f3ea`,
`5de7230bdcdd41e05780bda04a67eadba4c36d1a`,
`1d331673d591c677ace54bdabf82d0e38b380a91`. `probe.py` additionally pins the
SHA-256 of both source data files. Source links:

* [DecoderWall.lean](https://github.com/CrocSwap/integer-mult-bounds/blob/41beda1d6435760dc99e38bd7e65f36798aad212/research/p104-lowerbound-toolkit/lean/Nov15/DecoderWall.lean)
* [LinP104Free.lean](https://github.com/CrocSwap/integer-mult-bounds/blob/41beda1d6435760dc99e38bd7e65f36798aad212/research/p104-lowerbound-toolkit/lean/Nov15/LinP104Free.lean)
* [LinP104Base.lean](https://github.com/CrocSwap/integer-mult-bounds/blob/41beda1d6435760dc99e38bd7e65f36798aad212/research/p104-lowerbound-toolkit/lean/Nov15/LinP104Base.lean)
* [LinP104FreeInstBase.lean](https://github.com/CrocSwap/integer-mult-bounds/blob/41beda1d6435760dc99e38bd7e65f36798aad212/research/p104-lowerbound-toolkit/lean/Nov15/LinP104FreeInstBase.lean)
* [#7852 README, including the DRAT scope](https://github.com/CrocSwap/integer-mult-bounds/blob/41beda1d6435760dc99e38bd7e65f36798aad212/research/p104-lowerbound-toolkit/README.md)

Upstream package and source attribution: DreamingOfClouds with Claude Opus 5.5
via Claude Code, as stated on PR #7852. The subset/gauge deduction and the
finite examples in this local note are a separate consequence built on the
upstream rank lemma; no claim of novelty against the wider literature is made.

## Open next questions

Check for large gaugeable subsets in actual paid networks and prove the support transfer.

Clear1nsight prepared this contribution with substantial OpenAI Codex assistance. Credit DreamingOfClouds for the pinned P104 toolkit and its predecessor sources. Copied Apache-2.0 sources retain their notices.
