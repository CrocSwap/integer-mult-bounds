# Independent review of the proposed Gaussian-rational C-word extension

Review scope: the supplied copies of #7834's finite-word validator,
recursive dispatcher and BUTTERFLIES proof, together with #7828's
APPLICATION.md. Exact read-input hashes are in READ-INPUTS.json.
The proposed root extension was not read or imported. This is an
independent mathematical derivation and logical arithmetic check, not
a review of final root code or a fixed-tape implementation.

## Verdict

The odd lift is sufficient under these explicit conditions:

- One fixed finite word has base dimension \(N\ge2\), \(J\) instructions,
  fixed Gaussian-rational scalars and the exact all-column productive
  endpoint \(C^{\otimes Nf}\) on each productive owner.
- A scalar acts once on a full row. A column phase remains \(i^f\);
  it is not replaced by scalar \(i\).
- A completed smaller paid call returns the exact dyadic C transform
  relative to its input. Descendants carry the original root lift,
  without applying another root odd lift.
- Binary height and magnitude guards include actual scalar numerator
  sizes and binary denominator valuations.
- The full odd scale is retired only on completed productive outputs.
  Private banks keep their original complete erasure costs.

Let \(D\) be the least common multiple of all odd denominator parts and
\(d=\lfloor\log_Nh\rfloor\), interpreted as zero for \(h<N\).
Then \(D^{Jd}\) clears every intermediate odd denominator. It adds
\(Jd\lceil\log_2D\rceil=O_{\rm word}(\log h)\) magnitude bits.

No extra paid C call is needed. Root lift and retirement add
\(O_{\rm word}(V\log(2+h))\) bit time and linear backing, where \(V\)
is the complete field's bit volume in the widened \(O(p)\)-bit format.
The existing positive-power layer tariff absorbs this with its
polylogarithmic factor. This retains the original movement/XOR provider
and the admitted finite-word existence premise.

## 1. Odd-denominator induction

Write each scalar as \(q=(a+bi)/c\), \(c>0\), and
\(c=2^u c_{\rm odd}\). For every odd prime \(\ell\), let
\(g_\ell=\max v_\ell(c_{\rm odd})\) over the fixed scalar catalogue.
Then \(D=\prod_\ell\ell^{g_\ell}\).

Every current component is a linear combination of the original root
components. ADD, SUB, copy and clear cannot increase the maximum odd
pole order of their arguments. Scalar multiplication increases it by
at most \(g_\ell\). An affine contact \(x\leftarrow x+qy\) does the same:
its common denominator uses the maximum input pole order, not their sum.
Aliased doubling and zero scalars are included.

Native monomial/phase actions are integral. A completed paid C call
is dyadic, so it adds **zero odd pole order relative to its entry**,
even if its internal arithmetic used rationals. Individual C tails
have the same property.

A data dependency crosses at most \(d\) unfinished nonleaf contexts,
with at most \(J\) scalar instructions per context. Completed siblings
can be replaced, for this arithmetic argument, by their exact dyadic
endpoints. Every root-relative coefficient therefore has odd
\(\ell\)-pole order at most \(Jd g_\ell\). The root factor \(D^{Jd}\)
clears all these poles simultaneously.

This is strong induction on child width: the induction hypothesis
establishes both the child's internal grid and its exact return.
It does not assume that intermediate child states have no odd debt.
Correlated owned rows and arbitrary productive values are covered
because the claim is linear in all root inputs.

The row-stock recursion has exactly the required number of nonleaf
levels: repeated integer division by \(N\) reaches a width below \(N\)
after \(d\) active word contexts. No scalar-word context is entered
below that width; the remaining C axes are literal.

## 2. The binary and magnitude guards must change

The original guard depends on \(J,N,h\), so it cannot fund an arbitrary
new scalar height. A valid endpoint may multiply by \(2^M\), perform
exact C work and divide by \(2^M\), for any fixed \(M\). The internal
height and magnitude depend on \(M\).

One sufficient parameter is
\[
\beta\ge1,\quad
\beta\ge\max_qv_2(c_q),\quad
2^\beta\ge1+|a_q|+|b_q|
\]
for each \(q=(a_q+b_qi)/c_q\). The extra one covers the destination
summand in an affine contact. HALF and ordinary ADD remain covered.

For active widths \(e_0=h,e_{k+1}=\lfloor e_k/N\rfloor\), the completed
tails cost fewer than \((N-1)(d+1)\) height/magnitude bits. At most \(J\)
completed children in each prefix cost
\[
J\sum_{k\ge1}e_k\le Jh/(N-1).
\]
The incomplete scalar prefixes cost at most \(J\beta d\). A constant
allowance covers the numerator immediately before one literal C
division. Thus a safe bound for both dyadic height and maximum real
component log growth is
\[
H_{\rm prefix}\le
(N-1)(d+1)+J\beta d+Jh/(N-1)+2.
\]
The larger
\[
G=8(J\beta+N+1)(h+1)
\]
suffices.

For original signed width \(w\), reserve
\[
w+2G+Jd\lceil\log_2D\rceil+O_{\rm word}(1).
\]
One \(G\) pays the binary lift and one intermediate growth; the odd
term pays the initial odd lift. Include all scalar numerator temporaries.
Under #7834's \(h=O(p^{.997})\), after the finite word is fixed this is
\(O(p)\). This is sufficient, not optimized.

Form the complete complex numerator before exact division. No real
component may be silently truncated or approximately divided.

## 3. Root retirement and the complete additional bill

With \(E_0=Jd\), the root begins with \(2^GD^{E_0}x\) and finishes at
\[
2^GD^{E_0}C^{\otimes h}x.
\]
The C tensor denominator divides \(2^h\), and \(G\ge h\).
Every completed component is therefore divisible by \(D^{E_0}\).
Execute \(E_0\) exact fixed-\(D\) divisions, then drop \(G-h\) binary
places. The result is the existing numerator convention
\(2^hC^{\otimes h}x\). The two retirements commute mathematically;
the implementation must retain exact-divisibility checks.

Private intermediate banks need not be divisible by the full root
scale: the productive endpoint theorem does not say that. Erase them
under their declared ownership contract, scanning their full widened
backing. Check and remove zero padding as before.

For a \(B\)-bit component and fixed \(D\), binary multiplication and
long division cost \(O_D(B)\) with a fixed number of scan buffers.
A uniform interpreter can store \(D\) as bits and charge the conservative
\(O(B(\log D+1)^2)\) bound, including divisor, remainder and head returns.
For the eventually fixed word, this is \(O_{\rm word}(B)\).

Repeated fixed-\(D\) root passes cost \(O_{\rm word}(VE_0)\) in total.
They are not repeated at every recursive node. Alternating two full
streaming fields keeps backing linear. Loop/exponent descriptors are
polylogarithmic. Each rational scalar still pays its own
\(O_{\rm word}(V_{\rm node})\) scan. The existing geometric stack proof
applies to the widened payload. No new address operation or paid child
appears.

## 4. Effective all-column validation and startup

Formal dictionaries are still
\(\sum_Ac[A]A^{\otimes f}\), now with \(c[A]\in\mathbb Q(i)\).
Rational scalars change coefficients; column gates change the exact
dyadic matrix keys. The finite Vandermonde separation over \(\mathbb C\)
works for these coefficients unchanged. Equality after grouping exact
matrix keys is equivalent to equality for every positive column count.

A phase in a matrix key must stay there: \(iA\) and \(A\) are distinct,
because \((iA)^{\otimes f}=i^fA^{\otimes f}\). Exterior scalar \(i\)
acts only once. The independent mutation check agrees at one column
but fails at two.

For unary-field code length \(L\), dimensions, instruction counts and
scalar numerators/denominators are at most \(L\). After all scalar
instructions, rational coefficient heights are \(O(L\log L)\). Path
counts and dense matrix sizes remain exponential in \(L\). Ordinary
polynomial-time rational arithmetic changes only the polynomial factor.
The conservative \(2^{8L}\operatorname{poly}(L)\) per-code bound and
polynomial-in-\(p\) bounded startup therefore survive.

**Use binary rational checking and a binary divisor interpreter.**
Correction from the final code review: the unary denominator fields share
the total length budget, so \(\sum_i q_i\le L\) and
\(D\le\prod_i q_i\le3^{L/3}\). The initial review treated the loose
individual-field bound \(L^L\) as attainable and incorrectly claimed
that a \(D\)-state table necessarily exceeded the \(2^{O(L)}\) budget.
That obstruction does not follow for this unary code. Binary arithmetic
remains a valid uniform implementation and avoids needing such a table.

The first qualifying code in length/lexicographic order remains the
same at every later search cap. Conditional on one finite qualifying
rational word existing, the dispatched word and all coefficients are
eventually fixed. That supplies the constants above. This review does
not materialize a funded winning word or discharge its existence premise.

## 5. Independent checks

With Python 3.12 and the standard library:

    python3 -I -B -W error check_rational_grid.py
    python3 -I -O -B -W error check_rational_grid.py

RESULT.json and RESULT-OPTIMIZED.json agree. The script imports neither
the source dispatcher nor the root's proposed extension.

Its independently written, deliberately **unfunded** \(N=W=2\) word
uses nonreal scalars, denominators 3, 5 and 7, arbitrary signed inputs,
column phases, row mixing/unmixing, nonzero private paid work and
retirement. Ranks 1, 2, 3, 4, 6 and 8 reach three recursive levels.
The rank-eight case performs 49,920 exact rational divisions, 32,000
C divisions and 155 paid calls on 4,096 scalar components. Results
equal a separate Fraction-based direct C-tensor computation.

Controls reject omission of the odd lift, omission of depth in the odd
reserve, and the unchanged binary guard for an arbitrary new scalar.
Replacing a column phase by scalar \(i\) passes one column and fails
two columns, including exact final retirement. Another 1,024 finite
parameter checks corroborate the conservative prefix-height estimate.

Universality follows from Sections 1–4, not the finite checks.
This logical model does not execute tape transitions, prove funded-word
existence, audit the complete Gaussian product or establish a new
\(\kappa\). The five selected assumptions remain outside this review's
collective scope.

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance.
Credit #7834 for the dispatcher, all-column grammar and startup;
#7828 for the rational compiler context; and their credited finite C
word, integer-flow, native-operator and scalar-grid predecessors.

