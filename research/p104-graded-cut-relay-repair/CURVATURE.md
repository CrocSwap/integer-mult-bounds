# Discrete curvature of a paid rank histogram

Let \(0<t\le1\) and let \(n_r\ge0\) be a finite histogram of positive
integer ranks, all at most \(R\). Put \(f(0)=0\), \(f(r)=r^t\),
\(G=\sum_r r n_r\), and

\[
 H_j=\sum_r n_r(r-j)_+,\qquad
 w_j=2j^t-(j-1)^t-(j+1)^t \quad(1\le j<R).
\]

Concavity gives \(w_j\ge0\), and the exact identity is

\[
 \sum_r n_r r^t=G-\sum_{j=1}^{R-1}w_j H_j.
\]

Indeed, telescoping the second differences gives
\(\sum_{j=1}^{r-1}(r-j)w_j=r f(1)-f(r)=r-r^t\). Multiply by \(n_r\)
and sum. The identity holds for any nonnegative real histogram and has no
causal or geometric hypothesis. At \(t=1\), every \(w_j\) vanishes.

## Native word versus the interval relaxation

Apply the identity with \(R=8\) to the native upward MOVE histogram and the
optimal interval-cover histogram of [GRADE-PRICE.md](GRADE-PRICE.md). Both
have \(G=4750\). For \(j=1,\dots,7\), relaxed minus native \(H_j\) is

```
2149, 2967, 2539, 2067, 1554, 1020, 505.
```

At \(t=1-0.00389046\), the first two nonnegative terms
\(w_j(H_j^{relaxed}-H_j^{native})\) lie respectively in
`[11.574637158869318381, 11.574637158869318383]` and
`[6.001777803622792374, 6.001777803622792379]`. The seven terms sum to
`[25.059996283598193259, 25.059996283598193307]` per native invocation.
These are a decomposition of the relaxation gap, not savings realized by a
word. Downward payments and the complete caller remain outside that comparison.

## The best bounded-rank two-contact fusion

Replace charges \(a^t+b^t\) by \((a+b)^t\), where \(a,b\) are positive
integers and \(a+b\le8\). For fixed \(s=a+b\), concavity gives
\(a^t+b^t\le 2(s/2)^t\). Its upper bound on the gain is
\(s^t(2^{1-t}-1)\), which is nondecreasing in \(s\). Therefore the exact
maximum is at \((a,b)=(4,4)\), with saving \(2\,4^t-8^t\). For
\(0<t<1\) it is the unique maximizing ordered rank pair. At the target it is
in `[0.021428347033463130, 0.021428347033463131]`.

The verifier independently rebuilds the complete 36-call binary target and
paid histograms from the pinned #8027 graph and the pinned paired caller. At
the target, its baseline raw surplus lies in
`[-0.132405116496822352, -0.132405116496822052]`, enclosing the tighter #8041
receipt. Six **arbitrary rank-sum-at-most-eight** fusions, even at this best
price, cannot make that raw surplus positive. Seven hypothetical 4+4 fusions
would produce a raw surplus in
`[0.017593312737419560, 0.017593312737419860]`, if the rest of that invoice
were unchanged. These tests do not cover a fusion of total rank above eight,
or prove the stronger powered outer test, a realizable fusion, or a new κ.

As an incidence filter, among the original upward MOVEs there is exactly one
ordered 4+4 pair with the first destination chart equal to the second source
chart: clocks 7112 and 7210, chart path 0 → 509 → 1, owners 2241 and 2252.
The corresponding ordered 2+2 count is 4,227. These counts only assert clock
order and chart identity. The owners need not match, and no payload, source
history, nested projector, displaced reader or paid construction is assumed.

## Reproduce and corruption controls

From this directory, run

```
python3.12 -I -B curvature.py pinned/strong-bit.json.gz pinned/EFREE-CALLER.json.gz
```

The exact dyadic-root code in `grade_price.py` encloses all powers with
outward rational bounds. The replay authenticates the two source files,
reconstructs the full target and paid histograms, verifies the telescoping
identity for each unit rank through the complete paid histogram's rank 56,
checks the seven gap terms, exhausts all ordered rank pairs with sum at most
eight, and enumerates source chart incidences. The registered wrapper also
changes a native histogram while preserving its count and total rank, and
changes a source contact in memory; both altered-data checks must be rejected.
The unmodified expected result is [CURVATURE.json](CURVATURE.json).
