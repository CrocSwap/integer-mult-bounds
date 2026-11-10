# A smaller effective interval onset

This scoped proof is produced by Nick Petalas. It uses alephnan's
[PR #6713](https://github.com/CrocSwap/integer-mult-bounds/pull/6713),
`LOCAL_LIMIT.md` at `cd666f05c4e9006025b634687cc493911c8371c8`,
as a mathematical premise. No predecessor verifier or convolution is replayed.

## Premise and conclusion

Use the notation of that source. The centered sum is `Z_n`, the centered
Gaussian `G_n` has variance `nv`, and `c_sigma = sqrt(2*pi*v)`.
For every integer `n >= 1296`, every real `x`, and every interval `I` with
endpoints `x,x+b`, the source proves

\[
\begin{aligned}
 \sqrt n\,|\Pr(Z_n\in I)-\Pr(G_n\in I)|&\le A_n+bB_n,\\
 \left|\sqrt n\,\Pr(Z_n\in I)
       -\frac{b e^{-x^2/(2nv)}}{c_\sigma}\right|
   &\le A_n+bB_n+\frac{b^2}{4\sqrt n},
\end{aligned}
\]

where

\[
 B_n=3/\sqrt n+\sqrt n\log n\,e^{-\sqrt n/320},
 \qquad A_n=(1+4B_n)/\log n.
\]

These are its equations (1) and (2). They include every endpoint convention,
singletons when `b=0`, and the empty interval. Their six hypotheses H,
including `2 <= v <= 3`, and their classical analytic dependencies remain
premises here. In particular `c_sigma < 5` follows from `v <= 3, pi < 4`.

**New conclusion.** Put `K = 751000000`. For every integer `n >= 2^K`,
every real `x`, and `0 <= b <= 5000`, both

\[
 c_\sigma\sqrt n\,|\Pr(Z_n\in I)-\Pr(G_n\in I)| <10^{-8}
\]

and

\[
 \left|c_\sigma\sqrt n\,\Pr(Z_n\in I)
       -b e^{-x^2/(2nv)}\right|<10^{-8}
\]

hold with the same endpoint conventions. The source used `n >= 2^(10^12)`
for these guarantees. Only this local onset is improved. The proof below
also yields the sharper intermediate remainder coefficient `1025/1024`
in place of the source's simplification to `2`.

## Uniform remainder bound

Write `w = log n`, and first suppose `w >= 60`. The larger source bound is

\[
 E(n,b)=\frac1w+
 (b+4/w)\left(3e^{-w/2}+w e^{w/2}e^{-e^{w/2}/320}\right)
 +\frac{b^2}4e^{-w/2}.
\]

For `0 <= b <= 5000`, we have `b+4/w < 5001` and

\[
 3\cdot5001+5000^2/4=6265003<2^{23}.
\]

Consequently

\[
 E(n,b)<\frac1w+2^{23}e^{-w/2}
              +5001w e^{w/2}e^{-e^{w/2}/320}.                 \tag{A}
\]

Multiply the two remainder terms by `w`. The first,
`R_1(w)=2^23 w e^(-w/2)`, decreases on `[60,infinity)` because its
logarithmic derivative is `1/w-1/2 < 0`.
The positive Taylor terms through degree four give

\[
 e^3>1+3+9/2+27/6+81/24=131/8>16,
\]

so `e^30 > 2^40`. Therefore

\[
 R_1(w)\le R_1(60)<60/2^{17}<1/2048.                         \tag{B}
\]

The second is `R_2(w)=5001w^2 e^(w/2) exp(-e^(w/2)/320)`.
Its logarithmic derivative is

\[
 2/w+1/2-e^{w/2}/640
 \le 2/60+1/2-2^{40}/640<0.
\]

Thus `R_2` also decreases. The function `u exp(-u/320)` decreases for
`u>320`. Since `e^30>2^40>320`,

\[
 \begin{aligned}
 R_2(w)&\le R_2(60)
 <5001\cdot60^2\cdot2^{40} e^{-2^{40}/320}\\
 &<2^{65}e^{-2^{31}}
 <2^{65-2^{31}}<1/2048.                                    \tag{C}
 \end{aligned}
\]

Here `5001*60^2 < 2^25`, `2^40/320 > 2^31`, and `e>2`
justify the successive strict inequalities. All of these are small exact
integer or rational comparisons. Combining (A), (B), and (C) proves

\[
 \boxed{E(n,b)<\frac{1025}{1024\log n}}
 \quad(w\ge60,\ 0\le b\le5000).                            \tag{D}
\]

The smaller Gaussian-integral error obeys the same bound. No atomic-mass
estimate or change of endpoint convention is introduced.

## The new onset

The positive series
`log 2 = 2 sum_(j>=0) (1/3)^(2j+1)/(2j+1)` gives `log 2 > 2/3`.
For `n >= 2^K`, therefore, `w > 2K/3 > 60` and `n > 1296`.
Multiplying (D) by `c_sigma < 5` yields

\[
 c_\sigma E(n,b)
 <\frac{5\cdot1025}{1024w}
 <\frac{15375}{2048K}
 <\frac1{10^8},
\]

because, exactly,

\[
 2048\cdot751000000-15375\cdot10^8=548000000>0.
\]

This proves both stated conclusions. The old and new onset exponents obey
`10^12 > 1331*K`; this compares exponents of symbolic integers, not runtime
or measured practical performance. No power with either enormous exponent
is constructed.

## Scope and credit

Alephnan retains credit for the effective interval inequalities, their
Fourier argument and application to the complete historical flow. CubeJerry
retains the fixed-height exponent result in PR #6329. The raw-p7 law and
analytic lineage retain the credit recorded there, including zxv,
Ryanson Jonathan / pinterbanget, DLamdata, Cinna Davis / 1337isnot1337,
Jacob Alan Sussman, and Nick Petalas's earlier leaf results. Beurling,
Selberg, Vaaler and Shou retain the classical approximation credit.

The new contribution is the strict rational remainder budget and its smaller
sufficient local onset. The original hypotheses and interval inequalities
are cited, not independently proved or certified here. This written proof
has not been checked by a proof kernel. It does not substitute the new onset
into the full mixed-layer flow proof, improve its exponent, price a physical
implementation, or discharge any selected framework assumption.
