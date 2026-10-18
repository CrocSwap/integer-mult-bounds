# Prime-source selector transfer

## Scope and result

This package audits the all-size application of the prime-interval estimate in
the pinned assembly source, Section 08, “Prime source lengths.” For the source
parameters

- \(b=\lceil\log_2 n\rceil\),
- \(\epsilon=2^{-75}\),
- \(d=\lfloor b^\epsilon\rfloor\),
- \(p=6b\), and
- a power of two \(T\in[4n/b,8n/b)\), with
  \(r=2^{\lceil\log_2(T)/d\rceil}\),

the proof establishes the stated prime-length selection for every integer
\(b\ge 5^{2^{75}}\). In particular, if each axis length \(t_i\) is either
\(r/2\) or \(r\), one can choose distinct odd primes \(s_i\) with

\[
(1-2\eta)t_i<s_i\le(1-\eta)t_i,\qquad \eta=\frac1{4d}.
\]

The selected lengths satisfy \(T/2<\prod_i s_i<T\), are coprime to their
corresponding powers of two, and have resampling gaps
\(1/8>t_i/s_i-1>1/(4d)\). With the source value
\(\alpha=\lceil(12d^2b)^{1/4}\rceil\), this gives
\(\alpha^4(t_i/s_i-1)>p\). Scanning both intervals and testing candidates by
trial division has a conservative bit-operation upper bound
\(O(d\,r^{3/2}\operatorname{poly}(p))=n^{o(1)}=o(n)\).

The explicit cutoff is sufficient, not a practical crossover estimate. Since
\(\epsilon=2^{-75}\), \(b\ge5^{2^{75}}\) is astronomically large. The proof
does not claim that this is the least possible cutoff.

## Assumptions and claim status

The elementary transfer from the source parameters to the selector conclusion
is proved in [PROOF.md](PROOF.md). The one analytic input is the
Rosser–Schoenfeld estimate

\[
y-\frac{y}{2\log y}<\vartheta(y)<y+\frac{y}{2\log y}
\quad(y>563),\qquad
\vartheta(y)=\sum_{q\le y,\ q\ {\rm prime}}\log q.
\]

Under that cited estimate, this package derives the prime-interval count used
by the assembly source. It does not re-prove Rosser–Schoenfeld’s theorem.
The setup-cost bound assumes ordinary binary trial division and polynomial
bit-cost arithmetic on \(O(p)\)-bit candidates, as stated in the source.

The verifier checks exact source identity, rational constant reductions, and
finite exact geometry controls. It does not numerically search for primes at
the enormous source cutoff, and those finite controls are not evidence for
the all-size theorem. The universal argument is the written proof, conditional
on the stated analytic estimate and the source parameter definitions.

This is a source-level setup result. It does not change the selected
\(\kappa\), establish the full multiplication theorem, or discharge the other
analytic, precision, compiler, hosting, and supplier obligations recorded in
the selected review.

## Source pins

- [Pinned assembly source](https://github.com/CrocSwap/integer-mult-bounds/blob/463113d675af7410ac91d53a4fed51ec6494eb9a/upstream/build/sections/08-assembly.tex),
  Git blob 337810a1d9a58a2ecf14123420923c039ba322a6.
- [Repository audit](../../docs/audit.md), especially its external analytic
  interfaces section.
- Harvey and van der Hoeven, [Integer multiplication in time \(O(n\log n)\)](https://annals.math.princeton.edu/2021/193-2/p04),
  Lemma 5.1 and its proof.
- Rosser and Schoenfeld, [Approximate formulas for some functions of prime numbers](https://doi.org/10.1215/ijm/1255631807),
  Illinois Journal of Mathematics 6 (1962), Theorem 4, p. 70.

## Reproduce

From the repository root:

~~~sh
python3 scripts/research_package.py --package research/prime-source-selector-transfer --check-only
python3.12 scripts/research_package.py --package research/prime-source-selector-transfer
~~~

The registered replay uses only the Python standard library. The package pins
the catalogue task and selected record for provenance and the assembly source
as a live input.

## Open next questions

1. Can the imported Rosser–Schoenfeld estimate be independently formalized in
   the repository's trusted proof stack? This would remove the only analytic
   premise left in this selector result. A first step is to encode Theorem 4's
   two \(\vartheta\)-inequalities and then derive the interval count as in
   [PROOF.md](PROOF.md). The prime-number estimate itself is outside this
   package.
2. Can the \(O(d\,r^{3/2}\operatorname{poly}(p))\) scan be refined to an
   explicit machine-and-tape program under the selected compiler's exact cost
   rules? The first step is to account for candidate generation, trial
   divisors, and the \(d\)-prime output list on the named tapes.

## Credit

Prepared by Cinna Davis with OpenAI Codex assistance. The derivation and
verification scope are disclosed in [TASK.json](TASK.json).
