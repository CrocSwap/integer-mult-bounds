# Count backing at native extent preparation

This is a written source proof, supported by finite execution. The source is
Jose Manuel/jmbarrancoml's PR2697 at
`a53fdf4bcbe33c6732f0bec1badc8c023380f9d1`, retained in the declared
`selected-layout-numerical-lifetime/vendor` exports. SOURCES.json binds their
exact bytes, Git blobs and base commit.

## Metric and boundary

A tape's backing is `len(Tape.cells)`, including LEFT, delimiters and erased
cells. Sum distinct strongly reachable tapes once. Clearing writes BLANK but
does not shrink an array. Charge closed tapes until their last reference
disappears. Assume ordinary sequential successful execution, fixed source
methods, and no capturing observers or retained execution frames.

Inputs are positive counts with canonical significant digits. Borrowed inputs
may retain blank tails; their entire backing belongs to entry baseline K.
Numerical Words, payload, records, interpreter objects and unreachable arrays
awaiting host reclamation are separate metrics. Dropping a reference does not
prove a physical tape reuse rule.

## Exact product peak

For positive a,b, write A=bit_length(a), B=bit_length(b), C=bit_length(ab),
and t=v_2(b). The exact private peak of `Count.product(left,right)` is

```text
P(a,b) = A+B+C+6 + max(0,A+2-t).
```

Borrowed operands are excluded and may alias. Source copies are fresh.
The source retains factor, scan and result while scanning b from its most
significant bit. After prefix p, result is a*p. Doubling and addition increase
its value monotonically, and never allocate beyond its final RIGHT cell.
Initial zero has one digit and obeys the same bound.

The final three-tape cut contributes A+B+C+6. Each set bit also invokes
`Count.add(factor)`, whose private clone has A+2 cells. The last such ADD
occurs at the least significant set bit, when result becomes a*(b>>t), of
width C-t. Its exact four-tape cut is 2A+B+C-t+8. Earlier ADD widths are no
larger; later bits only double result. Taking their maximum gives P.

The raw literal-zero tape and returned Count coexist during startup, giving
A+B+10 including factor and scan. Since C-t>=A>=1, the last-ADD cut dominates
startup. Partial initialization does not exceed completed cuts. Clearing
factor, scan or ADD's clone neither grows nor releases its backing; these
cuts already charge them until their frames exit.

The formula is asymmetric: P(1,32)=19 and P(32,1)=27. At (1,1), peak 12
refutes the three-tape-only budget 9.

## Complete Layout.extents preparation

Fix M=q^w>1, bank width n>=1 and positive before, gap, suffix counts. Let a
and z be the first and last physical positions after `physical()`. Require
0<=a<=z<2n, strictly a<z in binary calls. Every numerical exponent Word has
exactly I encoded binary digits, including padding. Returned extent values are

```text
pre  = before*M^a*(gap if a>=n else 1)
tail = suffix*M^(2n-z-1)*(gap if z<n else 1)
mid  = M^(z-a-1)*(gap if a<n<=z else 1), binary only.
```

Return order is pre,mid,tail or pre,tail. Let r=3 or 2, L_i=bit_length(e_i),
W=max L_i, S=sum(L_i+2). Private count backing, including the exponent Counter
and excluding numerical Words, is at most

```text
S + max(I+2,3W+9).
```

Exact private backing after return is `sum(L_i+3)`, only the r marginal
extents. Add K for entry residents, whose contents and backing do not grow.

The original extent values increase monotonically toward their finals, so
their tapes occupy at most S. One exponent Counter copies an I-digit Word,
occupying at most I+2 cells. Erasing its padding does not shrink backing.
Only one exists at a time; radix_power's other temporaries are numerical.
The middle literal's three-cell raw temporary is covered by 3W+9.

Exactly one gap product executes. The conditions a>=n, z<n and a<n<=z
partition ordered positions. The crossing branch only exists for binary
calls; unary a=z makes the other two exhaustive. Hence `enlarged` aliases
one current original extent and retains no different earlier product. The
old multiplicand stays charged through close and its replacing assignment.

Keep the old multiplicand among S and add the entire product peak. If its
width is X, gap width G and product width L, that peak is at most
2X+G+L+8. Positive multiplication gives X+G<=L+1 and X<=L. The extra is
therefore at most 3L+9<=3W+9. The exponent Counter has already returned.

Marginalization retains all originals and fresh copies. Each marginal appends
one high zero and has backing L_i+3. The extra sum(L_i+3)<=rW+3r<=3W+9.
Closing originals leaves their backing charged until function exit; the frame
then releases originals and the alias enlarged. Exactly the marginals remain.
This proves both preparation and return bounds.

A coarse Natural/Count-only bound is 7(L+3) binary or 6(L+3) unary, where
L=bit_length(before*gap*suffix*M^(2n)). At most r originals plus four product
helpers coexist; marginalization has at most 2r tapes. This bound excludes
exponent Counter, whose encoded width need not be bounded by returned values.

## A successful padding counterexample

M=3,n=1,before=gap=suffix=1,a=0,z=1 returns three unit marginals, totalling
12 cells. At I=8, preparation peaks at 21; at I=256, it peaks at 267. The
source copies all I exponent digits even for value zero. Both executions
succeed with identical returned values and backing. A value-only bound cannot
cover arbitrary index padding; I+2 prices the missed transient. It does not
price the numerical arena storing the input Word.

## Composition boundary

The reached native ADD action retains three marginal extents through both
traversals and closes them in finally. Their exact backing can enter a common
chronological ledger. ADD's internal countdowns remain the separate PR2905
component, including its callback no-capture premise. Numerical, payload,
continuation and record maxima are not silently added here.

The finite ADD fixtures execute the unchanged source action with fixed
coefficients and check a complete integer-address permutation. They establish
neither selected GL64 catalogue membership, complete Consumer.apply reserve,
exception cleanup, nor physical bank placement. There is no new kappa.
