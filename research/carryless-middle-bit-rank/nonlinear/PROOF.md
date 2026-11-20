# Decoder degree and carryless width for an integer product bit

For unsigned \(m\)-bit integers with \(m\ge 3\), consider bit \(m-1\) of their ordinary product. Even when the inputs are restricted to odd integers, its \(\mathbb F_2\) matrix rank is \(2^{m-3}+1\). A degree-\(d\) decoder of separately encoded binary polynomial products needs exponentially many input coordinates at any fixed \(d\). At \(m=5\), a quadratic decoder achieves the minimum possible width of four coordinates on each side. It takes 3 decoder AND gates and 18 AND gates across the encoder, channel and decoder.

## Model and rank bound

For each channel \(j\) the left and right parties produce binary polynomials with fixed widths \(a_j,b_j\ge1\). Each coefficient can be an arbitrary Boolean function of its own operand. All positions count toward the width, including constants and unused positions. The receiver gets only the \(a_j+b_j-1\) coefficients of each product in \(\mathbb F_2[z]\). Let \(W_L=\sum_j a_j\) and \(W_R=\sum_j b_j\). The scalar decoder has Boolean algebraic normal form of degree at most \(d\) in the received bits.

Write \(F_{x,y}\) for the decoded bit matrix and \(J\) for the all-ones matrix. Let \(\alpha\) be the constant term of the decoder. Each product coefficient expands into terms consisting of one left and one right feature from its channel. A positive-degree decoder monomial of degree \(k\) therefore expands into products of left and right encoded features that use at most \(k\) coordinates on each side. Repeated coordinates collapse in the Boolean algebra. The sets of channels represented on the left and right coincide, since each selected output coefficient contributes a factor from its own channel on both sides.

For a nonempty set \(S\) of channels, let \(K_d(S;a)\) count subsets of at most \(d\) distinct left coordinates with channel support exactly \(S\). Equivalently,
\[
K_d(S;a)=\sum_{\substack{k_j\ge1\ (j\in S)\\\sum_{j\in S}k_j\le d}}
         \prod_{j\in S}\binom{a_j}{k_j}.
\]
Use the analogous definition for the right widths. Factoring \(F+\alpha J\) through the two families of feature evaluations gives an intermediate coefficient matrix with zero entries between different channel supports. The rank of each block is at most the minimum of its two dimensions. Thus
\[
\operatorname{rank}(F+\alpha J)\ \le\
  \sum_{\varnothing\ne S,\ |S|\le d}\min\{K_d(S;a),K_d(S;b)\}
\ \le\
  \min_{w\in\{W_L,W_R\}}\sum_{i=1}^{\min\{d,w\}}\binom{w}{i}.
\]
A further zero block occurs between subsets whose per-channel sizes satisfy \(\sum_{j\in S}\max(k_j^{(L)},k_j^{(R)})>d\). The weaker bound applies without knowing the channel partition. It includes the empty subset if the decoder constant is kept.

A circuit over two-input AND, XOR and constants with \(g\) AND gates always has Boolean degree at most \(g+1\). Cut the first AND by replacing its output by a new variable. Induction on the remaining \(g-1\) AND gates bounds the resulting polynomial's degree by \(g\). Substitution increases degree by at most one because a multilinear monomial contains the new variable at most once. Multiplicative depth \(h\) also bounds degree by \(2^h\), by tracking degree along each gate. Consequently the same width inequalities apply with \(d\) replaced by \(g+1\) or \(2^h\), even if preprocessing is unrestricted. The bounds charge only AND gates in these implications. The finite control below counts XOR gates too.

## Application to bit \(m-1\)

Let \(H=2^{m-3}\) and \(L=2H\). Induction by squaring gives \(5^{2^h}\equiv1+2^{h+2}\pmod{2^{h+3}}\) for \(h\ge0\). Therefore \(5\) has order \(L\) modulo \(2^m\), and every odd residue has a unique representation \((-1)^s5^t\) with \(s\in\{0,1\}\) and \(0\le t<L\). For \(f(t)=\operatorname{bit}_{m-1}(5^t\bmod 2^m)\),
\[
f(t+H)=f(t)+1
\]
in \(\mathbb F_2\), since \(5^H\equiv1+2^{m-1}\pmod{2^m}\) and multiplication by \(1+2^{m-1}\) flips the high bit of an odd residue. Negation of an odd residue also flips that bit. Hence the odd-by-odd matrix is obtained from the \(L\times L\) matrix \(f(u+v)\) by repeating rows and columns, using the combined class \(u=t+sH\bmod L\).

Write \(Q(z)=\sum_{t<H}f(t)z^t\) and \(P(z)=\sum_{t<L}f(t)z^t\). The preceding relation gives
\[
P(z)=(1+z^H)Q(z)+z^H(1+z+\cdots+z^{H-1})
    =(1+z)^{H-1}\big[(1+z)Q(z)+z^H\big].
\]
The bracket evaluates to \(1\) at \(z=1\). Up to permuting columns, the matrix \(f(u+v)\) is multiplication by \(P\) modulo \(z^L-1=(1+z)^L\). Multiplication by the bracket is invertible there. Multiplication by \((1+z)^{H-1}\) has rank \(L-H+1=H+1\). Complementing every entry of the odd matrix is a row permutation obtained by negating the left operand, so \(F+\alpha J\) has the same rank for either constant \(\alpha\).

In particular, affine decoding requires \(\sum_j\min(a_j,b_j)\ge H+1\). This threshold for width per side is attainable in the abstract model with \(H+1\) scalar channels by any rank factorization, allowing arbitrary operand-local functions. Degree-\(d\) decoding requires
\[
\sum_{i=1}^{\min\{d,w\}}\binom wi\ge 2^{m-3}+1
\]
for each side width \(w\). For \(1\le d\le w\), the sum including the empty subset is at most \((ew/d)^d\), by bounding \((1+d/w)^w\) and dividing by \((d/w)^d\). Thus \(w\ge(d/e)(2^{m-3}+1)^{1/d}\) for fixed \(d\) in this range. Polynomial width requires decoder degree \(\Omega(m/\log m)\) and linear width requires \(\Omega(m)\). For the latter, if \(w\le c m\) and \(d=o(m)\), then \(d\log_2(e w/d)=o(m)\). These necessary conditions also hold for a decoder of the full product by projecting onto the same bit and restricting the operands to odd values.

An unrestricted decoder still needs at least \(m-1\) coordinates on each side in this model. The \(L\)-periodic \(f\) has no smaller cyclic period, since every proper divisor of \(L\) divides \(H\) and \(f(t+H)\ne f(t)\). The target consequently has \(L\) distinct rows and columns, all nonconstant. Each side needs \(L\) distinct encoded vectors. A side with exactly \(m-2\) coordinates would have to use its all-zero vector, which makes all channel products zero on a row or column. Fewer coordinates give too few vectors.

## Full-domain gate bound with charged preprocessing

Let \(s_L,s_R\) be the numbers of AND gates used in the local encoders, and \(g\) the decoder AND count. On fixing the right operand, every received bit becomes an XOR of left encoded coefficients, since the right coefficients are now constants. The restricted composition can therefore be implemented with at most \(s_L+g\) AND gates, independently of the channel implementation. Fix \(y=2^m-1\). Bit \(m-1\) of \(xy\) becomes \(x_{m-1}\) XOR the OR of the lower \(m-1\) bits of \(x\). This has degree \(m-1\) on the full unsigned left domain. Thus \(s_L+g\ge m-2\) and, by symmetry, \(s_R+g\ge m-2\). For bit \(m\) of the full product, the restricted formula is \((1+x_0)+\prod_{i=0}^{m-1}(1+x_i)\), since for positive \(x\) the high part of \(x(2^m-1)\) is \(x-1\). For \(m\ge2\) this has degree \(m\), strengthening the full-product requirements to \(s_L+g,s_R+g\ge m-1\). With affine encoders, the latter requires at least \(m-1\) decoder AND gates.

## Width-optimal finite escape

Take odd five-bit inputs, so \(m=5\) and the odd matrix has rank five. For combined classes \(u=0,\ldots,7\), emit the following four-bit polynomial coefficient masks, low bit first.

| \(u\) | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Mask as an integer | 1 | 3 | 5 | 15 | 7 | 9 | 11 | 13 |

Each side implements this table directly from the four unrestricted input bits \(x_1,\ldots,x_4\) with
\[
p=x_2+x_3,\qquad a=p+x_4,\qquad
b=x_1+x_4+x_1a+x_2(x_3+x_4),\qquad
c=x_1+x_3+x_4p .
\]
Its polynomial is \(1+az+bz^2+cz^3\). The witness checks agreement with the table for every odd operand. With \(z_i\) the coefficient of degree \(i\) in the carryless product, the decoder evaluates in \(\mathbb F_2\)
\[
r=z_1+z_5,\qquad s=z_4+z_6,\qquad t=z_2+z_3,\qquad
b_4=t+s+z_5+z_3(r+s)+z_4z_5+z_6(r+z_2).
\]
An exhaustive comparison against ordinary multiplication checks all \(16^2\) input pairs. There are only 30 distinct channel returns, including a collision between the two unordered pairs \((1,25)\) and \((5,5)\) from different combined classes. The decoder receives seven channel coefficients and takes no original operand bits. The width and degree lower bounds above prove optimality of width four on each side among all decoders and degree two at this width.

| Stage per product bit | AND gates | XOR gates |
| --- | ---: | ---: |
| Left encoder | 3 | 8 |
| Right encoder | 3 | 8 |
| One carryless convolution | 9 | 9 |
| Nonlinear decoder | 3 | 10 |
| Total | 18 | 35 |

The convolution is realized by the ordinary coefficient equations with both constant terms fixed at 1. This leaves nine pairwise AND gates and nine XOR gates to sum their terms together with the constant and routed bits. Gate counts use hardwired constants and static wiring, with fan-out free, separately from the charge of all eight explicit polynomial input positions.

The checker also establishes the three-AND decoder minimum for this **fixed encoding**. Over the reachable channel values it represents each Boolean function by its truth vector and reduces modulo affine functions of the six nonconstant received bits. Up to affine terms, the first AND \(G\) is a product of two homogeneous linear forms. A second parallel AND adds another such product. A second serial AND can be written as \(\ell(M+G)\) for linear forms \(\ell,M\), up to affine terms and an optional additional \(G\). Indeed, a gate \((C+G)(D+G)\) equals \((C+D+1)(C+G)\) using Boolean idempotence, and constant parts of either factor only add affine terms or \(G\). Replacing a representative of \(G\) by another differing by an affine function just changes \(M\) and the affine output. The checker enumerates all linear forms and quotient classes for both second-gate possibilities. The ten-XOR schedule is due to the separate reviewer.

## Reproduction and scope

Run from this directory with Python 3.9+ and the standard library.

```sh
ulimit -t 220
ulimit -v 1572864
python3 -I -W error -B verify.py
```

The 220 CPU-second and 1.5 GiB address-space limits, measured execution time and maximum RSS are recorded in `RESULT.json`. The gate witness covers one actual output bit on odd five-bit inputs. The all-size lower bound applies to that output of a dense product as well. The finite construction has no P104 schedule, tape realization or signed-price reduction. The exact #7830 supplier and selected main serve as comparators, with no code or edit inherited in the witness.

The overlap check inspected the #7830 supplier, the earlier #493 bit supplier, #3787 exact FFT and carry recovery, #6252 unsigned carry envelopes, and #690/#693 signed packing audits. The separate carryless keyword search surfaced an extension-field backend rather than this odd-product-bit channel. [Comparator #7830](https://github.com/CrocSwap/integer-mult-bounds/pull/7830) · [#493](https://github.com/CrocSwap/integer-mult-bounds/pull/493) · [#3787](https://github.com/CrocSwap/integer-mult-bounds/pull/3787) · [#6252](https://github.com/CrocSwap/integer-mult-bounds/pull/6252) · [#690](https://github.com/CrocSwap/integer-mult-bounds/pull/690) · [#693](https://github.com/CrocSwap/integer-mult-bounds/pull/693)
