# Exact bounded-grid mixed-precision cancellation

The unrestricted integrality criterion in `mixed-precision-inverse-boundary`
does not decide a bounded reachable domain: a nonintegral coefficient can be
safe on every reachable input. This successor gives an exact scalar-interval
decision, count and least counterexample using logarithmic Euclidean sums.
It does not enumerate a large interval or require a large residue table.

For example, coefficient `1/1000` in coarse-grid units and two extra bits
gives identical rounded increments for every integer `k` in `[-100,100]`.
Extending the interval to 125 introduces its first failure at 125. Ties are
asymmetric: with coefficient `1/8` and two extra bits, -1 is safe and +1 is not.
For denominator `2^100+1`, three extra bits, and all inputs `0..2^200`, the
first failure is `2^96+1`. The complete safe count is in RESULT.json.

## Quantified contract and proof

Use the predecessor rounding `Q_w(t)=2^-w floor(2^w t+1/2)`, signed exact
target updates, rational coefficient A, integers `0<=p<=w<v`, and inputs
`x=k/2^p` with arbitrary integer endpoints `L<=k<=H`. Put
`q=2^(w-p) A=a/d` in lowest terms, `d>0`, and `g=2^(v-w)`.
Arbitrary target dirt is restored by `y+=Q_w(Ax); y-=Q_v(Ax)` exactly
when the two increments agree. There is no target rounding or saturation.

Write `ak=dn+r`, `0<=r<d`, including negative k via Euclidean remainder.
In coarse-grid units, the fine rounded value equals the coarse rounded
integer exactly when

```
2g r < d    or    2g(d-r) <= d.
```

Indeed, below the coarse midpoint the coarse answer is n, and the fine
answer is n iff `floor(g r/d+1/2)=0`. Above the midpoint the coarse answer
is n+1, and the fine answer equals it iff that floor is g. The strict lower
and non-strict upper inequalities follow from the specified tie rule.
Consequently safe residues are `[0,l)` and `[h,d)`, with
`l=floor((d-1)/(2g))+1`, `h=ceil(d(2g-1)/(2g))`.

To count residues below R on an interval, let `N=H-L+1`, `b=aL`, and
`F(N,d,a,b)=sum(i=0..N-1) floor((ai+b)/d)`. Then the exact count is

```
N - F(N,d,a,b+d-R) + F(N,d,a,b).
```

The difference of the two floors is the indicator that the Euclidean
residue is at least R. Sum the two disjoint safe ranges to get the answer.

The implemented Euclidean recurrence first removes integer parts of a,b,
adding `floor(a/d)N(N-1)/2 + floor(b/d)N`. With `0<=a,b<d`, if `aN+b<d`
the residual sum is zero. Otherwise put `N',b'=divmod(aN+b,d)` and replace
`(N,d,a,b)` by `(N',a,d,b')`. This is the same lattice-point count with the
two axes exchanged: each point below `y=(ai+b)/d` is counted once from its
horizontal level. The modulus decreases by Euclidean descent. Thus the
count uses O(log d) Euclidean iterations after normalization, with arbitrary
precision integers. This is an arithmetic-operation bound, not a bit runtime
or multiplication speedup claim. Binary search on whether a prefix contains
any failure returns the least one in O(log(H-L+1) log d) iterations.

## Evidence and reproduction

```
python -I -O -B research/bounded-grid-rounding-count/verify.py
python scripts/research_package.py --package research/bounded-grid-rounding-count
```

The new engine imports no predecessor implementation. Direct Fraction
rounding checks 7,125 signed intervals and 199,500 individual inputs, plus
105 arbitrary-target inverse cases. Direct integer summation checks 26,195
floor sums. A separate complete-period formula checks the huge interval.
The signed tie examples reject symmetric or inclusive-lower shortcuts;
the safe nonintegral example rejects misuse of the unrestricted criterion;
the first-failure case detects a truncated reachable interval. Invalid zero
gap, empty interval and floating coefficient are rejected explicitly.
Normal replay compares the complete deterministic receipt and writes nothing.
`--write` is authoring mode. Source SHA256 checks run directly; the registered
runner also checks exact base Git blobs and catalogue provenance.

No production caller, nonlinear PR628 leaf, physical schedule, selected cold
replay, native compiler or Lean kernel is checked. A matrix box is not silently
reduced to independent scalar intervals: sums of individually safe increments
can cross rounding boundaries. No selected source, precision or kappa changes.

## Open next questions

Bind one caller to a proven reachable interval or arithmetic progression on its
actual input grid. This matters because the predicate only certifies its stated
domain. First supply a source-range invariant and exact precision invoice.
Production reachability and complete compiler admission remain blockers; the
structured question is in TASK.json.

## Sources and credit

Base `0b1cccf86e2f5132ed286a26ef0a681a495740ea`; task draw nonce
`f810a3c6913ef433934b9b593c499bd7`, revision 3. Exact pins are in SOURCES.json.
The predecessor `mixed-precision-inverse-boundary` by woklerx established the
unrestricted grid theorem and actual PR628 counterexample, retaining Chafik
Boukhalfa, Gareth Davidson and Ali Romman's source lineage. This package resolves
only its scalar bounded-interval question. Euclidean floor-sum reciprocity is
standard arithmetic, not claimed as a new algorithm. Prepared by woklerx with
substantial OpenAI Codex assistance. Apache-2.0.
